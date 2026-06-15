import torch
from torch.utils.data import Dataset
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
import networkx as nx
from .llm_explanation_generator import LLMExplanationGenerator, MockLLMExplanationGenerator


class RumorStanceDataset(Dataset):
    """
    Dataset class for rumor and stance detection with propagation structure.
    Supports both training (claim-level labels only) and evaluation (with stance labels).
    """
    
    def __init__(self, data_path: str, config, mode: str = 'train', 
                 use_mock_llm: bool = False):
        """
        Initialize dataset.
        
        Args:
            data_path: Path to the dataset file
            config: Configuration object
            mode: 'train', 'val', or 'test'
            use_mock_llm: Whether to use mock LLM for testing
        """
        self.config = config
        self.mode = mode
        self.max_posts_per_claim = config.data.max_posts_per_claim
        
        # Load data
        self.data = self._load_data(data_path)
        
        # Initialize LLM explanation generator
        if use_mock_llm:
            self.llm_generator = MockLLMExplanationGenerator(config)
        else:
            self.llm_generator = LLMExplanationGenerator(config)
        
        # Class mappings
        self.rumor_classes = ['non-rumor', 'rumor']  # Weibo: 0=non-rumor, 1=rumor
        self.stance_classes = ['support', 'deny', 'question', 'comment']

        self.rumor_to_idx = {cls: idx for idx, cls in enumerate(self.rumor_classes)}
        # also accept integer strings '0'/'1'
        self.rumor_to_idx['0'] = 0
        self.rumor_to_idx['1'] = 1
        self.stance_to_idx = {cls: idx for idx, cls in enumerate(self.stance_classes)}
        # 'root' is the source post (claim) - treat as comment for encoding purposes
        self.stance_to_idx['root'] = 3
        
    def _load_data(self, data_path: str) -> List[Dict]:
        """Load dataset from JSON file."""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter out claims with too many posts
        filtered_data = []
        for item in data:
            if len(item.get('posts', [])) <= self.max_posts_per_claim:
                filtered_data.append(item)
        
        return filtered_data
    
    def _build_tree_structure(self, propagation_data: List[Dict]) -> Dict[int, List[int]]:
        """
        Build undirected tree structure from propagation data.
        
        Args:
            propagation_data: List of parent-child relationships
            
        Returns:
            Dictionary mapping post indices to neighbor indices
        """
        tree_structure = {}
        graph = nx.Graph()
        
        # Add edges from propagation data
        for relation in propagation_data:
            parent_idx = relation.get('parent_idx')
            child_idx = relation.get('child_idx')
            
            if parent_idx is not None and child_idx is not None:
                graph.add_edge(parent_idx, child_idx)
        
        # Convert to adjacency dictionary
        for node in graph.nodes():
            tree_structure[node] = list(graph.neighbors(node))
        
        return tree_structure
    
    def _create_structure_info(self, posts: List[Dict], claim_id: str) -> List[str]:
        """
        Create structural information prefixes for posts.
        
        Args:
            posts: List of post dictionaries
            claim_id: ID of the claim
            
        Returns:
            List of structure info strings
        """
        structure_info = []
        
        for i, post in enumerate(posts):
            parent_idx = post.get('parent_idx')
            
            if parent_idx is None or parent_idx == -1:
                # Direct reply to claim
                structure_info.append(f"t{i+1} replied to c")
            else:
                # Reply to another post
                structure_info.append(f"t{i+1} replied to t{parent_idx+1}")
        
        return structure_info
    
    def _generate_explanations(self, claim: str, posts: List[Dict],
                              structure_info: List[str]) -> List[str]:
        """
        Return explanations for posts.  If a post already has a cached
        'explanation' field (from data prep), use it directly.  Otherwise
        generate via LLM (mock or real).  Never leaks rumor label.
        """
        explanations = []
        for i, post in enumerate(posts):
            # Use pre-generated explanation if available
            if 'explanation' in post and post['explanation']:
                explanations.append(post['explanation'])
                continue

            post_content = post['text']
            stance_label = post.get('stance', 'comment')
            if stance_label == 'root':
                stance_label = 'comment'

            explanation = self.llm_generator.generate_stance_explanation(
                post_content=post_content,
                claim_content=claim,
                stance_type=stance_label,
                rumor_type="unknown",
                structure_info=structure_info[i],
            )
            explanations.append(explanation)
        return explanations
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict:
        """
        Get a single data sample.
        
        Args:
            idx: Sample index
            
        Returns:
            Dictionary containing sample data
        """
        item = self.data[idx]
        
        # Extract basic information
        claim = item['claim']
        posts_data = item['posts']
        rumor_label = item['rumor_label']
        propagation_data = item.get('propagation', [])
        
        # Limit number of posts
        posts_data = posts_data[:self.max_posts_per_claim]
        
        # Extract post texts and stance labels
        posts = [post['text'] for post in posts_data]
        stance_labels = []
        
        if self.mode in ['val', 'test'] and posts_data and 'stance' in posts_data[0]:
            stance_labels = [
                self.stance_to_idx.get(post.get('stance', 'comment'), 3)
                for post in posts_data
            ]
        
        # Build tree structure
        tree_structure = self._build_tree_structure(propagation_data)
        
        # Create structure information
        structure_info = self._create_structure_info(posts_data, item.get('claim_id', 'c'))
        
        # Generate (or load cached) explanations
        explanations = self._generate_explanations(claim, posts_data, structure_info)
        
        # Convert rumor_label to int index
        if isinstance(rumor_label, int):
            rumor_idx = rumor_label
        else:
            rumor_idx = self.rumor_to_idx[str(rumor_label)]

        sample = {
            'claim': claim,
            'posts': posts,
            'explanations': explanations,
            'structure_info': structure_info,
            'tree_structure': tree_structure,
            'rumor_label': rumor_idx,
            'claim_id': item.get('claim_id', f'claim_{idx}'),
        }
        
        # Add stance labels if available
        if stance_labels:
            sample['stance_labels'] = torch.tensor(stance_labels, dtype=torch.long)
        
        return sample


class CollateFunction:
    """
    Custom collate function for batching variable-length sequences.
    """
    
    def __init__(self, config):
        self.config = config
    
    def __call__(self, batch: List[Dict]) -> Dict:
        """
        Collate a batch of samples (FIXED: Support true batching).
        
        Args:
            batch: List of sample dictionaries
            
        Returns:
            Batched data dictionary
        """
        if len(batch) == 1:
            # Single sample - return as is
            return batch[0]
        
        # Multiple samples - create proper batch
        batched_data = {}
        
        # Get all keys from first sample
        keys = batch[0].keys()
        
        for key in keys:
            values = [sample[key] for sample in batch]
            
            if key in ['posts', 'explanations', 'structure_info']:
                # These are lists that should be batched as List[List[str]]
                batched_data[key] = values
            elif key == 'tree_structure':
                # Tree structures should be batched as List[Dict]
                batched_data[key] = values
            elif key == 'claim':
                # Claims can be batched as List[str] or kept as single str if all same
                if len(set(values)) == 1:
                    # All claims are the same, keep as single string
                    batched_data[key] = values[0]
                else:
                    # Different claims, batch as list
                    batched_data[key] = values
            elif key in ['rumor_label', 'claim_id']:
                # Labels and IDs should be batched as lists
                batched_data[key] = values
            elif key == 'stance_labels':
                # Stance labels are already tensors, stack them
                if isinstance(values[0], torch.Tensor):
                    batched_data[key] = values  # Keep as list for now
                else:
                    batched_data[key] = values
            else:
                # Default: keep as list
                batched_data[key] = values
        
        return batched_data


def create_sample_data():
    """Create sample data for testing."""
    sample_data = [
        {
            "claim_id": "claim_1",
            "claim": "Breaking: Major earthquake hits California",
            "rumor_label": "true-rumor",
            "posts": [
                {
                    "text": "I felt the shaking here in LA! This is real!",
                    "stance": "support",
                    "parent_idx": None
                },
                {
                    "text": "Are you sure? I haven't seen any official reports yet.",
                    "stance": "question", 
                    "parent_idx": 0
                },
                {
                    "text": "Just checked USGS, confirmed 6.2 magnitude earthquake.",
                    "stance": "support",
                    "parent_idx": 1
                }
            ],
            "propagation": [
                {"parent_idx": None, "child_idx": 0},
                {"parent_idx": 0, "child_idx": 1},
                {"parent_idx": 1, "child_idx": 2}
            ]
        },
        {
            "claim_id": "claim_2", 
            "claim": "Celebrity X died in car accident",
            "rumor_label": "false-rumor",
            "posts": [
                {
                    "text": "OMG is this true?? I can't believe it!",
                    "stance": "question",
                    "parent_idx": None
                },
                {
                    "text": "This is fake news, Celebrity X just posted on Instagram 10 minutes ago",
                    "stance": "deny",
                    "parent_idx": 0
                },
                {
                    "text": "Yeah, totally fake. People need to stop spreading rumors.",
                    "stance": "deny",
                    "parent_idx": 1
                }
            ],
            "propagation": [
                {"parent_idx": None, "child_idx": 0},
                {"parent_idx": 0, "child_idx": 1},
                {"parent_idx": 1, "child_idx": 2}
            ]
        }
    ]
    
    return sample_data
