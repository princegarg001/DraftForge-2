from typing import Optional
from app.ai.llm.base import BaseLLM
from app.ai.llm.groq import GroqLLM
from app.config import get_settings

settings = get_settings()


class LLMFactory:
    """Factory for initializing LLM providers based on environment configuration."""

    @staticmethod
    def get_llm(model_name: Optional[str] = None) -> BaseLLM:
        return GroqLLM(model_name=model_name)


def get_llm(model_name: Optional[str] = None) -> BaseLLM:
    """Convenience helper function to retrieve the configured LLM provider."""
    return LLMFactory.get_llm(model_name=model_name)