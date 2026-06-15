#!/usr/bin/env python3
"""
Training script for LLM-Enhanced Multiple Instance Learning model.
"""

import argparse
import os
import sys
import torch
import random
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config_loader import load_config
from src.training.trainer import create_trainer


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def main():
    parser = argparse.ArgumentParser(description='Train LLM-Enhanced MIL model')
    parser.add_argument('--config', type=str, default='config/default.yaml',
                       help='Path to configuration file')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to checkpoint to resume from')
    
    args = parser.parse_args()
    
    # Set random seed
    set_seed(args.seed)
    
    # Load configuration
    config = load_config(args.config)
    
    # Create trainer
    trainer = create_trainer(config)
    
    # Resume from checkpoint if specified
    if args.resume:
        trainer.load_checkpoint(args.resume)
        print(f"Resumed training from {args.resume}")
    
    # Start training
    print("Starting training...")
    print(f"Configuration: {args.config}")
    print(f"Device: {config.device}")
    print(f"Batch size: {config.training.batch_size}")
    print(f"Learning rate: {config.training.learning_rate}")
    print(f"Phase1 epochs: {config.training.num_epochs_phase1} | Phase2 epochs: {config.training.num_epochs_phase2}")
    
    try:
        trainer.train()
        
        # Evaluate on test set
        print("\nEvaluating on test set...")
        test_metrics = trainer.evaluate()
        
        print("Test Results:")
        for metric, value in test_metrics.items():
            print(f"  {metric}: {value:.4f}")
            
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        
    except Exception as e:
        print(f"\nTraining failed with error: {e}")
        raise
    
    print("Training completed!")


if __name__ == '__main__':
    main()
