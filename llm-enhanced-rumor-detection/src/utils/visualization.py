import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Optional
import pandas as pd


def plot_training_curves(train_losses: List[float], val_losses: List[float], 
                        save_path: Optional[str] = None):
    """
    Plot training and validation loss curves.
    
    Args:
        train_losses: List of training losses
        val_losses: List of validation losses
        save_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    
    epochs = range(1, len(train_losses) + 1)
    
    plt.plot(epochs, train_losses, 'b-', label='Training Loss', linewidth=2)
    plt.plot(epochs, val_losses, 'r-', label='Validation Loss', linewidth=2)
    
    plt.title('Training and Validation Loss', fontsize=16)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_confusion_matrix(cm: np.ndarray, class_names: List[str], 
                         title: str = 'Confusion Matrix',
                         save_path: Optional[str] = None):
    """
    Plot confusion matrix.
    
    Args:
        cm: Confusion matrix
        class_names: List of class names
        title: Plot title
        save_path: Path to save the plot
    """
    plt.figure(figsize=(8, 6))
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    
    plt.title(title, fontsize=16)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_metrics_comparison(metrics_dict: Dict[str, Dict[str, float]], 
                          save_path: Optional[str] = None):
    """
    Plot comparison of metrics across different models or datasets.
    
    Args:
        metrics_dict: Dictionary of {model_name: {metric_name: value}}
        save_path: Path to save the plot
    """
    df = pd.DataFrame(metrics_dict).T
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1']
    
    for i, metric in enumerate(metrics_to_plot):
        if metric in df.columns:
            df[metric].plot(kind='bar', ax=axes[i], color='skyblue')
            axes[i].set_title(f'{metric.capitalize()}', fontsize=14)
            axes[i].set_ylabel('Score', fontsize=12)
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_attention_weights(attention_weights: np.ndarray, post_texts: List[str],
                          title: str = 'Attention Weights',
                          save_path: Optional[str] = None):
    """
    Plot attention weights for posts.
    
    Args:
        attention_weights: Array of attention weights
        post_texts: List of post texts (truncated for display)
        title: Plot title
        save_path: Path to save the plot
    """
    # Truncate post texts for display
    truncated_texts = [text[:50] + '...' if len(text) > 50 else text 
                      for text in post_texts]
    
    plt.figure(figsize=(12, 6))
    
    bars = plt.bar(range(len(attention_weights)), attention_weights, 
                   color='lightcoral', alpha=0.7)
    
    plt.title(title, fontsize=16)
    plt.xlabel('Post Index', fontsize=12)
    plt.ylabel('Attention Weight', fontsize=12)
    plt.xticks(range(len(truncated_texts)), 
               [f'Post {i+1}' for i in range(len(truncated_texts))],
               rotation=45)
    
    # Add text annotations
    for i, (bar, text) in enumerate(zip(bars, truncated_texts)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_class_distribution(labels: List[int], class_names: List[str],
                           title: str = 'Class Distribution',
                           save_path: Optional[str] = None):
    """
    Plot class distribution.
    
    Args:
        labels: List of class labels
        class_names: List of class names
        title: Plot title
        save_path: Path to save the plot
    """
    unique, counts = np.unique(labels, return_counts=True)
    
    plt.figure(figsize=(10, 6))
    
    bars = plt.bar([class_names[i] for i in unique], counts, 
                   color='lightgreen', alpha=0.7)
    
    plt.title(title, fontsize=16)
    plt.xlabel('Class', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=45)
    
    # Add count annotations
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontsize=12)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
