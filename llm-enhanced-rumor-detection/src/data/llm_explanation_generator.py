import openai
import os
import time
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ExplanationRequest:
    """Data class for explanation generation requests."""
    post_content: str
    claim_content: str
    stance_type: str
    rumor_type: str
    structure_info: str


class LLMExplanationGenerator:
    """
    Generator for LLM-based explanations for stance and claim characteristics.
    Uses OpenAI's GPT models to generate contextual explanations.
    """
    
    def __init__(self, config):
        self.config = config
        # Model name comes from config; default to DeepSeek chat model
        self.model = getattr(config.model.llm, "model", "deepseek-chat")
        self.max_tokens = config.model.llm.max_tokens
        self.temperature = config.model.llm.temperature
        
        # Initialize DeepSeek client (OpenAI-compatible API)
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable is not set. "
                "Please set it to your DeepSeek API key."
            )
        base_url = getattr(config.model.llm, "base_url", "https://api.deepseek.com")
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Apply rate limiting between API requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def generate_stance_explanation(self, post_content: str, claim_content: str,
                                  stance_type: str, rumor_type: str,
                                  structure_info: str) -> str:
        """
        Generate stance explanation for a post.
        
        Args:
            post_content: Content of the post
            claim_content: Content of the claim
            stance_type: Target stance type (support, deny, question, comment)
            rumor_type: Target rumor type (true, false, unverified, non-rumor)
            structure_info: Structural information (e.g., "t1 replied to c")
            
        Returns:
            Generated explanation text
        """
        prompt = self._create_stance_prompt(
            post_content, claim_content, stance_type, rumor_type, structure_info
        )
        
        return self._call_llm(prompt)
    
    def generate_claim_explanation(self, claim_content: str, rumor_type: str) -> str:
        """
        Generate claim explanation for rumor type characteristics.
        
        Args:
            claim_content: Content of the claim
            rumor_type: Target rumor type
            
        Returns:
            Generated explanation text
        """
        prompt = self._create_claim_prompt(claim_content, rumor_type)
        return self._call_llm(prompt)
    
    def _create_stance_prompt(self, post_content: str, claim_content: str,
                            stance_type: str, rumor_type: str, structure_info: str) -> str:
        """Create prompt for stance explanation generation."""
        
        stance_mapping = {
            'support': 'support stance',
            'deny': 'deny stance', 
            'question': 'question stance',
            'comment': 'comment stance'
        }
        
        rumor_mapping = {
            'true': 'true rumor',
            'false': 'false rumor',
            'unverified': 'unverified rumor',
            'non-rumor': 'non-rumor'
        }
        
        stance_label = stance_mapping.get(stance_type.lower(), stance_type)
        rumor_label = rumor_mapping.get(rumor_type.lower(), rumor_type)
        
        prompt = f"""What are the characteristics of "{stance_label}" in the post "{structure_info}: {post_content}", towards "{rumor_label}" claimed that "{claim_content}"?

Please provide a concise explanation focusing on:
1. The linguistic indicators that suggest this stance
2. The relationship between the post content and the claim
3. How the structural position influences the stance expression

Keep the explanation under 100 words and focus on specific textual evidence."""
        
        return prompt
    
    def _create_claim_prompt(self, claim_content: str, rumor_type: str) -> str:
        """Create prompt for claim explanation generation."""
        
        rumor_mapping = {
            'true': 'True rumor',
            'false': 'False rumor', 
            'unverified': 'Unverified rumor',
            'non-rumor': 'Non-rumor'
        }
        
        rumor_label = rumor_mapping.get(rumor_type.lower(), rumor_type)
        
        prompt = f"""What are the characteristics of "{rumor_label}" in the claim "{claim_content}"?

Please provide a concise explanation focusing on:
1. Content characteristics that indicate this rumor type
2. Language patterns typical of this category
3. Contextual clues about veracity

Keep the explanation under 80 words and focus on specific indicators."""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Make API call to LLM with rate limiting and error handling.
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            Generated explanation text
        """
        self._rate_limit()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in social media analysis and rumor detection. Provide concise, analytical explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            explanation = response.choices[0].message.content.strip()
            return explanation
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            # Return a fallback explanation
            return f"Analysis of content characteristics and contextual indicators."
    
    def generate_batch_explanations(self, requests: List[ExplanationRequest]) -> List[str]:
        """
        Generate explanations for a batch of requests.
        
        Args:
            requests: List of explanation requests
            
        Returns:
            List of generated explanations
        """
        explanations = []
        
        for request in requests:
            explanation = self.generate_stance_explanation(
                request.post_content,
                request.claim_content,
                request.stance_type,
                request.rumor_type,
                request.structure_info
            )
            explanations.append(explanation)
        
        return explanations
    
    def cache_explanations(self, explanations: Dict, cache_file: str):
        """Cache generated explanations to avoid repeated API calls."""
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(explanations, f, ensure_ascii=False, indent=2)
    
    def load_cached_explanations(self, cache_file: str) -> Dict:
        """Load cached explanations from file."""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}


class MockLLMExplanationGenerator(LLMExplanationGenerator):
    """
    Mock version of LLM explanation generator for testing without API calls.
    """
    
    def __init__(self, config):
        self.config = config
        
    def _call_llm(self, prompt: str) -> str:
        """Return mock explanation without API call."""
        return "Mock explanation: Analysis of linguistic patterns and contextual indicators suggests specific stance characteristics."
    
    def generate_stance_explanation(self, post_content: str, claim_content: str,
                                  stance_type: str, rumor_type: str,
                                  structure_info: str) -> str:
        # Handle unknown rumor type to prevent data leakage
        if rumor_type.lower() in ['unknown', 'unk']:
            return f"Mock stance explanation for {stance_type}: {structure_info}"
        return f"Mock stance explanation for {stance_type} towards {rumor_type}: {structure_info}"
    
    def generate_claim_explanation(self, claim_content: str, rumor_type: str) -> str:
        return f"Mock claim explanation for {rumor_type}: Content analysis indicates typical characteristics."
