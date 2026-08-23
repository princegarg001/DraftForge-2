from fastapi import APIRouter
from app.api.v1 import (
    ai,
    analytics,
    assignments,
    auth,
    chat,
    conversations,
    documents,
    drafts,
    evaluations,
    health,
    leaderboard,
    loopholes,
    progress,
    quizzes,
    rag,
    roadmap,
    skills,
    submissions,
    teachers,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(drafts.router)
api_v1_router.include_router(rag.router)
api_v1_router.include_router(evaluations.router)
api_v1_router.include_router(loopholes.router)
api_v1_router.include_router(ai.router)
api_v1_router.include_router(conversations.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(skills.router)
api_v1_router.include_router(roadmap.router)
api_v1_router.include_router(quizzes.router)
api_v1_router.include_router(progress.router)
api_v1_router.include_router(leaderboard.router)
api_v1_router.include_router(teachers.router)
api_v1_router.include_router(assignments.router)
api_v1_router.include_router(submissions.router)
api_v1_router.include_router(analytics.router)