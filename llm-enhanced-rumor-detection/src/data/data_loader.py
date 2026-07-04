import torch
from torch.utils.data import DataLoader
from typing import Dict, Tuple
import json
import os

from .dataset import RumorStanceDataset, CollateFunction, create_sample_data


def create_data_loaders(config, use_mock_llm: bool = True) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create data loaders for training, validation, and testing.
    
    Args:
        config: Configuration object
        use_mock_llm: Whether to use mock LLM for testing
        
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    # Create sample data if files don't exist
    data_dir = os.path.dirname(config.data.train_data)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Create sample data files if they don't exist
    for data_path in [config.data.train_data, config.data.val_data, config.data.test_data]:
        if not os.path.exists(data_path):
            sample_data = create_sample_data()
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    # Create datasets
    train_dataset = RumorStanceDataset(
        config.data.train_data, config, mode='train', use_mock_llm=use_mock_llm
    )
    
    val_dataset = RumorStanceDataset(
        config.data.val_data, config, mode='val', use_mock_llm=use_mock_llm
    )
    
    test_dataset = RumorStanceDataset(
        config.data.test_data, config, mode='test', use_mock_llm=use_mock_llm
    )
    
    # Create collate function
    collate_fn = CollateFunction(config)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.training.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
        collate_fn=collate_fn
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=1,  # 修复：验证时使用batch_size=1确保每个样本独立处理
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
        collate_fn=collate_fn
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=1,  # Process one claim at a time for testing
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
        collate_fn=collate_fn
    )
    
    return train_loader, val_loader, test_loader


def load_twitter_dataset(data_path: str) -> Dict:
    """
    Load Twitter dataset in the expected format.
    
    Args:
        data_path: Path to the Twitter dataset
        
    Returns:
        Loaded dataset dictionary
    """
    # This would be implemented based on the actual Twitter dataset format
    # For now, return sample data
    return {
        'claims': create_sample_data(),
        'metadata': {
            'num_claims': 2,
            'num_posts': 6,
            'rumor_classes': ['non-rumor', 'true-rumor', 'false-rumor', 'unverified-rumor'],
            'stance_classes': ['support', 'deny', 'question', 'comment']
        }
    }


def load_weibo_dataset(data_path: str) -> Dict:
    """
    Load Weibo dataset in the expected format.
    
    Args:
        data_path: Path to the Weibo dataset
        
    Returns:
        Loaded dataset dictionary
    """
    # This would be implemented based on the actual Weibo dataset format
    # For now, return sample data adapted for Chinese
    sample_data = [
        {
            "claim_id": "weibo_claim_1",
            "claim": "某明星在机场被拍到与神秘人士会面",
            "rumor_label": "unverified-rumor",
            "posts": [
                {
                    "text": "这是真的吗？有图有真相！",
                    "stance": "question",
                    "parent_idx": None
                },
                {
                    "text": "我觉得是炒作，最近正好要发新专辑",
                    "stance": "deny",
                    "parent_idx": 0
                }
            ],
            "propagation": [
                {"parent_idx": None, "child_idx": 0},
                {"parent_idx": 0, "child_idx": 1}
            ]
        }
    ]
    
    return {
        'claims': sample_data,
        'metadata': {
            'num_claims': 1,
            'num_posts': 2,
            'language': 'chinese',
            'platform': 'weibo'
        }
    }


class DatasetStatistics:
    """Utility class for computing dataset statistics."""
    
    @staticmethod
    def compute_statistics(dataset: RumorStanceDataset) -> Dict:
        """
        Compute statistics for a dataset.
        
        Args:
            dataset: Dataset to analyze
            
        Returns:
            Dictionary containing statistics
        """
        stats = {
            'num_samples': len(dataset),
            'rumor_class_distribution': {},
            'stance_class_distribution': {},
            'avg_posts_per_claim': 0,
            'max_posts_per_claim': 0,
            'min_posts_per_claim': float('inf')
        }
        
        total_posts = 0
        
        for i in range(len(dataset)):
            sample = dataset[i]
            
            # Rumor class distribution
            rumor_label = sample['rumor_label']
            rumor_class = dataset.rumor_classes[rumor_label]
            stats['rumor_class_distribution'][rumor_class] = (
                stats['rumor_class_distribution'].get(rumor_class, 0) + 1
            )
            
            # Posts statistics
            num_posts = len(sample['posts'])
            total_posts += num_posts
            stats['max_posts_per_claim'] = max(stats['max_posts_per_claim'], num_posts)
            stats['min_posts_per_claim'] = min(stats['min_posts_per_claim'], num_posts)
            
            # Stance class distribution (if available)
            if 'stance_labels' in sample:
                for stance_label in sample['stance_labels']:
                    stance_class = dataset.stance_classes[stance_label.item()]
                    stats['stance_class_distribution'][stance_class] = (
                        stats['stance_class_distribution'].get(stance_class, 0) + 1
                    )
        
        stats['avg_posts_per_claim'] = total_posts / len(dataset)
        
        return stats
