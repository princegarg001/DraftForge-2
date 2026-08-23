from typing import Any, Dict, List, Optional
from app.core.constants import DocumentType
from app.db.repositories.base_repository import BaseRepository


class QuizRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="quizzes")

    def list_quizzes(self, doc_type: Optional[DocumentType] = None) -> List[Dict[str, Any]]:
        query = self.client.table(self.table_name).select("*, skills(*)")
        if doc_type:
            query = query.eq("document_type", doc_type.value)
        res = query.execute()
        return res.data or []

    def get_quiz_with_questions(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, quiz_questions(*), skills(*)")
            .eq("id", quiz_id)
            .execute()
        )
        return res.data[0] if res.data else None

    def create_question(
        self,
        quiz_id: str,
        question_text: str,
        options: List[Dict[str, str]],
        correct_option: str,
        explanation: str,
        order_index: int = 1
    ) -> Dict[str, Any]:
        payload = {
            "quiz_id": quiz_id,
            "question_text": question_text,
            "options": options,
            "correct_option": correct_option,
            "explanation": explanation,
            "order_index": order_index
        }
        res = self.client.table("quiz_questions").insert(payload).execute()
        return res.data[0] if res.data else {}

    def log_quiz_attempt(
        self,
        quiz_id: str,
        user_id: str,
        answers: Dict[str, str],
        score: float,
        total_questions: int,
        passed: bool
    ) -> Dict[str, Any]:
        payload = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "answers": answers,
            "score": score,
            "total_questions": total_questions,
            "passed": passed
        }
        res = self.client.table("quiz_attempts").insert(payload).execute()
        return res.data[0] if res.data else {}

    def get_user_attempts(self, user_id: str) -> List[Dict[str, Any]]:
        res = (
            self.client.table("quiz_attempts")
            .select("*, quizzes(*)")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []