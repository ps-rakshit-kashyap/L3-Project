import os
import re
import uuid
from pathlib import Path
from typing import Any

from supabase import Client, create_client

from app.core.config import settings
from app.core.logging import logger


class StorageService:
    def __init__(self) -> None:
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self.client: Client | None = None

        secret_key = settings.effective_supabase_key
        if settings.SUPABASE_URL and secret_key:
            try:
                self.client = create_client(
                    settings.SUPABASE_URL, secret_key
                )
                logger.info(f"Supabase Storage initialized for bucket '{self.bucket}'")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Supabase client: {e}. Falling back to local storage."
                )
                self.client = None
        else:
            logger.info("Supabase credentials not configured. Using local fallback file storage.")

        # Local storage fallback directory
        self.local_dir = Path("storage_resumes")
        self.local_dir.mkdir(exist_ok=True, parents=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitizes filename removing harmful characters."""
        clean = re.sub(r"[^\w\.-]", "_", filename)
        return clean[:100]

    def upload_file(
        self,
        file_bytes: bytes,
        original_name: str,
        content_type: str,
        candidate_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Uploads a resume file to Supabase Storage (or local fallback).
        Returns a dict containing file_name, file_path, file_type, and file_url.
        """
        clean_name = self._sanitize_filename(original_name)
        unique_id = uuid.uuid4().hex[:8]
        file_path = f"resumes/{candidate_id}/{unique_id}_{clean_name}"

        # 1. Supabase Storage upload
        if self.client:
            try:
                # Ensure bucket exists and is kept private
                try:
                    self.client.storage.create_bucket(self.bucket, options={"public": False})
                except Exception:
                    # Bucket likely already exists
                    pass

                self.client.storage.from_(self.bucket).upload(
                    path=file_path,
                    file=file_bytes,
                    file_options={"content-type": content_type, "upsert": "true"},
                )

                # Generate signed URL (valid for 7 days) since bucket is private
                try:
                    signed_res = self.client.storage.from_(self.bucket).create_signed_url(
                        file_path, 60 * 60 * 24 * 7
                    )
                    file_url = (
                        signed_res.get("signedURL")
                        or signed_res.get("signedUrl")
                        or self.client.storage.from_(self.bucket).get_public_url(file_path)
                    )
                except Exception:
                    file_url = self.client.storage.from_(self.bucket).get_public_url(file_path)

                return {
                    "file_name": original_name,
                    "file_path": file_path,
                    "file_type": content_type,
                    "file_url": file_url,
                }
            except Exception as exc:
                logger.error(f"Supabase upload failed: {exc}. Storing locally.")

        # 2. Local fallback storage
        local_target = self.local_dir / file_path
        local_target.parent.mkdir(parents=True, exist_ok=True)
        with open(local_target, "wb") as f:
            f.write(file_bytes)

        return {
            "file_name": original_name,
            "file_path": file_path,
            "file_type": content_type,
            "file_url": f"/static/resumes/{file_path}",
        }

    def delete_file(self, file_path: str) -> bool:
        """Deletes a file from Supabase storage or local fallback."""
        deleted = False
        if self.client:
            try:
                self.client.storage.from_(self.bucket).remove([file_path])
                deleted = True
            except Exception as exc:
                logger.warning(f"Supabase delete failed for {file_path}: {exc}")

        local_target = self.local_dir / file_path
        if local_target.exists():
            try:
                os.remove(local_target)
                deleted = True
            except Exception as exc:
                logger.warning(f"Local file delete failed for {file_path}: {exc}")

        return deleted

    def get_file_metadata(self, file_path: str) -> dict[str, Any] | None:
        """Retrieves file metadata from storage."""
        if self.client:
            try:
                files = self.client.storage.from_(self.bucket).list(os.path.dirname(file_path))
                base = os.path.basename(file_path)
                for f in files:
                    if f.get("name") == base:
                        return f
            except Exception as exc:
                logger.warning(f"Failed to fetch metadata from Supabase: {exc}")

        local_target = self.local_dir / file_path
        if local_target.exists():
            stat = local_target.stat()
            return {
                "name": local_target.name,
                "size": stat.st_size,
                "created_at": stat.st_ctime,
            }
    def download_file(self, file_path: str) -> bytes:
        """
        Retrieves raw file bytes from Supabase Storage or local fallback.
        Raises FileNotFoundError if the file cannot be retrieved.
        """
        # 1. Try Supabase Storage
        if self.client:
            try:
                res = self.client.storage.from_(self.bucket).download(file_path)
                if res:
                    return res
            except Exception as exc:
                logger.warning(f"Supabase download failed for '{file_path}': {exc}. Trying local fallback.")

        # 2. Try local fallback storage
        local_target = self.local_dir / file_path
        if local_target.exists():
            with open(local_target, "rb") as f:
                return f.read()

        raise FileNotFoundError(f"File '{file_path}' not found in Supabase Storage or local storage.")


storage_service = StorageService()
