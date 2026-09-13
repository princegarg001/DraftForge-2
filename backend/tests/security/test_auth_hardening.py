"""Regression tests for authentication and authorization hardening.

Each test pins a specific vulnerability that existed before Phase 1.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.constants import UserRole
from app.core.security import (
    _ASYMMETRIC_ALGORITHMS,
    _SUPPORTED_ALGORITHMS,
    _SYMMETRIC_ALGORITHMS,
    normalize_role,
)
from app.models.schemas.auth import UserLoginRequest, UserRegisterRequest

pytestmark = pytest.mark.security


class TestRoleCannotBeSelfAssigned:
    """The registration schema previously carried a `role` field, so anyone
    could POST role="TEACHER" and obtain instructor privileges."""

    def test_register_schema_has_no_role_field(self) -> None:
        assert "role" not in UserRegisterRequest.model_fields

    def test_register_rejects_injected_role(self) -> None:
        # extra="forbid" makes this fail loudly rather than silently ignoring
        # the field, so a client still sending one finds out.
        with pytest.raises(ValidationError) as exc:
            UserRegisterRequest(
                email="student@example.edu",
                password="Str0ng!Passphrase",
                full_name="Test Student",
                role="TEACHER",
            )
        assert "role" in str(exc.value)

    def test_register_rejects_privilege_fields(self) -> None:
        for field, value in (("is_active", False), ("app_metadata", {"role": "ADMIN"})):
            with pytest.raises(ValidationError):
                UserRegisterRequest(
                    email="student@example.edu",
                    password="Str0ng!Passphrase",
                    full_name="Test Student",
                    **{field: value},
                )

    def test_login_schema_has_no_role_field(self) -> None:
        assert "role" not in UserLoginRequest.model_fields


class TestPasswordPolicy:
    @pytest.mark.parametrize(
        "password",
        [
            "short",              # below minimum length
            "alllowercase1234",   # only two character classes
            "password123",        # on the trivial list
            "a" * 200,            # above the upper bound
        ],
    )
    def test_rejects_weak_passwords(self, password: str) -> None:
        with pytest.raises(ValidationError):
            UserRegisterRequest(
                email="student@example.edu", password=password, full_name="Test Student"
            )

    def test_accepts_strong_password(self) -> None:
        request = UserRegisterRequest(
            email="student@example.edu",
            password="Correct-Horse-9Battery",
            full_name="Test Student",
        )
        assert request.password

    def test_upper_bound_exists(self) -> None:
        """Unbounded password input is a hashing-cost denial-of-service vector."""
        assert UserRegisterRequest.model_fields["password"].metadata

    def test_login_does_not_enforce_strength(self) -> None:
        # Enforcing policy at login would confirm a password fails policy, and
        # would lock out accounts predating the rule.
        assert UserLoginRequest(email="a@b.com", password="x").password == "x"


class TestEmailNormalization:
    def test_email_is_lowercased_and_trimmed(self) -> None:
        request = UserLoginRequest(email="  Student@Example.EDU  ", password="x")
        assert request.email == "student@example.edu"


class TestJWTAlgorithmAllowlist:
    """Algorithm confusion: if permitted algorithms came from the token header,
    an attacker could sign with a JWKS public key as an HMAC secret."""

    def test_none_algorithm_is_not_supported(self) -> None:
        assert "NONE" not in _SUPPORTED_ALGORITHMS
        assert "none" not in _SUPPORTED_ALGORITHMS

    def test_algorithm_families_are_disjoint(self) -> None:
        # A key can never be used with an algorithm of the wrong family.
        assert not (_ASYMMETRIC_ALGORITHMS & _SYMMETRIC_ALGORITHMS)

    def test_only_known_strong_algorithms_permitted(self) -> None:
        assert _SUPPORTED_ALGORITHMS <= {
            "RS256", "RS384", "RS512",
            "ES256", "ES384", "ES512",
            "HS256", "HS384", "HS512",
        }


class TestRoleNormalization:
    @pytest.mark.parametrize("value", ["teacher", "TEACHER", " Teacher "])
    def test_accepts_case_and_whitespace_variants(self, value: str) -> None:
        assert normalize_role(value) is UserRole.TEACHER

    @pytest.mark.parametrize("value", [None, "", "SUPERUSER", "root", 42, {"role": "ADMIN"}])
    def test_unknown_values_fall_back_to_least_privilege(self, value: object) -> None:
        assert normalize_role(value) is UserRole.STUDENT
