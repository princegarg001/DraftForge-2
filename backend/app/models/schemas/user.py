from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr
from app.core.constants import UserRole


class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    full_name: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None