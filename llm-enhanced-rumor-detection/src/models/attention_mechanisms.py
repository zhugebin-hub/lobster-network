import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple
import math


class LocalAttention(nn.Module):
    """
    Local Attention (paper Eq.6): updates each node's binary stance probability
    using dot-product attention over tree neighbors.  No node filtering is applied.
    """

    def __init__(self, retention_ratio: float = 0.5):
        super(LocalAttention, self).__init__()
        self.retention_ratio = retention_ratio  # lambda in paper

    def forward(self, stance_probs: torch.Tensor,
                tree_structure: Dict) -> torch.Tensor:
        """
        Args:
            stance_probs: Binary stance probs (num_posts, 2) from binary stance classifier
            tree_structure: {post_idx: [neighbor_idx, ...]}

        Returns:
            updated_probs: (num_posts, 2)  -- paper Eq.6 p̃'_i
        """
        num_posts = stance_probs.size(0)
        updated_probs = stance_probs.clone()

        for i in range(num_posts):
            neighbors = tree_structure.get(i, [])
            if not neighbors:
                continue

            neighbor_probs = stance_probs[neighbors]          # (k, 2)
            # dot-product attention: a_{ij} ∝ exp(p̃_j · p̃_i^T)
            scores = neighbor_probs @ stance_probs[i]         # (k,)
            attn = F.softmax(scores, dim=0)                   # (k,)
            aggregated = (attn.unsqueeze(-1) * neighbor_probs).sum(0)  # (2,)
            updated_probs[i] = (self.retention_ratio * stance_probs[i]
                                + (1.0 - self.retention_ratio) * aggregated)

        return updated_probs  # (num_posts, 2)


class GlobalAttention(nn.Module):
    """
    Stance-Explanation-Guided Global Attention (paper Eq.7).
    beta_i = softmax(e_i · x_c^T)
    y_c^k  = sum_i(beta_i * p̃'_i^k[1])   <- scalar binary rumor probability
    """

    def __init__(self, hidden_dim: int):
        super(GlobalAttention, self).__init__()
        self.scale = math.sqrt(hidden_dim)

    def forward(self, updated_stance_probs: torch.Tensor,
                explanation_embeddings: torch.Tensor,
                claim_embedding: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            updated_stance_probs:    (num_posts, 2)  after LocalAttention
            explanation_embeddings:  (num_posts, hidden_dim)
            claim_embedding:         (hidden_dim,)

        Returns:
            rumor_prob:      scalar tensor in [0,1]  -- ỹ_c^k
            attn_weights:    (num_posts,)
        """
        # beta_i = softmax(e_i · x_c / sqrt(d))
        scores = (explanation_embeddings @ claim_embedding) / self.scale  # (num_posts,)
        attn_weights = F.softmax(scores, dim=0)                           # (num_posts,)

        # ỹ_c^k = Σ beta_i * p̃'_i^k[positive_class]
        pos_probs = updated_stance_probs[:, 1]                            # (num_posts,)
        rumor_prob = torch.sum(attn_weights * pos_probs)                  # scalar
        return rumor_prob, attn_weights


class HierarchicalStanceTreeAttention(nn.Module):
    """
    Hierarchical Stance Tree Attention combining LocalAttention and GlobalAttention.
    """

    def __init__(self, hidden_dim: int, local_retention_ratio: float = 0.5,
                 global_attention_dim: int = 256):
        super(HierarchicalStanceTreeAttention, self).__init__()
        self.local_attention = LocalAttention(local_retention_ratio)
        self.global_attention = GlobalAttention(hidden_dim)

    def forward(self, stance_probs: torch.Tensor,
                explanation_embeddings: torch.Tensor,
                tree_structure: Dict,
                claim_embedding: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            stance_probs:           (num_posts, 2)
            explanation_embeddings: (num_posts, hidden_dim)
            tree_structure:         {post_idx: [neighbor_idx, ...]}
            claim_embedding:        (hidden_dim,)

        Returns:
            rumor_prob:          scalar -- ỹ_c^k (binary rumor probability for classifier k)
            updated_stance_probs:(num_posts, 2)
            attn_weights:        (num_posts,)
        """
        updated_stance_probs = self.local_attention(stance_probs, tree_structure)
        rumor_prob, attn_weights = self.global_attention(
            updated_stance_probs, explanation_embeddings, claim_embedding
        )
        return rumor_prob, updated_stance_probs, attn_weights


class ClaimExplanationAttention(nn.Module):
    """
    Claim-explanation-guided attention for binary model aggregation (paper Eq.8).
    V^k = softmax(c̄ · key_proj(claim_repr^k) / sqrt(d))
    where c̄ is the global claim query (Sentence-BERT claim embedding).
    """

    def __init__(self, hidden_dim: int, num_binary_classifiers: int):
        super(ClaimExplanationAttention, self).__init__()
        self.hidden_dim = hidden_dim
        self.scale = math.sqrt(hidden_dim)
        # Project per-classifier claim representation to key space
        self.key_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.dropout = nn.Dropout(0.1)

    def forward(self, claim_query: torch.Tensor,
                claim_representations: torch.Tensor) -> torch.Tensor:
        """
        Args:
            claim_query:           (hidden_dim,)  -- global claim embedding (Sentence-BERT)
            claim_representations: (K, hidden_dim) -- per-classifier claim representations

        Returns:
            attention_weights: (K,)
        """
        keys = self.key_proj(claim_representations)           # (K, hidden_dim)
        scores = (keys @ claim_query) / self.scale            # (K,)
        attention_weights = F.softmax(scores, dim=0)          # (K,)
        attention_weights = self.dropout(attention_weights)
        return attention_weights
