from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """Abstract base class for high-dimensional vector embedding providers."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text chunks."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generates an embedding for a single search query."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Returns vector dimensionality (e.g. 384 for BGE-small)."""
        pass