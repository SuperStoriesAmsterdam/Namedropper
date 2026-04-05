"""File storage — Cloudflare R2 with local fallback.

Uses R2 when credentials are configured, otherwise falls back to
local disk storage under /app/uploads/ so the app still works
during development or if R2 isn't set up yet.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config

from app.config import get_settings

logger = logging.getLogger(__name__)

SIGNED_URL_EXPIRY_SECONDS = 86400  # 24 hours

# Local fallback directory
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _use_r2() -> bool:
    """Check if R2 credentials are configured."""
    settings = get_settings()
    return bool(settings.R2_ENDPOINT_URL and settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY)


def get_r2_client():
    """Create and return an S3-compatible client configured for Cloudflare R2."""
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def upload_file(key: str, data: bytes, content_type: str) -> str:
    """Upload a file to R2 (or local fallback) and return the URL."""
    if _use_r2():
        settings = get_settings()
        client = get_r2_client()
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=f"personalvideo/{key}",
            Body=data,
            ContentType=content_type,
        )
        logger.info(f"Uploaded file to R2: personalvideo/{key}")
        return f"{settings.R2_PUBLIC_URL}/personalvideo/{key}"
    else:
        file_path = UPLOAD_DIR / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        logger.info(f"Saved file locally (R2 not configured): {key} ({len(data)} bytes)")
        return f"/api/files/{key}"


def download_file(key: str) -> bytes:
    """Download a file from R2 or local storage."""
    if _use_r2():
        settings = get_settings()
        client = get_r2_client()
        response = client.get_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=f"personalvideo/{key}",
        )
        return response["Body"].read()
    else:
        file_path = UPLOAD_DIR / key
        return file_path.read_bytes()


def delete_file(key: str) -> None:
    """Delete a file from R2 or local storage."""
    if _use_r2():
        settings = get_settings()
        client = get_r2_client()
        client.delete_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=f"personalvideo/{key}",
        )
        logger.info(f"Deleted file from R2: personalvideo/{key}")
    else:
        file_path = UPLOAD_DIR / key
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted local file: {key}")


def delete_prefix(prefix: str) -> None:
    """Delete all files under a given prefix."""
    if _use_r2():
        settings = get_settings()
        client = get_r2_client()
        full_prefix = f"personalvideo/{prefix}"
        response = client.list_objects_v2(
            Bucket=settings.R2_BUCKET_NAME,
            Prefix=full_prefix,
        )
        objects = response.get("Contents", [])
        if not objects:
            return
        delete_request = {"Objects": [{"Key": obj["Key"]} for obj in objects]}
        client.delete_objects(
            Bucket=settings.R2_BUCKET_NAME,
            Delete=delete_request,
        )
        logger.info(f"Deleted {len(objects)} files from R2 under prefix: {full_prefix}")
    else:
        dir_path = UPLOAD_DIR / prefix
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            logger.info(f"Deleted local directory: {prefix}")


def generate_signed_url(key: str, expiry_seconds: Optional[int] = None) -> str:
    """Generate a signed URL for downloading a file."""
    if _use_r2():
        settings = get_settings()
        client = get_r2_client()
        expiry = expiry_seconds or SIGNED_URL_EXPIRY_SECONDS
        url = client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.R2_BUCKET_NAME,
                "Key": f"personalvideo/{key}",
            },
            ExpiresIn=expiry,
        )
        return url
    else:
        return f"/api/files/{key}"
