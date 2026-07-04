import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from typing import Dict, List, Tuple, Optional
import torch


def compute_metrics(y_true: List, y_pred: List, labels: Optional[List[str]] = None) -> Dict[str, float]:
    """
    Compute classification metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: Label names for reporting
        
    Returns:
        Dictionary containing metrics
    """
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    
    # Precision, recall, F1
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average='macro', zero_division=0
    )
    
    metrics['precision'] = precision
    metrics['recall'] = recall
    metrics['f1'] = f1
    
    # Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    
    if labels:
        for i, label in enumerate(labels):
            metrics[f'{label}_precision'] = precision_per_class[i]
            metrics[f'{label}_recall'] = recall_per_class[i]
            metrics[f'{label}_f1'] = f1_per_class[i]
    
    return metrics


class MetricsCalculator:
    """
    Utility class for computing and tracking metrics during training and evaluation.
    """
    
    def __init__(self, rumor_classes: List[str], stance_classes: List[str]):
        self.rumor_classes = rumor_classes
        self.stance_classes = stance_classes
        
    def compute_rumor_metrics(self, y_true: List, y_pred: List) -> Dict[str, float]:
        """Compute metrics for rumor detection."""
        return compute_metrics(y_true, y_pred, self.rumor_classes)
    
    def compute_stance_metrics(self, y_true: List, y_pred: List) -> Dict[str, float]:
        """Compute metrics for stance detection."""
        return compute_metrics(y_true, y_pred, self.stance_classes)
    
    def compute_confusion_matrix(self, y_true: List, y_pred: List, 
                               labels: List[str]) -> np.ndarray:
        """Compute confusion matrix."""
        return confusion_matrix(y_true, y_pred, labels=range(len(labels)))
    
    def format_metrics_report(self, metrics: Dict[str, float]) -> str:
        """Format metrics into a readable report."""
        report = []
        report.append("Metrics Report:")
        report.append("-" * 40)
        
        # Main metrics
        main_metrics = ['accuracy', 'precision', 'recall', 'f1']
        for metric in main_metrics:
            if metric in metrics:
                report.append(f"{metric.capitalize()}: {metrics[metric]:.4f}")
        
        # Per-class metrics
        report.append("\nPer-class metrics:")
        for key, value in metrics.items():
            if any(cls in key for cls in self.rumor_classes + self.stance_classes):
                report.append(f"  {key}: {value:.4f}")
        
        return "\n".join(report)
