import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional

from .post_encoder import PostEncoder
from .attention_mechanisms import HierarchicalStanceTreeAttention
from .binary_classifiers import MILBinaryClassifiers
from .aggregation import BinaryModelsAggregation

_EPS = 1e-8


class LLMEnhancedMIL(nn.Module):
    """
    LLM-Enhanced Multiple Instance Learning model for joint rumor and stance detection.
    Paper: "LLM-Enhanced Multiple Instance Learning for Joint Rumor and Stance
    Detection with Social Context Information"

    Two-stage training:
      Phase 1: train PostEncoder + binary stance classifiers + HierarchicalStanceTreeAttention
               Loss = Σ_k BCE(ỹ_c^k, y^k)           (paper Eq.12)
      Phase 2: freeze Phase-1 params; train only BinaryModelsAggregation
               Loss = Σ_r BCE(ŷ_{c,r}, y_r)          (paper Eq.13)
    """

    def __init__(self, config):
        super(LLMEnhancedMIL, self).__init__()

        self.config = config
        self.hidden_dim = config.model.post_encoder.hidden_dim
        self.num_rumor_classes = config.model.mil.num_rumor_classes
        self.num_stance_classes = config.model.mil.num_stance_classes
        self.num_binary_classifiers = config.model.mil.num_binary_classifiers

        self.post_encoder = PostEncoder(config)
        self.hierarchical_attention = HierarchicalStanceTreeAttention(
            self.hidden_dim,
            config.model.attention.local_retention_ratio,
            config.model.attention.global_attention_dim,
        )
        self.binary_classifiers = MILBinaryClassifiers(config)
        self.aggregation = BinaryModelsAggregation(config)
        
    def forward(self, batch_data: Dict) -> Dict[str, torch.Tensor]:
        """
        Forward pass. Supports both single sample and batch (list of samples).
        """
        posts = batch_data['posts']
        is_batch = isinstance(posts, list) and len(posts) > 0 and isinstance(posts[0], list)
        if is_batch:
            return self._forward_batch(batch_data)
        return self._forward_single(batch_data)

    def _forward_single(self, batch_data: Dict) -> Dict[str, torch.Tensor]:
        """
        Forward pass for one claim + its posts.

        Pipeline (matches paper exactly):
          Eq.1-4  : PostEncoder   → post_embeddings (num_posts, 2d), claim_embedding (d), explanation_embeddings (num_posts, d)
          Eq.5    : K stance classifiers → stance_logits_k (num_posts, 2)
          Eq.6    : LocalAttention   → updated_stance_probs_k (num_posts, 2)
          Eq.7    : GlobalAttention  → binary_rumor_prob_k  (scalar ỹ_c^k)
          Eq.8-10 : BinaryModelsAggregation → final_stance (num_posts, Ns), final_rumor (Nr,)
        """
        claim        = batch_data['claim']
        posts        = batch_data['posts']
        explanations = batch_data['explanations']
        structure_info  = batch_data['structure_info']
        tree_structure  = batch_data['tree_structure']

        # --- Eq.1-4: Post Encoding ---
        post_embeddings, claim_embedding, explanation_embeddings = self.post_encoder(
            claim, posts, explanations, structure_info, tree_structure
        )
        num_posts = post_embeddings.size(0)

        # post_claim_pairs = x̃_i ⊕ ô_c  (num_posts, 3d)
        claim_expanded  = claim_embedding.unsqueeze(0).expand(num_posts, -1)
        post_claim_pairs = torch.cat([post_embeddings, claim_expanded], dim=-1)

        # --- Eq.5: Binary stance classifiers → softmax probs ---
        stance_logits_list = self.binary_classifiers(post_claim_pairs)   # K × (num_posts, 2)
        binary_stance_probs = [F.softmax(lg, dim=-1) for lg in stance_logits_list]

        # --- Eq.6-7: Hierarchical Stance Tree Attention per classifier ---
        binary_rumor_probs  = []   # K scalars  ỹ_c^k
        updated_stance_list = []   # K × (num_posts, 2)

        for k in range(self.num_binary_classifiers):
            rumor_prob_k, updated_k, _ = self.hierarchical_attention(
                binary_stance_probs[k],   # (num_posts, 2)
                explanation_embeddings,   # (num_posts, d)
                tree_structure,
                claim_embedding,          # (d,)
            )
            binary_rumor_probs.append(rumor_prob_k)
            updated_stance_list.append(updated_k)

        # --- claim_representations for Eq.8 aggregation attention ---
        # Use claim_embedding for all k (upgraded when real LLM claim expl. available)
        claim_representations = claim_embedding.unsqueeze(0).expand(
            self.num_binary_classifiers, -1
        ).contiguous()  # (K, d)

        # --- Eq.8-10: Aggregation ---
        final_stance, final_rumor_raw, attn_weights = self.aggregation(
            binary_stance_probs,   # K × (num_posts, 2)
            binary_rumor_probs,    # K scalars
            claim_embedding,       # query  (d,)
            claim_representations, # keys   (K, d)
        )

        return {
            'stance_predictions':     final_stance,         # (num_posts, Ns)
            'rumor_probs':            final_rumor_raw,       # (Nr,)  unnormalized
            'binary_stance_probs':    binary_stance_probs,  # K × (num_posts, 2)
            'binary_rumor_probs':     binary_rumor_probs,   # K scalars
            'aggregation_weights':    attn_weights,         # (K,)
            'claim_embedding':        claim_embedding,
            'explanation_embeddings': explanation_embeddings,
        }

    def _forward_batch(self, batch_data: Dict) -> Dict[str, torch.Tensor]:
        """Iterate over batch samples; outputs are lists (variable-length posts)."""
        claims         = batch_data['claim']
        posts_batch    = batch_data['posts']
        expl_batch     = batch_data['explanations']
        si_batch       = batch_data['structure_info']
        ts_batch       = batch_data['tree_structure']

        batch_outputs = []
        for i in range(len(posts_batch)):
            sample = {
                'claim':          claims[i] if isinstance(claims, list) else claims,
                'posts':          posts_batch[i],
                'explanations':   expl_batch[i],
                'structure_info': si_batch[i],
                'tree_structure': ts_batch[i],
            }
            if 'rumor_label' in batch_data:
                rl = batch_data['rumor_label']
                sample['rumor_label'] = rl[i] if isinstance(rl, (list, torch.Tensor)) else rl
            batch_outputs.append(self._forward_single(sample))

        # Merge: tensor keys that are same shape → stack; else keep as list
        merged = {}
        for key in batch_outputs[0].keys():
            vals = [o[key] for o in batch_outputs]
            if isinstance(vals[0], torch.Tensor) and all(v.shape == vals[0].shape for v in vals):
                merged[key] = torch.stack(vals, dim=0)
            else:
                merged[key] = vals
        return merged

    
    def compute_loss(self, outputs: Dict[str, torch.Tensor],
                     batch_data: Dict,
                     phase: int = 1) -> Dict[str, torch.Tensor]:
        """
        Compute training loss.

        Phase 1 (binary classifier training, paper Eq.12):
            L1 = Σ_k BCE(ỹ_c^k, y^k)
            where y^k = 1 iff claim's rumor_label == target_rumor_class of classifier k.

        Phase 2 (aggregation training, paper Eq.13):
            L2 = Σ_r BCE(ŷ_{c,r}, (rumor_label == r).float())

        Args:
            outputs:    from forward()
            batch_data: contains 'rumor_label' (int or 0-d tensor)
            phase:      1 or 2
        """
        losses = {}

        if 'rumor_label' not in batch_data:
            losses['total_loss'] = torch.tensor(0.0, requires_grad=True)
            return losses

        rumor_label = batch_data['rumor_label']
        if isinstance(rumor_label, torch.Tensor):
            rumor_label = int(rumor_label.item())
        else:
            rumor_label = int(rumor_label)

        device = outputs['rumor_probs'].device

        if phase == 1:
            # --- Eq.12: BCE per binary classifier ---
            binary_rumor_probs = outputs['binary_rumor_probs']  # K scalars
            phase1_loss = torch.tensor(0.0, device=device)
            for k in range(self.num_binary_classifiers):
                target_r, _ = self.binary_classifiers.get_target_class_pair(k)
                y_k = float(rumor_label == target_r)
                prob_k = binary_rumor_probs[k].clamp(_EPS, 1.0 - _EPS)
                bce_k = -(y_k * torch.log(prob_k) + (1.0 - y_k) * torch.log(1.0 - prob_k))
                phase1_loss = phase1_loss + bce_k
            losses['phase1_loss'] = phase1_loss
            losses['total_loss']  = phase1_loss

        else:
            # --- Eq.13: BCE on final aggregated rumor probabilities ---
            final_rumor = outputs['rumor_probs']   # (Nr,)  unnormalized but in [0,1]
            phase2_loss = torch.tensor(0.0, device=device)
            for r in range(self.num_rumor_classes):
                y_r  = float(rumor_label == r)
                p_r  = final_rumor[r].clamp(_EPS, 1.0 - _EPS)
                bce_r = -(y_r * torch.log(p_r) + (1.0 - y_r) * torch.log(1.0 - p_r))
                phase2_loss = phase2_loss + bce_r
            losses['phase2_loss'] = phase2_loss
            losses['total_loss']  = phase2_loss

        return losses

    def predict(self, batch_data: Dict, use_phase1_logic: bool = False) -> Dict[str, torch.Tensor]:
        """Make predictions without gradients.
        
        Args:
            batch_data: Input data
            use_phase1_logic: If True, use binary_rumor_probs average instead of aggregation
                             (useful for Phase 1 evaluation when aggregation is not trained)
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(batch_data)
            
            if use_phase1_logic:
                # Phase 1: use binary_rumor_probs to compute rumor prediction
                # Average the probabilities for each rumor class across its classifiers
                binary_rumor_probs = outputs['binary_rumor_probs']  # K scalars
                rumor_probs_aggregated = torch.zeros(self.num_rumor_classes, device=binary_rumor_probs[0].device)
                
                for k in range(self.num_binary_classifiers):
                    target_r, _ = self.binary_classifiers.get_target_class_pair(k)
                    rumor_probs_aggregated[target_r] += binary_rumor_probs[k]
                
                # Normalize by number of classifiers per rumor class
                rumor_probs_aggregated = rumor_probs_aggregated / self.num_stance_classes
                rumor_probs = rumor_probs_aggregated
            else:
                # Phase 2: use aggregation output
                rumor_probs = outputs['rumor_probs']  # (Nr,)
            
            rumor_class = torch.argmax(rumor_probs, dim=-1)  # scalar
            stance_classes = torch.argmax(outputs['stance_predictions'], dim=-1)  # (num_posts,)
        
        return {
            'rumor_class':   rumor_class,
            'stance_classes': stance_classes,
            'rumor_probs':   rumor_probs,
            'stance_probs':  outputs['stance_predictions'],
        }


def create_model(config) -> LLMEnhancedMIL:
    """
    Factory function to create LLM-Enhanced MIL model.
    
    Args:
        config: Configuration object
        
    Returns:
        Initialized model
    """
    model = LLMEnhancedMIL(config)
    
    # Initialize weights
    def init_weights(m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                torch.nn.init.zeros_(m.bias)
    
    model.apply(init_weights)
    
    return model
