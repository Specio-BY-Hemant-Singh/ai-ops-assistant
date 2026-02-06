"""
LLM Client for Google Gemini API
Handles all interactions with the Gemini model
"""
import os
import json
import time
from typing import Optional, Dict, Any
import google.generativeai as genai


class LLMClient:
    """Wrapper for Google Gemini API with structured output support"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the LLM client
        
        Args:
            api_key: Google API key (if None, reads from env)
            model_name: Gemini model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
    def get_completion(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        Get completion from Gemini with retry logic
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            temperature: Sampling temperature (0.0 to 1.0)
            max_retries: Number of retries on failure
            
        Returns:
            Model response as string
        """
        for attempt in range(max_retries):
            try:
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                )
                
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=system_instruction
                    )
                else:
                    model = self.model
                
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                return response.text
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"LLM call failed after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
    def get_json_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Get structured JSON completion from Gemini
        
        Args:
            prompt: User prompt (should request JSON output)
            system_instruction: System instruction
            temperature: Lower temperature for more consistent JSON
            
        Returns:
            Parsed JSON response as dictionary
        """
        # Add JSON formatting instruction to prompt
        json_prompt = f"""{prompt}

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanations, just the JSON object."""
        
        if system_instruction:
            system_instruction += "\nYou must respond with valid JSON only."
        else:
            system_instruction = "You must respond with valid JSON only."
        
        response = self.get_completion(
            json_prompt,
            system_instruction=system_instruction,
            temperature=temperature
        )
        
        # Try to parse JSON from response
        return self.parse_json_response(response)
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from model response, handling markdown code blocks
        
        Args:
            response: Raw model response
            
        Returns:
            Parsed JSON as dictionary
        """
        # Remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to find JSON object in the response
            import re
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            raise ValueError(f"Failed to parse JSON from response: {e}\nResponse: {response}")


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create singleton LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
