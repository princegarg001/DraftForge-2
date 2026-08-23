from typing import List
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.skill import StudentSkillResponse
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills & Mastery Graph"])
skill_service = SkillService()


@router.get("/my-skills", response_model=List[StudentSkillResponse])
async def get_my_skills(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves the student's personal legal drafting skill proficiencies and confidence levels.
    """
    return skill_service.get_student_skills(user_id=current_user.id)