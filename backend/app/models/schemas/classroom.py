"""Class, roster and invitation schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.constants import UserRole
from app.models.schemas.auth import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH, _validate_password_strength

# A single bulk invite is capped so one request cannot enqueue thousands of
# messages and burn the sending domain's reputation.
MAX_BULK_INVITES = 200


class ClassCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    institution: str | None = Field(default=None, max_length=160)
    academic_term: str | None = Field(default=None, max_length=64)

    @field_validator("name", "institution", "academic_term")
    @classmethod
    def _collapse_whitespace(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else value


class ClassUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    institution: str | None = Field(default=None, max_length=160)
    academic_term: str | None = Field(default=None, max_length=64)
    is_archived: bool | None = None


class ClassResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    teacher_id: str
    name: str
    description: str | None = None
    institution: str | None = None
    academic_term: str | None = None
    join_code: str | None = None
    is_archived: bool = False
    student_count: int = 0
    created_at: Any | None = None


class StudentInvite(BaseModel):
    """One roster entry supplied by the teacher."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def _clean_name(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else None


class BulkInviteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    students: list[StudentInvite] = Field(min_length=1, max_length=MAX_BULK_INVITES)

    @field_validator("students")
    @classmethod
    def _reject_duplicates(cls, students: list[StudentInvite]) -> list[StudentInvite]:
        seen: set[str] = set()
        unique: list[StudentInvite] = []
        for student in students:
            if student.email not in seen:
                seen.add(student.email)
                unique.append(student)
        return unique


class InviteOutcome(BaseModel):
    email: str
    status: str  # invited | already_enrolled | resent | failed
    detail: str | None = None


class BulkInviteResponse(BaseModel):
    class_id: str
    total_submitted: int
    invited: int
    skipped: int
    failed: int
    results: list[InviteOutcome]


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    class_id: str
    student_id: str | None = None
    email: str
    full_name: str | None = None
    status: str
    invited_at: Any | None = None
    joined_at: Any | None = None


class PendingInvitationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    email: str
    status: str
    expires_at: Any | None = None
    send_count: int = 0
    created_at: Any | None = None


class InvitationPreviewResponse(BaseModel):
    """Shown on the acceptance page before a password is set.

    Carries only what the page needs to render. In particular it does not
    confirm whether an account already exists for the address.
    """

    email: str
    class_name: str
    institution: str | None = None
    teacher_name: str | None = None
    full_name: str | None = None
    expires_at: datetime | None = None


class AcceptInvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=16, max_length=256)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("password")
    @classmethod
    def _check_password(cls, value: str) -> str:
        return _validate_password_strength(value)

    @field_validator("full_name")
    @classmethod
    def _clean_name(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else None


class FacultyRegisterRequest(BaseModel):
    """Faculty registration, gated by an institution-issued code.

    Without the gate, the role-escalation hole closed in Phase 1 would simply
    reopen as a self-service teacher signup.
    """

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    full_name: str = Field(min_length=1, max_length=255)
    registration_code: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def _check_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class JoinByCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    join_code: str = Field(min_length=4, max_length=12)

    @field_validator("join_code")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.strip().upper()


class RoleChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: UserRole
    reason: str = Field(min_length=1, max_length=500)
