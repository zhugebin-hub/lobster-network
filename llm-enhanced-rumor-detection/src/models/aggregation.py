import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple
from .attention_mechanisms import ClaimExplanationAttention


class BinaryModelsAggregation(nn.Module):
    """
    Aggregation module (paper Eq.8-10):
      V^k  = softmax(c̄ · key_proj(claim_repr^k) / sqrt(d))
      ŷ_{c,r} = Σ_{k∈I(r)} V^k * ỹ_c^k        (rumor, Eq.10)
      p̂_{i,s} = Σ_{k∈I(s)} V^k * p̃_i^k[1]     (stance, Eq.9)

    where:
      c̄          = Sentence-BERT claim embedding (query)
      claim_repr^k = per-classifier claim representation (key)
      ỹ_c^k       = scalar binary rumor probability from GlobalAttention
      p̃_i^k[1]   = positive-class binary stance probability per post
    """

    def __init__(self, config):
        super(BinaryModelsAggregation, self).__init__()

        self.hidden_dim = config.model.post_encoder.hidden_dim
        self.num_rumor_classes = config.model.mil.num_rumor_classes
        self.num_stance_classes = config.model.mil.num_stance_classes
        self.num_binary_classifiers = config.model.mil.num_binary_classifiers

        self.claim_attention = ClaimExplanationAttention(
            self.hidden_dim, self.num_binary_classifiers
        )

        self.classifier_to_classes = self._create_classifier_mapping()

    def _create_classifier_mapping(self) -> dict:
        mapping = {}
        idx = 0
        for r in range(self.num_rumor_classes):
            for s in range(self.num_stance_classes):
                mapping[idx] = (r, s)
                idx += 1
        return mapping

    def forward(self,
                binary_stance_probs: List[torch.Tensor],
                binary_rumor_probs: List[torch.Tensor],
                claim_query: torch.Tensor,
                claim_representations: torch.Tensor
                ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            binary_stance_probs:   K-list of (num_posts, 2) softmax probability tensors
            binary_rumor_probs:    K-list of scalar tensors in [0,1]  (ỹ_c^k)
            claim_query:           (hidden_dim,)  -- Sentence-BERT claim embedding
            claim_representations: (K, hidden_dim) -- per-classifier claim representations

        Returns:
            final_stance_preds: (num_posts, num_stance_classes)
            final_rumor_probs:  (num_rumor_classes,)  unnormalized
            attention_weights:  (K,)
        """
        device = claim_query.device

        # Eq.8: compute attention weights V^k
        attn_weights = self.claim_attention(claim_query, claim_representations)  # (K,)

        num_posts = binary_stance_probs[0].size(0)

        # Eq.9: final stance per class s = Σ_{k∈I(s)} V^k * p̃_i^k[1]
        final_stance = torch.zeros(num_posts, self.num_stance_classes, device=device)
        for k in range(self.num_binary_classifiers):
            _, target_s = self.classifier_to_classes[k]
            final_stance[:, target_s] += attn_weights[k] * binary_stance_probs[k][:, 1]

        # Eq.10: final rumor per class r = Σ_{k∈I(r)} V^k * ỹ_c^k
        final_rumor = torch.zeros(self.num_rumor_classes, device=device)
        for k in range(self.num_binary_classifiers):
            target_r, _ = self.classifier_to_classes[k]
            final_rumor[target_r] += attn_weights[k] * binary_rumor_probs[k]

        return final_stance, final_rumor, attn_weights
