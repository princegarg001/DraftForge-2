from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "Legal Drafting AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "production"
    ALLOWED_ORIGINS: Union[str, List[str]] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://draftforge-2-1.onrender.com",
            "https://draftforge-2-d9mc.onrender.com",
        ]
    )

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Supabase Storage Buckets
    SUPABASE_REFERENCE_BUCKET: str = "reference-documents"
    SUPABASE_DRAFT_BUCKET: str = "student-drafts"
    SUPABASE_SUBMISSION_BUCKET: str = "assignment-submissions"

    # Neo4j Aura Cloud
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "neo4j"

    # Qdrant Managed Cloud
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "legal_reference_corpus"

    # LLM Providers
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:latest"

    # Embeddings Configuration
    EMBEDDING_PROVIDER: str = "fastembed"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Union[str, List[str]]) -> List[str]:
        default_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://draftforge-2-1.onrender.com",
            "https://draftforge-2-d9mc.onrender.com",
        ]
        if not value:
            return default_origins

        if isinstance(value, str):
            parsed = [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        elif isinstance(value, list):
            parsed = [origin.strip().rstrip("/") if isinstance(origin, str) else origin for origin in value]
        else:
            parsed = []

        seen = set()
        combined = []
        for origin in parsed + default_origins:
            if origin and origin not in seen:
                seen.add(origin)
                combined.append(origin)
        return combined

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()