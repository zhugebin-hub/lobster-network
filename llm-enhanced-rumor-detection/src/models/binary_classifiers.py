import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple


class BinaryStanceClassifier(nn.Module):
    """
    Binary stance classifier for MIL framework (paper Eq.5).
    Each classifier k targets one specific (rumor_class, stance_class) pair.
    Input:  x̃_i ⊕ ô_c  =  (post+expl embedding) concat claim embedding
    Output: 2-class softmax probability (negative / positive)
    """

    def __init__(self, input_dim: int, hidden_dim: int = 256):
        super(BinaryStanceClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 2)
        self.dropout = nn.Dropout(0.1)
        self.activation = nn.ReLU()

    def forward(self, post_claim_pairs: torch.Tensor) -> torch.Tensor:
        """
        Args:
            post_claim_pairs: (num_posts, input_dim)
        Returns:
            logits: (num_posts, 2)  -- softmax applied externally
        """
        x = self.activation(self.fc1(post_claim_pairs))
        x = self.dropout(x)
        x = self.activation(self.fc2(x))
        x = self.dropout(x)
        return self.fc3(x)


class MILBinaryClassifiers(nn.Module):
    """
    K = Nr * Ns binary stance classifiers.
    Rumor probability for each classifier k comes from GlobalAttention output,
    NOT from a separate rumor head (paper architecture).
    """

    def __init__(self, config):
        super(MILBinaryClassifiers, self).__init__()

        self.num_rumor_classes = config.model.mil.num_rumor_classes
        self.num_stance_classes = config.model.mil.num_stance_classes
        self.num_binary_classifiers = config.model.mil.num_binary_classifiers

        # input = (post_emb ⊕ expl_emb) ⊕ claim_emb = 2*d + d = 3*d
        self.input_dim = config.model.post_encoder.hidden_dim * 3

        self.stance_classifiers = nn.ModuleList([
            BinaryStanceClassifier(self.input_dim)
            for _ in range(self.num_binary_classifiers)
        ])

        # Mapping: classifier_idx -> (rumor_class, stance_class)
        self.classifier_mapping = self._create_classifier_mapping()

    def _create_classifier_mapping(self) -> dict:
        mapping = {}
        idx = 0
        for r in range(self.num_rumor_classes):
            for s in range(self.num_stance_classes):
                mapping[idx] = (r, s)
                idx += 1
        return mapping

    def forward(self, post_claim_pairs: torch.Tensor) -> List[torch.Tensor]:
        """
        Run all K stance classifiers.

        Args:
            post_claim_pairs: (num_posts, input_dim)

        Returns:
            List of K tensors, each (num_posts, 2)  -- binary stance logits
        """
        return [cls(post_claim_pairs) for cls in self.stance_classifiers]

    def get_target_class_pair(self, classifier_idx: int) -> Tuple[int, int]:
        """Return (rumor_class, stance_class) target for classifier k."""
        return self.classifier_mapping[classifier_idx]
