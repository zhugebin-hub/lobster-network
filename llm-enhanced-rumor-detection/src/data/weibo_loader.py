import json
import os
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WeiboDataLoader:
    """
    Data loader for Weibo stance detection dataset.
    
    The Weibo dataset consists of JSON files where each file contains
    a conversation thread with posts having stance labels:
    - "root": Original post (rumor claim)
    - "support": Supporting the rumor
    - "deny": Denying the rumor  
    - "comment": Neutral comment
    """
    
    def __init__(self, data_dir: str, label_file: str = None):
        """
        Initialize the Weibo data loader.
        
        Args:
            data_dir: Directory containing Weibo JSON files
            label_file: Path to Weibo.txt file containing true labels
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"Data directory does not exist: {data_dir}")
        
        # Load true labels from Weibo.txt
        self.true_labels = {}
        if label_file:
            self.label_file = Path(label_file)
            self._load_true_labels()
        else:
            # Try to find Weibo.txt in parent directory
            parent_dir = self.data_dir.parent
            weibo_txt = parent_dir / "Weibo.txt"
            if weibo_txt.exists():
                self.label_file = weibo_txt
                self._load_true_labels()
            else:
                logger.warning("No Weibo.txt file found, will use default labels")
    
    def _load_true_labels(self):
        """Load true labels from Weibo.txt file."""
        logger.info(f"Loading true labels from {self.label_file}")
        
        with open(self.label_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse line format: eid:12345 label:0 post_ids...
                parts = line.split('\t')
                if len(parts) >= 2:
                    eid_part = parts[0]  # eid:12345
                    label_part = parts[1]  # label:0
                    
                    if eid_part.startswith('eid:') and label_part.startswith('label:'):
                        eid = eid_part.split(':', 1)[1]
                        label = int(label_part.split(':', 1)[1])
                        self.true_labels[eid] = label
        
        logger.info(f"Loaded {len(self.true_labels)} true labels")
        label_counts = {}
        for label in self.true_labels.values():
            label_counts[label] = label_counts.get(label, 0) + 1
        logger.info(f"Label distribution: {label_counts}")
            
    def load_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Load all conversation threads from JSON files.
        
        Returns:
            List of conversation dictionaries, each containing:
            - conversation_id: Unique identifier for the conversation
            - root_post: The original rumor post
            - replies: List of reply posts with stance labels
        """
        conversations = []
        json_files = list(self.data_dir.glob("*.json"))
        
        logger.info(f"Found {len(json_files)} JSON files in {self.data_dir}")
        
        for json_file in json_files:
            try:
                conversation = self._load_conversation_from_file(json_file)
                if conversation:
                    conversations.append(conversation)
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")
                continue
                
        logger.info(f"Successfully loaded {len(conversations)} conversations")
        return conversations
    
    def _load_conversation_from_file(self, json_file: Path) -> Dict[str, Any]:
        """
        Load a single conversation from a JSON file.
        
        Args:
            json_file: Path to the JSON file
            
        Returns:
            Dictionary containing conversation data
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            
        if not posts:
            return None
            
        # Find the root post
        root_post = None
        replies = []
        
        for post in posts:
            if post.get('stance') == 'root':
                root_post = post
            else:
                replies.append(post)
                
        if not root_post:
            logger.warning(f"No root post found in {json_file}")
            return None
            
        conversation = {
            'conversation_id': json_file.stem,  # Use filename as conversation ID
            'root_post': root_post,
            'replies': replies
        }
        
        return conversation
    
    def extract_training_samples(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract training samples from conversations.
        
        Each sample contains:
        - claim_text: The root post text (rumor claim)
        - post_text: A reply post text
        - stance_label: The stance of the reply towards the claim
        - rumor_label: Binary label (1 for rumor, 0 for non-rumor)
        - metadata: Additional information
        
        Args:
            conversations: List of conversation dictionaries
            
        Returns:
            List of training sample dictionaries
        """
        samples = []
        
        for conv in conversations:
            root_post = conv['root_post']
            claim_text = root_post.get('text', '').strip()
            
            if not claim_text:
                continue
                
            # Get true rumor label from Weibo.txt file
            conversation_id = conv['conversation_id']
            rumor_label = self.true_labels.get(conversation_id, 1)  # Default to 1 if not found
            
            for reply in conv['replies']:
                post_text = reply.get('text', '').strip()
                stance = reply.get('stance', '').lower()
                
                if not post_text or not stance:
                    continue
                    
                # Map stance labels to our format
                stance_label = self._map_stance_label(stance)
                if stance_label is None:
                    continue
                    
                sample = {
                    'claim_text': claim_text,
                    'post_text': post_text,
                    'stance_label': stance_label,
                    'rumor_label': rumor_label,
                    'metadata': {
                        'conversation_id': conv['conversation_id'],
                        'post_id': reply.get('id', ''),
                        'user_id': reply.get('uid', ''),
                        'timestamp': reply.get('t', 0),
                        'reposts_count': reply.get('reposts_count', 0),
                        'comments_count': reply.get('comments_count', 0),
                        'attitudes_count': reply.get('attitudes_count', 0)
                    }
                }
                
                samples.append(sample)
                
        logger.info(f"Extracted {len(samples)} training samples")
        return samples
    
    def _map_stance_label(self, stance: str) -> int:
        """
        Map Weibo stance labels to numeric labels.
        
        Args:
            stance: Original stance label from Weibo data
            
        Returns:
            Numeric stance label or None if invalid
        """
        stance_mapping = {
            'support': 0,  # Supporting the rumor
            'deny': 1,     # Denying the rumor
            'comment': 2   # Neutral comment
        }
        
        return stance_mapping.get(stance.lower())
    
    def get_dataset_statistics(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the dataset.
        
        Args:
            samples: List of training samples
            
        Returns:
            Dictionary containing dataset statistics
        """
        if not samples:
            return {}
            
        stance_counts = {}
        rumor_counts = {}
        total_samples = len(samples)
        
        for sample in samples:
            stance = sample['stance_label']
            rumor = sample['rumor_label']
            
            stance_counts[stance] = stance_counts.get(stance, 0) + 1
            rumor_counts[rumor] = rumor_counts.get(rumor, 0) + 1
            
        # Calculate text length statistics
        claim_lengths = [len(sample['claim_text']) for sample in samples]
        post_lengths = [len(sample['post_text']) for sample in samples]
        
        stats = {
            'total_samples': total_samples,
            'stance_distribution': stance_counts,
            'rumor_distribution': rumor_counts,
            'avg_claim_length': sum(claim_lengths) / len(claim_lengths) if claim_lengths else 0,
            'avg_post_length': sum(post_lengths) / len(post_lengths) if post_lengths else 0,
            'unique_conversations': len(set(sample['metadata']['conversation_id'] for sample in samples))
        }
        
        return stats
    
    def save_processed_data(self, samples: List[Dict[str, Any]], output_file: str):
        """
        Save processed samples to a JSON file.
        
        Args:
            samples: List of training samples
            output_file: Path to output JSON file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved {len(samples)} samples to {output_file}")


def main():
    """
    Example usage of the Weibo data loader.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize data loader
    data_dir = "C:/Users/24469/CascadeProjects/llm-enhanced-rumor-detection/Weibo_stance/Weibo_stance"
    label_file = "C:/Users/24469/CascadeProjects/llm-enhanced-rumor-detection/Weibo_stance/Weibo.txt"
    loader = WeiboDataLoader(data_dir, label_file)
    
    # Load conversations
    conversations = loader.load_all_conversations()
    
    # Extract training samples
    samples = loader.extract_training_samples(conversations)
    
    # Get statistics
    stats = loader.get_dataset_statistics(samples)
    print("Dataset Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save processed data
    output_file = "C:/Users/24469/CascadeProjects/llm-enhanced-rumor-detection/data/weibo_processed.json"
    loader.save_processed_data(samples, output_file)


if __name__ == "__main__":
    main()
