from typing import List
from fastembed import TextEmbedding
from app.ai.embeddings.base import BaseEmbeddingProvider
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("fastembed_provider")
settings = get_settings()


class FastEmbedProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        logger.info(f"Loading FastEmbed model: {self.model_name}")
        self.model = TextEmbedding(model_name=self.model_name)
        self._dimension = 384  # Default for BAAI/bge-small-en-v1.5

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = list(self.model.embed(texts))
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, text: str) -> List[float]:
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    def get_dimension(self) -> int:
        return self._dimension