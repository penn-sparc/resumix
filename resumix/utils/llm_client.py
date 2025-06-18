from uuid import UUID
import requests
import os
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import Generation, LLMResult
from typing import Any, List, Optional, Dict
from pydantic import Field
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMWrapper(BaseLLM):
    client: Any = Field(exclude=True)
    model_name: str = "deepseek"

    # Required fields for LangChain Agent compatibility
    callbacks: Optional[List[Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Call LLM to generate text.
        
        Args:
            prompt: Input prompt text
            stop: Optional list of stop sequences
            
        Returns:
            Generated text from LLM
        """
        logger.info(f"Calling LLM with prompt: {prompt[:50]}...")
        return self.client(prompt)

    @property
    def _llm_type(self) -> str:
        """Return LLM type"""
        return "deepseek"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs,
    ) -> LLMResult:
        """Batch generation of text (used by Agent)"""
        generations = [[Generation(text=self._call(p))] for p in prompts]
        return LLMResult(generations=generations)


class LLMClient:
    _instance = None

    def __new__(cls, timeout=60):
        if cls._instance is None:
            cls._instance = super(LLMClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, timeout=60):
        if self._initialized:
            return
            
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model_name = "deepseek-chat"  # or whatever model you're using
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        self.timeout = timeout

    def __call__(self, prompt: str) -> str:
        """Call LLM to generate text"""
        logger.info(f"Calling Deepseek API with prompt: {prompt[:50]}...")
        return self.generate(prompt)

    def generate(self, prompt: str) -> str:
        """
        Call Deepseek API to generate text.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text or error message
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000,
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if not response.ok:
                return f"❌ Error: {response.status_code} - {response.text}"

            return (
                response.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "⚠️ Model did not return a result.")
            )

        except Exception as e:
            return f"❌ Error calling Deepseek API: {e}"


if __name__ == "__main__":
    # Initialize the client
    client = LLMClient()
    
    # Test with a simple prompt
    test_prompt = "Hello, world! Just reply 'OK' if you received this."
    response = client.generate(test_prompt)
    
    print("=== TEST RESULTS ===")
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")