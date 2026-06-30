import re
import json
from typing import Dict, List, Tuple, Optional
import pandas as pd
import networkx as nx


class DataPreprocessor:
    """
    Data preprocessor for rumor and stance detection datasets.
    Handles data cleaning, formatting, and structure building.
    """
    
    def __init__(self, config):
        self.config = config
        self.max_posts_per_claim = config.data.max_posts_per_claim
        self.max_post_length = config.data.max_post_length
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags (keep the text part)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        if len(text) > self.max_post_length:
            text = text[:self.max_post_length] + "..."
        
        return text
    
    def build_propagation_tree(self, posts: List[Dict]) -> Dict[int, List[int]]:
        """
        Build propagation tree structure from posts.
        
        Args:
            posts: List of post dictionaries with parent-child relationships
            
        Returns:
            Dictionary mapping post indices to neighbor indices
        """
        tree_structure = {}
        graph = nx.Graph()
        
        # Add nodes
        for i in range(len(posts)):
            graph.add_node(i)
        
        # Add edges based on reply relationships
        for i, post in enumerate(posts):
            parent_idx = post.get('parent_idx')
            if parent_idx is not None and parent_idx != -1 and parent_idx < len(posts):
                graph.add_edge(parent_idx, i)
        
        # Convert to adjacency dictionary
        for node in graph.nodes():
            tree_structure[node] = list(graph.neighbors(node))
        
        return tree_structure
    
    def process_twitter_data(self, raw_data: Dict) -> List[Dict]:
        """
        Process Twitter dataset format.
        
        Args:
            raw_data: Raw Twitter data
            
        Returns:
            Processed data in standard format
        """
        processed_data = []
        
        for claim_data in raw_data.get('claims', []):
            # Clean claim text
            claim = self.clean_text(claim_data.get('claim', ''))
            
            # Process posts
            posts = []
            for post_data in claim_data.get('posts', [])[:self.max_posts_per_claim]:
                cleaned_post = {
                    'text': self.clean_text(post_data.get('text', '')),
                    'stance': post_data.get('stance', 'comment'),
                    'parent_idx': post_data.get('parent_idx')
                }
                posts.append(cleaned_post)
            
            # Build tree structure
            tree_structure = self.build_propagation_tree(posts)
            
            processed_item = {
                'claim_id': claim_data.get('claim_id', ''),
                'claim': claim,
                'posts': posts,
                'rumor_label': claim_data.get('rumor_label', 'unverified-rumor'),
                'tree_structure': tree_structure,
                'propagation': claim_data.get('propagation', [])
            }
            
            processed_data.append(processed_item)
        
        return processed_data
    
    def process_weibo_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Process Weibo dataset format from WeiboDataLoader.
        
        Args:
            raw_data: List of training samples from WeiboDataLoader
            
        Returns:
            Processed data in standard format
        """
        processed_data = []
        
        # Group samples by conversation/claim
        claim_groups = {}
        for sample in raw_data:
            claim_text = sample['claim_text']
            conversation_id = sample['metadata']['conversation_id']
            
            if conversation_id not in claim_groups:
                claim_groups[conversation_id] = {
                    'claim_text': claim_text,
                    'posts': [],
                    'rumor_label': sample['rumor_label']
                }
            
            # Add post to the claim group
            post = {
                'text': self.clean_text(sample['post_text']),
                'stance': self._map_stance_to_string(sample['stance_label']),
                'parent_idx': 0,  # All posts reply to root claim
                'metadata': sample['metadata']
            }
            claim_groups[conversation_id]['posts'].append(post)
        
        # Convert grouped data to standard format
        for conversation_id, claim_data in claim_groups.items():
            # Clean claim text
            claim = self.clean_text(claim_data['claim_text'])
            
            # Limit posts per claim
            posts = claim_data['posts'][:self.max_posts_per_claim]
            
            # Build tree structure (simple: all posts connect to root)
            tree_structure = self._build_simple_tree(len(posts))
            
            processed_item = {
                'claim_id': conversation_id,
                'claim': claim,
                'posts': posts,
                'rumor_label': self._map_rumor_label(claim_data['rumor_label']),
                'tree_structure': tree_structure,
                'propagation': []  # Not available in Weibo format
            }
            
            processed_data.append(processed_item)
        
        return processed_data
    
    def _map_stance_to_string(self, stance_label: int) -> str:
        """Map numeric stance labels back to strings."""
        stance_mapping = {
            0: 'support',
            1: 'deny', 
            2: 'comment'
        }
        return stance_mapping.get(stance_label, 'comment')
    
    def _map_rumor_label(self, rumor_label: int) -> str:
        """Map numeric rumor labels to strings."""
        return 'unverified-rumor' if rumor_label == 1 else 'non-rumor'
    
    def _build_simple_tree(self, num_posts: int) -> Dict[int, List[int]]:
        """Build a simple tree where all posts connect to root (index 0)."""
        tree_structure = {0: list(range(1, num_posts))}  # Root connects to all posts
        for i in range(1, num_posts):
            tree_structure[i] = [0]  # Each post connects back to root
        return tree_structure
    
    def validate_data(self, data: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Validate processed data and return valid samples with error messages.
        
        Args:
            data: Processed data
            
        Returns:
            Tuple of (valid_data, error_messages)
        """
        valid_data = []
        error_messages = []
        
        for i, item in enumerate(data):
            errors = []
            
            # Check required fields
            if not item.get('claim'):
                errors.append(f"Item {i}: Missing claim")
            
            if not item.get('posts'):
                errors.append(f"Item {i}: No posts")
            
            if not item.get('rumor_label'):
                errors.append(f"Item {i}: Missing rumor label")
            
            # Check post validity
            for j, post in enumerate(item.get('posts', [])):
                if not post.get('text'):
                    errors.append(f"Item {i}, Post {j}: Empty text")
            
            if errors:
                error_messages.extend(errors)
            else:
                valid_data.append(item)
        
        return valid_data, error_messages
    
    def split_data(self, data: List[Dict], 
                   train_ratio: float = 0.7, 
                   val_ratio: float = 0.15) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Split data into train/validation/test sets.
        
        Args:
            data: Processed data
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        import random
        
        # Shuffle data
        shuffled_data = data.copy()
        random.shuffle(shuffled_data)
        
        # Calculate split indices
        total_size = len(shuffled_data)
        train_size = int(total_size * train_ratio)
        val_size = int(total_size * val_ratio)
        
        # Split data
        train_data = shuffled_data[:train_size]
        val_data = shuffled_data[train_size:train_size + val_size]
        test_data = shuffled_data[train_size + val_size:]
        
        return train_data, val_data, test_data
    
    def save_processed_data(self, data: List[Dict], output_path: str):
        """
        Save processed data to JSON file.
        
        Args:
            data: Processed data
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_data_statistics(self, data: List[Dict]) -> Dict:
        """
        Get statistics about the processed data.
        
        Args:
            data: Processed data
            
        Returns:
            Dictionary containing statistics
        """
        stats = {
            'num_claims': len(data),
            'total_posts': sum(len(item['posts']) for item in data),
            'avg_posts_per_claim': 0,
            'rumor_class_distribution': {},
            'stance_class_distribution': {}
        }
        
        if stats['num_claims'] > 0:
            stats['avg_posts_per_claim'] = stats['total_posts'] / stats['num_claims']
        
        # Count class distributions
        for item in data:
            rumor_label = item['rumor_label']
            stats['rumor_class_distribution'][rumor_label] = (
                stats['rumor_class_distribution'].get(rumor_label, 0) + 1
            )
            
            for post in item['posts']:
                stance = post.get('stance', 'comment')
                stats['stance_class_distribution'][stance] = (
                    stats['stance_class_distribution'].get(stance, 0) + 1
                )
        
        return stats
