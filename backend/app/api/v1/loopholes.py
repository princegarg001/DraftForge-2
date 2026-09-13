from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.loophole import LoopholeAnalysisResponse
from app.services.loophole_service import LoopholeService

router = APIRouter(prefix="/loopholes", tags=["GraphRAG Loophole & Risk Analysis"])
loophole_service = LoopholeService()


@router.get("/{evaluation_id}", response_model=LoopholeAnalysisResponse)
async def get_loophole_analysis(
    evaluation_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Executes graph-traversal reasoning over Neo4j Aura to detect clause dependency gaps,
    unmitigated risks, and structural loopholes for a completed evaluation.
    """
    return loophole_service.analyze_evaluation_loopholes(
        evaluation_id=evaluation_id, requester=current_user
    )