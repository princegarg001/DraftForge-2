from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user, require_student
from app.models.database.models import UserProfileDB
from app.models.schemas.evaluation import EvaluateDraftRequest, EvaluationResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["Evaluation & Scoring Engine"])
eval_service = EvaluationService()


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_student)])
async def evaluate_draft(
    payload: EvaluateDraftRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Triggers deterministic, rubric-based evaluation on a student draft version.
    """
    return eval_service.evaluate_draft(
        user_id=current_user.id,
        draft_id=payload.draft_id,
        version_number=payload.version_number
    )


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation_details(
    evaluation_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves full evaluation report including traceable evidence and reference citations.
    """
    return eval_service.get_evaluation(evaluation_id=evaluation_id, requester=current_user)