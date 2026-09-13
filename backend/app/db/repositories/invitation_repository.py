from __future__ import annotations

from typing import Any

from app.db.repositories.base_repository import BaseRepository


class InvitationRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="invitations")

    def create_invitation(
        self,
        class_id: str,
        enrollment_id: str,
        email: str,
        token_hash: str,
        expires_at: str,
        issued_by: str,
        intended_role: str = "STUDENT",
    ) -> dict[str, Any]:
        return self.create(
            {
                "class_id": class_id,
                "enrollment_id": enrollment_id,
                "email": email.strip().lower(),
                "token_hash": token_hash,
                "expires_at": expires_at,
                "issued_by": issued_by,
                "intended_role": intended_role,
                "status": "PENDING",
                "send_count": 1,
            }
        )

    def find_by_token_hash(self, token_hash: str) -> dict[str, Any] | None:
        """Look up an invitation by the hash of the presented token.

        The lookup is on the hash, never the raw token, so the stored value is
        useless to anyone who reads the table.
        """
        res = (
            self.client.table(self.table_name)
            .select("*, classes(id, name, teacher_id, institution)")
            .eq("token_hash", token_hash)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def list_pending_for_class(self, class_id: str) -> list[dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("id, email, status, expires_at, send_count, created_at")
            .eq("class_id", class_id)
            .eq("status", "PENDING")
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []

    def revoke_pending_for(self, class_id: str, email: str) -> None:
        """Invalidate any live invitation for this address in this class.

        Called before issuing a replacement so that a resend does not leave the
        previous token usable - otherwise every resend widens the window of
        valid credentials.
        """
        (
            self.client.table(self.table_name)
            .update({"status": "REVOKED", "revoked_at": "now()"})
            .eq("class_id", class_id)
            .eq("email", email.strip().lower())
            .eq("status", "PENDING")
            .execute()
        )

    def revoke(self, invitation_id: str) -> dict[str, Any] | None:
        return self.update(invitation_id, {"status": "REVOKED", "revoked_at": "now()"})

    def mark_accepted(self, invitation_id: str, accepted_by: str) -> dict[str, Any] | None:
        return self.update(
            invitation_id,
            {"status": "ACCEPTED", "accepted_at": "now()", "accepted_by": accepted_by},
        )

    def mark_expired(self, invitation_id: str) -> None:
        self.update(invitation_id, {"status": "EXPIRED"})


class FacultyCodeRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="faculty_registration_codes")

    def find_usable(self, code_hash: str) -> dict[str, Any] | None:
        res = (
            self.client.table(self.table_name)
            .select("*")
            .eq("code_hash", code_hash)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def consume(self, code_id: str, current_use_count: int, max_uses: int) -> bool:
        """Increment the use counter, deactivating the code once exhausted."""
        patch: dict[str, Any] = {"use_count": current_use_count + 1}
        if current_use_count + 1 >= max_uses:
            patch["is_active"] = False
        result = self.update(code_id, patch)
        return result is not None
