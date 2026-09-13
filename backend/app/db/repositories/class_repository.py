from __future__ import annotations

from typing import Any

from app.db.repositories.base_repository import BaseRepository


class ClassRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="classes")

    def list_for_teacher(self, teacher_id: str, include_archived: bool = False) -> list[dict[str, Any]]:
        query = (
            self.client.table(self.table_name)
            .select("*, class_enrollments(count)")
            .eq("teacher_id", teacher_id)
        )
        if not include_archived:
            query = query.eq("is_archived", False)
        return query.order("created_at", desc=True).execute().data or []

    def get_by_join_code(self, join_code: str) -> dict[str, Any] | None:
        res = (
            self.client.table(self.table_name)
            .select("*")
            .eq("join_code", join_code.strip().upper())
            .eq("is_archived", False)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def list_for_student(self, student_id: str) -> list[dict[str, Any]]:
        res = (
            self.client.table("class_enrollments")
            .select("class_id, status, joined_at, classes(*)")
            .eq("student_id", student_id)
            .eq("status", "ACTIVE")
            .execute()
        )
        return [row["classes"] for row in (res.data or []) if row.get("classes")]


class EnrollmentRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="class_enrollments")

    def list_roster(self, class_id: str) -> list[dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, profiles:student_id(full_name, email, is_active)")
            .eq("class_id", class_id)
            .neq("status", "REMOVED")
            .order("invited_at", desc=False)
            .execute()
        )
        return res.data or []

    def get_by_class_and_email(self, class_id: str, email: str) -> dict[str, Any] | None:
        res = (
            self.client.table(self.table_name)
            .select("*")
            .eq("class_id", class_id)
            .eq("email", email.strip().lower())
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def upsert_invited(
        self, class_id: str, email: str, full_name: str | None, invited_by: str
    ) -> dict[str, Any]:
        """Add a roster entry, or revive a previously removed one.

        Re-adding a student must not orphan their existing coursework, so a
        REMOVED row is reinstated rather than replaced.
        """
        normalized = email.strip().lower()
        existing = self.get_by_class_and_email(class_id, normalized)

        if existing:
            if existing["status"] == "REMOVED":
                updated = self.update(existing["id"], {"status": "INVITED", "invited_by": invited_by})
                return updated or existing
            return existing

        return self.create(
            {
                "class_id": class_id,
                "email": normalized,
                "full_name": full_name,
                "status": "INVITED",
                "invited_by": invited_by,
            }
        )

    def mark_active(self, enrollment_id: str, student_id: str) -> dict[str, Any] | None:
        return self.update(
            enrollment_id,
            {"student_id": student_id, "status": "ACTIVE", "joined_at": "now()"},
        )

    def taught_student_ids(self, teacher_id: str) -> list[str]:
        """Ids of every active student across the classes this teacher runs."""
        classes = (
            self.client.table("classes")
            .select("id")
            .eq("teacher_id", teacher_id)
            .eq("is_archived", False)
            .execute()
        )
        class_ids = [row["id"] for row in (classes.data or [])]
        if not class_ids:
            return []

        students = (
            self.client.table(self.table_name)
            .select("student_id")
            .in_("class_id", class_ids)
            .eq("status", "ACTIVE")
            .execute()
        )
        return sorted({row["student_id"] for row in (students.data or []) if row.get("student_id")})

    def classmate_ids(self, student_id: str) -> list[str]:
        """Ids of students sharing at least one active class with this student.

        Used to scope the leaderboard, which previously ranked every student in
        the database against every other.
        """
        mine = (
            self.client.table(self.table_name)
            .select("class_id")
            .eq("student_id", student_id)
            .eq("status", "ACTIVE")
            .execute()
        )
        class_ids = [row["class_id"] for row in (mine.data or [])]
        if not class_ids:
            return []

        peers = (
            self.client.table(self.table_name)
            .select("student_id")
            .in_("class_id", class_ids)
            .eq("status", "ACTIVE")
            .execute()
        )
        return sorted({row["student_id"] for row in (peers.data or []) if row.get("student_id")})
