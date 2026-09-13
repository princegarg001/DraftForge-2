from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_DEV_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]


class Settings(BaseSettings):
    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "DraftForge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"  # noqa: S104 - binding all interfaces is required in a container
    PORT: int = 8000
    ENVIRONMENT: Literal["development", "staging", "production"] = "production"

    # Comma-separated exact origins. Local development origins are added
    # automatically outside production; they are never added in production.
    ALLOWED_ORIGINS: str | list[str] = Field(default_factory=list)

    # Hosts accepted in the Host header. "*" is rejected in production.
    TRUSTED_HOSTS: str | list[str] = Field(default_factory=lambda: ["*"])

    # Interactive API docs. Forced off in production unless explicitly enabled.
    ENABLE_DOCS: bool = False

    # ------------------------------------------------------------------
    # Supabase
    # ------------------------------------------------------------------
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    SUPABASE_REFERENCE_BUCKET: str = "reference-documents"
    SUPABASE_DRAFT_BUCKET: str = "student-drafts"
    SUPABASE_SUBMISSION_BUCKET: str = "assignment-submissions"

    # ------------------------------------------------------------------
    # JWT verification
    #
    # Tokens are verified locally against the project JWKS (asymmetric keys)
    # or the shared secret (legacy HS256). Either path removes the
    # per-request network round-trip to Supabase Auth.
    # ------------------------------------------------------------------
    JWT_AUDIENCE: str = "authenticated"
    JWT_LEEWAY_SECONDS: int = 30
    JWKS_CACHE_TTL_SECONDS: int = 600
    JWKS_REFRESH_COOLDOWN_SECONDS: int = 30
    JWKS_REQUEST_TIMEOUT_SECONDS: float = 5.0

    # ------------------------------------------------------------------
    # Graph, vector & LLM services
    # ------------------------------------------------------------------
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "neo4j"

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "legal_reference_corpus"

    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:latest"

    EMBEDDING_PROVIDER: str = "fastembed"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Outbound call budgets. Without these a hung upstream ties up a worker
    # indefinitely.
    LLM_REQUEST_TIMEOUT_SECONDS: float = 45.0
    VECTOR_REQUEST_TIMEOUT_SECONDS: float = 10.0
    GRAPH_REQUEST_TIMEOUT_SECONDS: float = 10.0

    # ------------------------------------------------------------------
    # Redis - rate limiting, caching and the email outbox
    # ------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_REQUIRED: bool = False  # when False, rate limiting fails open in dev

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = 120
    RATE_LIMIT_AUTH_PER_MINUTE: int = 5
    RATE_LIMIT_AUTH_PER_HOUR: int = 30
    RATE_LIMIT_LLM_PER_MINUTE: int = 10
    RATE_LIMIT_LLM_PER_DAY: int = 300
    RATE_LIMIT_UPLOAD_PER_HOUR: int = 40
    RATE_LIMIT_INVITE_PER_HOUR: int = 200

    # Per-user daily LLM token budget; 0 disables the budget check.
    LLM_TOKEN_BUDGET_PER_DAY: int = 150_000

    # ------------------------------------------------------------------
    # Request hardening
    # ------------------------------------------------------------------
    MAX_REQUEST_BYTES: int = 20 * 1024 * 1024
    MAX_UPLOAD_BYTES: int = 15 * 1024 * 1024
    HSTS_MAX_AGE_SECONDS: int = 63_072_000  # 2 years, preload-eligible

    # ------------------------------------------------------------------
    # Email (Resend) - student invitations
    # ------------------------------------------------------------------
    EMAIL_PROVIDER: Literal["resend", "console"] = "console"
    RESEND_API_KEY: str = ""
    RESEND_API_URL: str = "https://api.resend.com/emails"
    EMAIL_FROM_ADDRESS: str = "DraftForge <onboarding@draftforge.app>"
    EMAIL_REPLY_TO: str = ""
    EMAIL_REQUEST_TIMEOUT_SECONDS: float = 15.0
    EMAIL_MAX_RETRIES: int = 5

    INVITE_TOKEN_TTL_HOURS: int = 168  # 7 days
    APP_PUBLIC_URL: str = "http://localhost:5173"

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "draftforge-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_EXPORTER_OTLP_HEADERS: str = ""
    OTEL_TRACES_SAMPLER_RATIO: float = 1.0
    LOG_FORMAT: Literal["console", "json"] = "console"
    LOG_LEVEL: str = "INFO"

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("ALLOWED_ORIGINS", "TRUSTED_HOSTS", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> list[str]:
        # mode="before" runs on raw env input, which may be a CSV string,
        # a list, or absent entirely.
        if value is None or value == "":
            return []
        items = value.split(",") if isinstance(value, str) else list(value)  # type: ignore[arg-type]
        return [text.rstrip("/") for item in items if (text := str(item).strip())]

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def _validate_origins(cls, origins: list[str], info: ValidationInfo) -> list[str]:
        environment = info.data.get("ENVIRONMENT", "production")

        # Outside production, local dev origins are a convenience. In
        # production they are never injected - an origin must be configured
        # explicitly to be trusted.
        candidates = list(origins)
        if environment != "production":
            candidates += LOCAL_DEV_ORIGINS

        seen: set[str] = set()
        result: list[str] = []
        for origin in candidates:
            if origin == "*":
                raise ValueError(
                    "ALLOWED_ORIGINS must not contain '*'. Credentialed CORS requires exact origins."
                )
            parsed = urlparse(origin)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"ALLOWED_ORIGINS entry '{origin}' is not a valid absolute origin.")
            if environment == "production" and parsed.scheme != "https":
                raise ValueError(f"ALLOWED_ORIGINS entry '{origin}' must use https in production.")
            if origin not in seen:
                seen.add(origin)
                result.append(origin)
        return result

    @model_validator(mode="after")
    def _enforce_production_invariants(self) -> "Settings":
        if self.ENVIRONMENT != "production":
            return self

        if self.DEBUG:
            raise ValueError("DEBUG must be False in production.")
        if not self.ALLOWED_ORIGINS:
            raise ValueError("ALLOWED_ORIGINS must list at least one https origin in production.")
        if "*" in self.TRUSTED_HOSTS:
            raise ValueError("TRUSTED_HOSTS must be an explicit list in production, not '*'.")
        # Both halves matter. REDIS_REQUIRED=False lets limits fail open the
        # moment Redis blips, and RATE_LIMIT_ENABLED=False removes them
        # outright - which would leave the LLM endpoints unmetered again.
        if not self.RATE_LIMIT_ENABLED:
            raise ValueError("RATE_LIMIT_ENABLED must be True in production.")
        if not self.REDIS_REQUIRED:
            raise ValueError(
                "REDIS_REQUIRED must be True in production, otherwise rate limits "
                "silently fail open when Redis is unreachable."
            )
        if self.EMAIL_PROVIDER == "console":
            raise ValueError("EMAIL_PROVIDER must be a real provider in production, not 'console'.")
        if self.EMAIL_PROVIDER == "resend" and not self.RESEND_API_KEY:
            raise ValueError("RESEND_API_KEY is required when EMAIL_PROVIDER is 'resend'.")
        if not self.APP_PUBLIC_URL.startswith("https://"):
            raise ValueError("APP_PUBLIC_URL must be an https URL in production.")
        return self

    @property
    def jwks_url(self) -> str:
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"

    @property
    def jwt_issuer(self) -> str:
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1"

    @property
    def docs_enabled(self) -> bool:
        return self.ENABLE_DOCS and self.ENVIRONMENT != "production"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
