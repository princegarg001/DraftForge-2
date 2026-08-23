import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.constants import DocumentType, UserRole
from app.models.database.models import UserProfileDB


@pytest.fixture
def mock_student_user() -> UserProfileDB:
    return UserProfileDB(
        id="00000000-0000-0000-0000-000000000001",
        email="student@legaldraft.ai",
        role=UserRole.STUDENT,
        full_name="Arjun Sharma",
        created_at="2026-08-22T00:00:00Z",
        updated_at="2026-08-22T00:00:00Z"
    )


@pytest.fixture
def mock_teacher_user() -> UserProfileDB:
    return UserProfileDB(
        id="00000000-0000-0000-0000-000000000002",
        email="teacher@legaldraft.ai",
        role=UserRole.TEACHER,
        full_name="Prof. Meera Rao",
        created_at="2026-08-22T00:00:00Z",
        updated_at="2026-08-22T00:00:00Z"
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