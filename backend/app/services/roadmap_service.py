from typing import Optional
from app.db.repositories.roadmap_repository import RoadmapRepository
from app.models.schemas.roadmap import RoadmapItemResponse, RoadmapResponse
from app.pipelines.roadmap_pipeline import RoadmapPipeline


class RoadmapService:
    def __init__(self):
        self.repo = RoadmapRepository()
        self.pipeline = RoadmapPipeline()

    def get_active_roadmap(self, user_id: str) -> Optional[RoadmapResponse]:
        record = self.repo.get_active_roadmap(user_id)
        if not record:
            return None

        items = [RoadmapItemResponse(**i) for i in record.get("roadmap_items", [])]
        return RoadmapResponse(
            id=record["id"],
            user_id=record["user_id"],
            title=record["title"],
            is_active=record["is_active"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
            roadmap_items=items
        )

    async def generate_roadmap(self, user_id: str) -> RoadmapResponse:
        record = await self.pipeline.generate_personalized_roadmap(user_id)
        items = [RoadmapItemResponse(**i) for i in record.get("roadmap_items", [])]
        return RoadmapResponse(
            id=record["id"],
            user_id=record["user_id"],
            title=record["title"],
            is_active=record["is_active"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
            roadmap_items=items
        )

    def complete_item(self, item_id: str) -> RoadmapItemResponse:
        res = self.repo.mark_item_completed(item_id)
        return RoadmapItemResponse(**res)