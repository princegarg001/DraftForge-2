from typing import Any, Dict, List, Optional
from app.core.constants import DocumentType
from app.core.exceptions import NotFoundError
from app.db.repositories.quiz_repository import QuizRepository
from app.models.schemas.quiz import (
    QuizAttemptResponse,
    QuizOption,
    QuizQuestionResponse,
    QuizResponse,
    SubmitQuizAttemptRequest,
)


class QuizService:
    def __init__(self):
        self.repo = QuizRepository()

    def list_quizzes(self, doc_type: Optional[DocumentType] = None) -> List[QuizResponse]:
        records = self.repo.list_quizzes(doc_type)
        return [QuizResponse(**r, questions=[]) for r in records]

    def get_quiz(self, quiz_id: str) -> QuizResponse:
        record = self.repo.get_quiz_with_questions(quiz_id)
        if not record:
            raise NotFoundError("Quiz", quiz_id)

        questions = []
        for q in record.get("quiz_questions", []):
            opts = []
            for idx, o in enumerate(q.get("options") or []):
                if isinstance(o, dict):
                    opts.append(QuizOption(key=o.get("key", chr(65 + idx)), text=o.get("text", str(o))))
                elif isinstance(o, str):
                    opts.append(QuizOption(key=chr(65 + idx), text=o))
                else:
                    opts.append(QuizOption(key=chr(65 + idx), text=str(o)))

            questions.append(
                QuizQuestionResponse(
                    id=q["id"],
                    quiz_id=q["quiz_id"],
                    question_text=q["question_text"],
                    options=opts,
                    order_index=q.get("order_index", 1)
                )
            )

        return QuizResponse(
            id=record["id"],
            skill_id=record.get("skill_id"),
            document_type=record["document_type"],
            title=record["title"],
            description=record.get("description"),
            difficulty=record["difficulty"],
            created_at=record["created_at"],
            questions=questions
        )

    def submit_quiz(self, user_id: str, payload: SubmitQuizAttemptRequest) -> QuizAttemptResponse:
        quiz_data = self.repo.get_quiz_with_questions(payload.quiz_id)
        if not quiz_data:
            raise NotFoundError("Quiz", payload.quiz_id)

        questions = quiz_data.get("quiz_questions", [])
        total = len(questions)
        correct_count = 0
        breakdown: List[Dict[str, Any]] = []

        for q in questions:
            qid = q["id"]
            correct = q["correct_option"]
            user_ans = payload.answers.get(qid)
            is_correct = user_ans == correct
            if is_correct:
                correct_count += 1

            breakdown.append({
                "question_id": qid,
                "user_answer": user_ans,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

        score = round((correct_count / max(total, 1)) * 100.0, 2)
        passed = score >= 70.0

        attempt = self.repo.log_quiz_attempt(
            quiz_id=payload.quiz_id,
            user_id=user_id,
            answers=payload.answers,
            score=score,
            total_questions=total,
            passed=passed
        )

        return QuizAttemptResponse(
            id=attempt["id"],
            quiz_id=attempt["quiz_id"],
            user_id=attempt["user_id"],
            score=attempt["score"],
            total_questions=attempt["total_questions"],
            passed=attempt["passed"],
            breakdown=breakdown,
            created_at=attempt["created_at"]
        )