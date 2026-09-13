from __future__ import annotations

from typing import Any

from app.core.constants import UserRole
from app.core.logging import get_logger
from app.db.repositories.base_repository import BaseRepository

logger = get_logger("user_repository")


class UserRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="profiles")

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        response = (
            self.client.table(self.table_name).select("*").eq("email", email.strip().lower()).limit(1).execute()
        )
        if response.data:
            return response.data[0]
        return None

    def ensure_profile(
        self,
        user_id: str,
        email: str,
        role: str,
        full_name: str | None = None,
    ) -> dict[str, Any]:
        """Return the existing profile, or create one with ``role`` if absent.

        Deliberately **not** an upsert. The previous ``upsert_profile`` rewrote
        every column on each call, so a plain login could overwrite the stored
        role with whatever the caller's token happened to carry. Role changes
        must go through ``set_role``, which is admin-gated and audited.
        """
        existing = self.get_by_id(user_id)
        if existing:
            # Keep the display name and email in sync, but never the role.
            patch: dict[str, Any] = {}
            normalized_email = email.strip().lower()
            if normalized_email and existing.get("email") != normalized_email:
                patch["email"] = normalized_email
            if full_name and existing.get("full_name") != full_name:
                patch["full_name"] = full_name
            if patch:
                updated = self.update(user_id, patch)
                return updated or existing
            return existing

        payload = {
            "id": user_id,
            "email": email.strip().lower(),
            "role": role,
            "full_name": full_name,
        }
        created = self.client.table(self.table_name).insert(payload).execute()
        return created.data[0]

    def set_role(self, user_id: str, role: UserRole) -> dict[str, Any] | None:
        """Change a user's role. Callers must be admin-gated and must audit."""
        logger.warning(f"Role change applied: user={user_id} new_role={role.value}")
        return self.update(user_id, {"role": role.value})

    def set_active(self, user_id: str, is_active: bool) -> dict[str, Any] | None:
        return self.update(user_id, {"is_active": is_active})

    def list_by_ids(self, user_ids: list[str]) -> list[dict[str, Any]]:
        if not user_ids:
            return []
        response = self.client.table(self.table_name).select("*").in_("id", user_ids).execute()
        return response.data or []
