import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer
import networkx as nx
from typing import List, Dict, Tuple, Optional


class PostEncoder(nn.Module):
    """
    Post Encoder that combines post-level and explanation-level representations
    using undirected tree structure for modeling post interactions.
    """
    
    def __init__(self, config):
        super(PostEncoder, self).__init__()
        
        self.config = config
        self.hidden_dim = config.model.post_encoder.hidden_dim
        self.retention_ratio = config.model.post_encoder.retention_ratio
        
        # Initialize encoders with offline mode support
        print("[PostEncoder] Loading BERT model...")
        try:
            self.bert_tokenizer = AutoTokenizer.from_pretrained(
                config.model.post_encoder.bert_model,
                local_files_only=True  # 优先使用本地缓存
            )
            self.bert_model = AutoModel.from_pretrained(
                config.model.post_encoder.bert_model,
                local_files_only=True
            )
            print(f"[PostEncoder] BERT loaded from cache: {config.model.post_encoder.bert_model}")
        except Exception as e:
            print(f"[PostEncoder] Loading BERT from cache failed, trying online: {e}")
            self.bert_tokenizer = AutoTokenizer.from_pretrained(config.model.post_encoder.bert_model)
            self.bert_model = AutoModel.from_pretrained(config.model.post_encoder.bert_model)
        
        bert_hidden = self.bert_model.config.hidden_size

        # Try to load Sentence-BERT; fall back to bert_model with mean-pooling if offline
        print("[PostEncoder] Loading Sentence-BERT model...")
        try:
            self.sentence_bert = SentenceTransformer(
                config.model.post_encoder.sentence_bert_model,
                device='cpu'  # 先在 CPU 加载，后续会移到 GPU
            )
            sbert_dim = self.sentence_bert.get_sentence_embedding_dimension()
            self._use_sbert = True
            print(f"[PostEncoder] Sentence-BERT loaded: {config.model.post_encoder.sentence_bert_model}")
        except Exception as e:
            print(f"[PostEncoder] SentenceTransformer unavailable ({e}), using BERT mean-pool for post/claim encoding.")
            self.sentence_bert = None
            sbert_dim = bert_hidden
            self._use_sbert = False

        # Projection layers
        self.post_projection   = nn.Linear(sbert_dim,   self.hidden_dim)
        self.explanation_projection = nn.Linear(bert_hidden, self.hidden_dim)
        self.claim_projection  = nn.Linear(sbert_dim,   self.hidden_dim)
        
        self.dropout = nn.Dropout(config.model.post_encoder.dropout)

    def _mean_pool_bert(self, texts: List[str]) -> torch.Tensor:
        """使用 BERT + mean-pooling 编码文本（离线 fallback）。"""
        inputs = self.bert_tokenizer(
            texts, padding=True, truncation=True,
            max_length=self.config.data.max_post_length,
            return_tensors='pt'
        )
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            # mean-pool over sequence (ignore padding)
            mask = inputs['attention_mask'].unsqueeze(-1)
            embeddings = (outputs.last_hidden_state * mask).sum(1) / mask.sum(1)
        return embeddings

    def encode_posts_with_structure(self, posts: List[str], structure_info: List[str]) -> torch.Tensor:
        """
        Encode posts with structural information prefixes.
        
        Args:
            posts: List of post texts
            structure_info: List of structural prefixes (e.g., "t1 replied to c")
            
        Returns:
            Post embeddings tensor of shape (num_posts, hidden_dim)
        """
        structured_posts = [f"{prefix}: {post}" for prefix, post in zip(structure_info, posts)]

        if self._use_sbert:
            post_embeddings = self.sentence_bert.encode(structured_posts, convert_to_tensor=True)
        else:
            post_embeddings = self._mean_pool_bert(structured_posts)

        post_embeddings = self.post_projection(post_embeddings)
        return post_embeddings
    
    def encode_explanations(self, explanations: List[str]) -> torch.Tensor:
        """
        Encode LLM-generated explanations using BERT.
        
        Args:
            explanations: List of explanation texts
            
        Returns:
            Explanation embeddings tensor of shape (num_explanations, hidden_dim)
        """
        # Tokenize explanations
        inputs = self.bert_tokenizer(
            explanations,
            padding=True,
            truncation=True,
            max_length=self.config.data.max_explanation_length,
            return_tensors="pt"
        )
        
        # Encode with BERT
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            explanation_embeddings = outputs.last_hidden_state[:, 0, :]  # Use [CLS] token
        
        # Project to hidden dimension
        explanation_embeddings = self.explanation_projection(explanation_embeddings)
        
        return explanation_embeddings
    
    def encode_claim(self, claim: str) -> torch.Tensor:
        """
        Encode claim using Sentence-BERT (or BERT mean-pool fallback).
        """
        if self._use_sbert:
            claim_embedding = self.sentence_bert.encode([claim], convert_to_tensor=True).squeeze(0)
        else:
            claim_embedding = self._mean_pool_bert([claim]).squeeze(0)

        claim_embedding = self.claim_projection(claim_embedding)
        return claim_embedding
    
    def compute_post_interactions(self, post_embeddings: torch.Tensor, 
                                tree_structure: Dict) -> torch.Tensor:
        """
        Compute post interactions using undirected tree structure.
        
        Args:
            post_embeddings: Post embeddings of shape (num_posts, hidden_dim)
            tree_structure: Dictionary representing the tree structure
            
        Returns:
            Updated post embeddings with interactions
        """
        num_posts = post_embeddings.size(0)
        updated_embeddings = post_embeddings.clone()
        
        # Build adjacency information from tree structure
        scale = post_embeddings.size(-1) ** 0.5
        for i in range(num_posts):
            neighbors = tree_structure.get(i, [])
            
            if neighbors:
                # Get neighbor embeddings
                neighbor_embeddings = post_embeddings[neighbors]
                
                # Dot-product attention: a_{ij} ∝ exp(o_j · o_i^T / sqrt(d))  (paper Eq.2)
                attention_scores = (neighbor_embeddings @ post_embeddings[i]) / scale
                attention_weights = F.softmax(attention_scores, dim=0)
                
                # Aggregate neighbor information
                aggregated_neighbor = torch.sum(
                    attention_weights.unsqueeze(-1) * neighbor_embeddings, dim=0
                )
                
                # Update post embedding with retention ratio rho
                updated_embeddings[i] = (
                    self.retention_ratio * post_embeddings[i] + 
                    (1 - self.retention_ratio) * aggregated_neighbor
                )
        
        return updated_embeddings
    
    def forward(self, claim: str, posts: List[str], explanations: List[str],
                structure_info: List[str], tree_structure: Dict) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass of the post encoder.
        
        Args:
            claim: Claim text
            posts: List of post texts
            explanations: List of explanation texts
            structure_info: List of structural prefixes
            tree_structure: Dictionary representing the tree structure
            
        Returns:
            Tuple of (final_post_embeddings, claim_embedding, explanation_embeddings)
        """
        # Encode claim
        claim_embedding = self.encode_claim(claim)
        
        # Encode posts with structure
        post_embeddings = self.encode_posts_with_structure(posts, structure_info)
        
        # Encode explanations
        explanation_embeddings = self.encode_explanations(explanations)
        
        # Compute post interactions
        post_embeddings = self.compute_post_interactions(post_embeddings, tree_structure)
        
        # Combine post and explanation embeddings
        final_post_embeddings = torch.cat([post_embeddings, explanation_embeddings], dim=-1)
        final_post_embeddings = self.dropout(final_post_embeddings)
        
        return final_post_embeddings, claim_embedding, explanation_embeddings


def build_tree_structure(propagation_data: List[Dict]) -> Dict:
    """
    Build tree structure from propagation data.
    
    Args:
        propagation_data: List of dictionaries containing post relationships
        
    Returns:
        Dictionary mapping post indices to their neighbors
    """
    tree_structure = {}
    
    # Build undirected graph
    graph = nx.Graph()
    
    for relation in propagation_data:
        parent = relation.get('parent_id')
        child = relation.get('child_id')
        
        if parent is not None and child is not None:
            graph.add_edge(parent, child)
    
    # Convert to adjacency dictionary
    for node in graph.nodes():
        tree_structure[node] = list(graph.neighbors(node))
    
    return tree_structure
