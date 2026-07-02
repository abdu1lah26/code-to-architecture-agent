"""
Ollama LLM Client for local inference.
Handles communication with Ollama API.
"""

import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL (default from env or localhost:11434)
            model: Model name to use (default from env or deepseek-coder-v2)
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "deepseek-coder-v2")

    def health_check(self) -> bool:
        """Check if Ollama server is running."""
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            print(f"❌ Ollama health check failed: {e}")
            return False

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Generate text using Ollama.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text or None if error
        """
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "stream": False,
                    },
                    timeout=300,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    print(f"❌ Ollama error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"❌ Ollama request failed: {e}")
            return None

    def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.5,
        max_tokens: int = 1500
    ) -> Optional[str]:
        """
        Generate text with context (grounded in actual code).

        Args:
            prompt: The question/instruction
            context: Code snippets or relevant information
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated response grounded in context
        """
        full_prompt = f"""You are an expert software architect. Answer based on the provided code context.

CONTEXT:
{context}

INSTRUCTION:
{prompt}

ANSWER:"""

        return self.generate(full_prompt, temperature=temperature, max_tokens=max_tokens)


def test_ollama():
    """Test Ollama connection."""
    client = OllamaClient()

    if not client.health_check():
        print("❌ Ollama is not running. Start it with: ollama serve")
        return False

    print("✅ Ollama connection successful")

    # Test simple generation
    response = client.generate("What is software architecture?", max_tokens=100)
    if response:
        print(f"✅ Generation test passed\nResponse: {response[:100]}...")
        return True
    else:
        print("❌ Generation test failed")
        return False


if __name__ == "__main__":
    test_ollama()