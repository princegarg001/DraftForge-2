from abc import ABC
from app.ai.llm.base import BaseLLM
from app.ai.llm.factory import LLMFactory


class BaseAgent(ABC):
    """Base class for all pedagogical AI agents."""

    def __init__(self, llm: BaseLLM = None):
        self.llm = llm or LLMFactory.get_llm()