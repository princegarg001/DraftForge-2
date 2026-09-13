"""Shared test fixtures.

Test-safe configuration is installed into the environment *before* any ``app``
module is imported. ``app.config`` builds its Settings at import time and
several modules read it at import time in turn, so importing the application
first made the whole suite depend on a populated local .env - and risked
picking up a developer's real credentials.
"""

from __future__ import annotations

import os

_TEST_ENV: dict[str, str] = {
    "ENVIRONMENT": "development",
    "DEBUG": "True",
    "SUPABASE_URL": "https://test-project.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
    "SUPABASE_JWT_SECRET": "test-jwt-secret-value-for-local-tests-only",
    "NEO4J_URI": "neo4j+s://test.databases.neo4j.io",
    "NEO4J_USERNAME": "neo4j",
    "NEO4J_PASSWORD": "test-password",
    "QDRANT_URL": "https://test.qdrant.tech:6333",
    "QDRANT_API_KEY": "test-qdrant-key",
    "GROQ_API_KEY": "test-groq-key",
    "REDIS_URL": "redis://localhost:6379/15",
    "REDIS_REQUIRED": "False",
    "RATE_LIMIT_ENABLED": "False",
    "EMAIL_PROVIDER": "console",
    "ALLOWED_ORIGINS": "",
    "TRUSTED_HOSTS": "*",
    "OTEL_ENABLED": "False",
    "LOG_FORMAT": "console",
}

# setdefault, so an explicitly exported variable (for example pointing CI at a
# disposable Supabase project) still wins.
for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)

import pytest  # noqa: E402

from app.core.constants import UserRole  # noqa: E402
from app.models.database.models import UserProfileDB  # noqa: E402


@pytest.fixture
def mock_student_user() -> UserProfileDB:
    return UserProfileDB(
        id="00000000-0000-0000-0000-000000000001",
        email="student@legaldraft.ai",
        role=UserRole.STUDENT,
        full_name="Arjun Sharma",
        created_at="2026-08-22T00:00:00Z",
        updated_at="2026-08-22T00:00:00Z",
    )


@pytest.fixture
def mock_other_student_user() -> UserProfileDB:
    """A second student, for cross-tenant authorization assertions."""
    return UserProfileDB(
        id="00000000-0000-0000-0000-000000000003",
        email="other.student@legaldraft.ai",
        role=UserRole.STUDENT,
        full_name="Kavya Iyer",
        created_at="2026-08-22T00:00:00Z",
        updated_at="2026-08-22T00:00:00Z",
    )


@pytest.fixture
def mock_teacher_user() -> UserProfileDB:
    return UserProfileDB(
        id="00000000-0000-0000-0000-000000000002",
        email="teacher@legaldraft.ai",
        role=UserRole.TEACHER,
        full_name="Prof. Meera Rao",
        created_at="2026-08-22T00:00:00Z",
        updated_at="2026-08-22T00:00:00Z",
    )


@pytest.fixture
def mock_other_teacher_user() -> UserProfileDB:
    """A second instructor, for cross-instructor authorization assertions."""
    return UserProfileDB(
        id="00000000-0000-0000-0000-000000000004",
        email="other.teacher@legaldraft.ai",
        role=UserRole.TEACHER,
        full_name="Prof. Anil Kapoor",
        created_at="2026-08-22T00:00:00Z",
        updated_at="2026-08-22T00:00:00Z",
    )


@pytest.fixture
def sample_affidavit_text() -> str:
    return """
    AFFIDAVIT OF CHARACTER

    I, Arjun Sharma, son of Shri Rajesh Sharma, aged about 24 years, resident of Flat 102, Green Enclave, New Delhi, do hereby solemnly affirm and state as follows:

    1. That I am a law student and bear good moral character in society.
    2. That no criminal case or FIR is pending against me in any court of law and I am not convicted of any offence.

    VERIFICATION:
    Verified at New Delhi on this 22nd day of August, 2026 that the contents of above affidavit are true to the best of my knowledge and belief and nothing material has been concealed.

    DEPONENT
    """


@pytest.fixture
def sample_employment_text() -> str:
    return """
    EMPLOYMENT AGREEMENT

    This Employment Agreement is entered into between TechCorp India Pvt Ltd having its registered office at Cyber City, Gurugram (Employer) and Priya Nair residing at Indiranagar, Bangalore (Employee).

    1. APPOINTMENT AND DUTIES: The Employer hereby appoints the Employee as Senior Legal Counsel to undertake all assigned duties and responsibilities, subject to a probation period of three months.
    2. COMPENSATION AND REMUNERATION: The Employee shall receive a total remuneration and CTC salary of INR 1,50,000 per month, payable subject to statutory tax deductions.
    3. CONFIDENTIALITY AND IP: The Employee agrees to non-disclosure of confidential information, trade secrets, and proprietary data, and hereby assigns all intellectual property created during employment.
    4. TERMINATION OF EMPLOYMENT: Either party may terminate this agreement by providing 30 days written notice or salary in lieu thereof, save for gross breach warranting summary dismissal.
    5. GOVERNING LAW AND DISPUTE RESOLUTION: This agreement shall be governed by the laws of India. Any dispute shall be referred to arbitration with exclusive jurisdiction vested in the courts at Bangalore.

    IN WITNESS WHEREOF the parties have executed this agreement.
    """
