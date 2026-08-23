from app.ai.embeddings.base import BaseEmbeddingProvider
from app.ai.embeddings.fastembed_provider import FastEmbedProvider
from app.config import get_settings

settings = get_settings()


class EmbeddingFactory:
    @staticmethod
    def get_provider(provider_type: str = None, model_name: str = None) -> BaseEmbeddingProvider:
        provider = provider_type or settings.EMBEDDING_PROVIDER
        if provider.lower() == "fastembed":
            return FastEmbedProvider(model_name=model_name)
        # Defaults to FastEmbed
        return FastEmbedProvider(model_name=model_name)