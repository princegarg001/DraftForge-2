"""Authentication request/response schemas.

``role`` is deliberately absent from every request model. It was previously a
field on the registration request, which let any caller create a TEACHER
account for themselves. Roles are now assigned server-side only.
"""

from __future__ import annotations

import unicodedata

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.constants import UserRole

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

# Rejected outright regardless of length. Credential-stuffing lists are far
# larger than this; Supabase Auth applies its own breach checks on top. This
# catches the handful that pass a naive complexity rule.
_TRIVIAL_PASSWORDS = frozenset(
    {
        "password123",
        "passw0rd123",
        "administrator",
        "draftforge123",
        "qwertyuiop123",
        "123456789012",
        "letmein12345",
        "iloveyou1234",
        "welcome12345",
    }
)


def _validate_password_strength(value: str) -> str:
    # Normalize first: without NFKC, visually identical strings can carry
    # different byte lengths and defeat the length check.
    password = unicodedata.normalize("NFKC", value)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    if len(password) > MAX_PASSWORD_LENGTH:
        # Unbounded input is a hashing-cost denial-of-service vector.
        raise ValueError(f"Password must be at most {MAX_PASSWORD_LENGTH} characters long.")
    if password.lower() in _TRIVIAL_PASSWORDS:
        raise ValueError("This password is too common. Choose something less predictable.")

    categories = sum(
        [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ]
    )
    if categories < 3:
        raise ValueError(
            "Password must contain at least three of: lowercase, uppercase, digits, symbols."
        )
    return password


class _EmailNormalizingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("email", check_fields=False)
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserRegisterRequest(_EmailNormalizingModel):
    """Self-service registration. Always creates a STUDENT account.

    Teacher accounts are provisioned through the gated faculty-registration
    flow, never here.
    """

    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    full_name: str = Field(min_length=1, max_length=255)

    @field_validator("password")
    @classmethod
    def _check_password(cls, value: str) -> str:
        return _validate_password_strength(value)

    @field_validator("full_name")
    @classmethod
    def _clean_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Full name cannot be blank.")
        return cleaned


class UserLoginRequest(_EmailNormalizingModel):
    email: EmailStr
    # No strength constraints on login: rejecting a weak password here would
    # confirm that it fails policy, and would lock out accounts created before
    # the policy tightened.
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1, max_length=2048)


class PasswordResetRequest(_EmailNormalizingModel):
    email: EmailStr


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 - a scheme name, not a credential
    expires_in: int | None = None
    refresh_token: str | None = None
    user_id: str
    email: str
    role: UserRole
    full_name: str | None = None


class AuthenticatedUserResponse(BaseModel):
    """Current-user payload. Never includes tokens."""

    user_id: str
    email: str
    role: UserRole
    full_name: str | None = None
    is_active: bool = True
