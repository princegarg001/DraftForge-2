import difflib
from typing import List, Optional
from fastapi import UploadFile
from app.core.constants import DocumentType
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.file_security import validate_uploaded_file
from app.db.repositories.draft_repository import DraftRepository
from app.models.schemas.draft import DraftCreateRequest, DraftResponse, DraftVersionResponse, VersionCompareResponse
from app.services.parsing.classifier import DocumentClassifier
from app.services.parsing.parser_factory import ParserFactory
from app.services.storage_service import StorageService
from app.utils.file_utils import compute_sha256


class DraftService:
    def __init__(self):
        self.repo = DraftRepository()
        self.storage_service = StorageService()

    def create_draft(self, user_id: str, payload: DraftCreateRequest) -> DraftResponse:
        # Determine document type
        if payload.document_type:
            doc_type = payload.document_type
        else:
            doc_type, _ = DocumentClassifier.classify(payload.raw_content)

        draft_record = self.repo.create({
            "user_id": user_id,
            "document_type": doc_type.value,
            "title": payload.title,
            "status": "DRAFT",
        })

        version_record = self.repo.create_version(
            draft_id=draft_record["id"],
            version_number=1,
            content=payload.raw_content,
        )

        draft_record["draft_versions"] = [version_record]
        return self._build_draft_response(draft_record)

    async def create_draft_from_file(self, user_id: str, file: UploadFile, title: Optional[str] = None) -> DraftResponse:
        content = await file.read()
        validate_uploaded_file(file, content)

        file_hash = compute_sha256(content)
        parser = ParserFactory.get_parser_for_file(file.filename)
        parsed_doc = parser.parse(content, file.filename)

        doc_type, _ = DocumentClassifier.classify(parsed_doc.raw_text)

        draft_record = self.repo.create({
            "user_id": user_id,
            "document_type": doc_type.value,
            "title": title or file.filename,
            "status": "DRAFT",
        })

        storage_path = self.storage_service.store_student_draft(
            user_id=user_id,
            draft_id=draft_record["id"],
            version=1,
            filename=file.filename,
            content=content,
            content_type=file.content_type or "application/octet-stream"
        )

        version_record = self.repo.create_version(
            draft_id=draft_record["id"],
            version_number=1,
            content=parsed_doc.raw_text,
            storage_path=storage_path,
            file_hash=file_hash
        )

        draft_record["draft_versions"] = [version_record]
        return self._build_draft_response(draft_record)

    def add_draft_version(self, user_id: str, draft_id: str, new_content: str) -> DraftVersionResponse:
        draft = self.repo.get_by_id(draft_id)
        if not draft:
            raise NotFoundError("Draft", draft_id)
        if draft["user_id"] != user_id:
            raise PermissionDeniedError("Cannot modify another student's draft.")

        latest_v = self.repo.get_latest_version(draft_id)
        next_version_num = (latest_v["version_number"] + 1) if latest_v else 1

        v_record = self.repo.create_version(
            draft_id=draft_id,
            version_number=next_version_num,
            content=new_content
        )
        return DraftVersionResponse(**v_record)

    def get_user_drafts(self, user_id: str) -> List[DraftResponse]:
        drafts = self.repo.list_user_drafts(user_id)
        return [self._build_draft_response(d) for d in drafts]

    def get_draft(self, draft_id: str, user_id: str) -> DraftResponse:
        draft = self.repo.get_draft_with_versions(draft_id, user_id)
        if not draft:
            raise NotFoundError("Draft", draft_id)
        return self._build_draft_response(draft)

    def compare_versions(self, draft_id: str, user_id: str, v1_num: int, v2_num: int) -> VersionCompareResponse:
        draft = self.repo.get_draft_with_versions(draft_id, user_id)
        if not draft:
            raise NotFoundError("Draft", draft_id)

        v1 = self.repo.get_version_by_number(draft_id, v1_num)
        v2 = self.repo.get_version_by_number(draft_id, v2_num)

        if not v1 or not v2:
            raise NotFoundError("DraftVersion", f"v{v1_num} or v{v2_num}")

        lines1 = v1["raw_content"].splitlines(keepends=True)
        lines2 = v2["raw_content"].splitlines(keepends=True)

        diff = list(difflib.unified_diff(lines1, lines2, fromfile=f"v{v1_num}", tofile=f"v{v2_num}"))
        additions = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        deletions = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

        return VersionCompareResponse(
            draft_id=draft_id,
            v1_number=v1_num,
            v2_number=v2_num,
            additions=additions,
            deletions=deletions,
            diff_summary="".join(diff)
        )

    def _build_draft_response(self, record: dict) -> DraftResponse:
        versions_raw = record.get("draft_versions") or []
        versions = [DraftVersionResponse(**v) for v in versions_raw]
        return DraftResponse(
            id=record["id"],
            user_id=record["user_id"],
            document_type=record["document_type"],
            title=record["title"],
            status=record["status"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
            versions=versions
        )