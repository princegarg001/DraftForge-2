from typing import List
from app.ai.embeddings.base import BaseEmbeddingProvider
from app.ai.embeddings.factory import EmbeddingFactory


class EmbeddingService:
    _instance: BaseEmbeddingProvider = None

    @classmethod
    def get_provider(cls) -> BaseEmbeddingProvider:
        if cls._instance is None:
            cls._instance = EmbeddingFactory.get_provider()
        return cls._instance

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        return cls.get_provider().embed_documents(texts)

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        return cls.get_provider().embed_query(text)

    @classmethod
    def get_dimension(cls) -> int:
        return cls.get_provider().get_dimension()