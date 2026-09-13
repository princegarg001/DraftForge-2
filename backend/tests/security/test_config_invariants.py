"""Regression tests for configuration safety.

The CORS wildcard was the single highest-severity finding in the baseline
audit: allow_origin_regex matched every *.onrender.com host while credentials
were enabled, so any hostname obtainable by deploying to Render could issue
credentialed requests against this API.
"""

from __future__ import annotations

import pytest

from app.config import Settings

pytestmark = pytest.mark.security

BASE_ENV: dict[str, str | bool] = {
    # Passed explicitly rather than inherited: conftest exports DEBUG=True for
    # the suite, and init kwargs are the only source that reliably overrides
    # the process environment.
    "DEBUG": False,
    "RATE_LIMIT_ENABLED": True,
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "service-key",
    "SUPABASE_JWT_SECRET": "jwt-secret",
    "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
    "NEO4J_USERNAME": "neo4j",
    "NEO4J_PASSWORD": "password",
    "QDRANT_URL": "https://example.qdrant.tech:6333",
    "QDRANT_API_KEY": "qdrant-key",
}


def build(**overrides: object) -> Settings:
    # _env_file=None so a developer's local .env cannot influence the result.
    return Settings(_env_file=None, **{**BASE_ENV, **overrides})  # type: ignore[arg-type]


class TestCORSOrigins:
    def test_wildcard_origin_is_rejected(self) -> None:
        with pytest.raises(ValueError, match=r"must not contain"):
            build(ENVIRONMENT="development", ALLOWED_ORIGINS="*")

    def test_production_requires_https_origins(self) -> None:
        with pytest.raises(ValueError, match=r"https"):
            build(
                ENVIRONMENT="production",
                ALLOWED_ORIGINS="http://app.example.com",
                REDIS_REQUIRED=True,
                EMAIL_PROVIDER="resend",
                RESEND_API_KEY="re_test",
                TRUSTED_HOSTS="api.example.com",
                APP_PUBLIC_URL="https://app.example.com",
            )

    def test_malformed_origin_is_rejected(self) -> None:
        with pytest.raises(ValueError, match=r"absolute origin"):
            build(ENVIRONMENT="development", ALLOWED_ORIGINS="not-a-url")

    def test_localhost_added_outside_production_only(self) -> None:
        dev = build(ENVIRONMENT="development", ALLOWED_ORIGINS="")
        assert any("localhost" in origin for origin in dev.ALLOWED_ORIGINS)

    def test_production_does_not_inject_localhost(self) -> None:
        prod = build(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="https://app.example.com",
            REDIS_REQUIRED=True,
            EMAIL_PROVIDER="resend",
            RESEND_API_KEY="re_test",
            TRUSTED_HOSTS="api.example.com",
            APP_PUBLIC_URL="https://app.example.com",
        )
        assert prod.ALLOWED_ORIGINS == ["https://app.example.com"]
        assert not any("localhost" in origin for origin in prod.ALLOWED_ORIGINS)


class TestProductionInvariants:
    def _prod(self, **overrides: object) -> Settings:
        defaults = {
            "ENVIRONMENT": "production",
            "ALLOWED_ORIGINS": "https://app.example.com",
            "TRUSTED_HOSTS": "api.example.com",
            "REDIS_REQUIRED": True,
            "RATE_LIMIT_ENABLED": True,
            "EMAIL_PROVIDER": "resend",
            "RESEND_API_KEY": "re_test",
            "APP_PUBLIC_URL": "https://app.example.com",
        }
        return build(**{**defaults, **overrides})

    def test_valid_production_config_builds(self) -> None:
        assert self._prod().is_production

    def test_debug_forbidden_in_production(self) -> None:
        with pytest.raises(ValueError, match=r"DEBUG"):
            self._prod(DEBUG=True)

    def test_wildcard_trusted_host_forbidden(self) -> None:
        with pytest.raises(ValueError, match=r"TRUSTED_HOSTS"):
            self._prod(TRUSTED_HOSTS="*")

    def test_rate_limiting_cannot_fail_open_in_production(self) -> None:
        with pytest.raises(ValueError, match=r"REDIS_REQUIRED"):
            self._prod(REDIS_REQUIRED=False)

    def test_rate_limiting_cannot_be_disabled_in_production(self) -> None:
        with pytest.raises(ValueError, match=r"RATE_LIMIT_ENABLED"):
            self._prod(RATE_LIMIT_ENABLED=False)

    def test_console_email_provider_forbidden(self) -> None:
        with pytest.raises(ValueError, match=r"EMAIL_PROVIDER"):
            self._prod(EMAIL_PROVIDER="console")

    def test_resend_requires_api_key(self) -> None:
        with pytest.raises(ValueError, match=r"RESEND_API_KEY"):
            self._prod(RESEND_API_KEY="")

    def test_public_url_must_be_https(self) -> None:
        with pytest.raises(ValueError, match=r"APP_PUBLIC_URL"):
            self._prod(APP_PUBLIC_URL="http://app.example.com")


class TestDocsExposure:
    def test_docs_disabled_in_production_even_when_enabled(self) -> None:
        settings = build(
            ENVIRONMENT="production",
            ENABLE_DOCS=True,
            ALLOWED_ORIGINS="https://app.example.com",
            TRUSTED_HOSTS="api.example.com",
            REDIS_REQUIRED=True,
            EMAIL_PROVIDER="resend",
            RESEND_API_KEY="re_test",
            APP_PUBLIC_URL="https://app.example.com",
        )
        assert settings.docs_enabled is False

    def test_docs_available_in_development(self) -> None:
        assert build(ENVIRONMENT="development", ENABLE_DOCS=True).docs_enabled is True


class TestDerivedURLs:
    def test_jwks_url_is_derived_from_project_url(self) -> None:
        settings = build(ENVIRONMENT="development", SUPABASE_URL="https://abc.supabase.co/")
        assert settings.jwks_url == "https://abc.supabase.co/auth/v1/.well-known/jwks.json"
        assert settings.jwt_issuer == "https://abc.supabase.co/auth/v1"
