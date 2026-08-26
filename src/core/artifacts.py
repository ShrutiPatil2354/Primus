"""Optional MinIO storage for multimodal learning artifacts."""
import os
from pathlib import Path


class ArtifactStore:
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "").strip()
        self.bucket = os.getenv("MINIO_BUCKET", "primus-learning").strip()
        self.client = None
        if self.endpoint:
            try:
                from minio import Minio
                self.client = Minio(
                    self.endpoint,
                    access_key=os.getenv("MINIO_ACCESS_KEY", ""),
                    secret_key=os.getenv("MINIO_SECRET_KEY", ""),
                    secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
                )
                self._ensure_bucket()
            except Exception as exc:
                print(f"[PRIMUS] MinIO unavailable ({exc}); artifact storage disabled")
                self.client = None

    @property
    def enabled(self):
        return self.client is not None

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put_file(self, path, object_name=None, content_type=None):
        if not self.enabled:
            return None
        source = Path(path)
        object_name = object_name or source.name
        self.client.fput_object(self.bucket, object_name, str(source), content_type=content_type)
        return f"{self.bucket}/{object_name}"

    def put_bytes(self, data, object_name, content_type="application/octet-stream"):
        if not self.enabled:
            return None
        from io import BytesIO
        self.client.put_object(self.bucket, object_name, BytesIO(data), len(data), content_type=content_type)
        return f"{self.bucket}/{object_name}"


ARTIFACTS = ArtifactStore()
