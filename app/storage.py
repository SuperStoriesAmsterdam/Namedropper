"""Cloudflare R2 file storage client (S3-compatible).

Handles uploading, downloading, deleting, and generating signed URLs
for video files and generated assets.
"""

import logging
from typing import Optional

import boto3
from botocore.config import Config

from app.config import get_settings

logger = logging.getLogger(__name__)

SIGNED_URL_EXPIRY_SECONDS = 86400  # 24 hours


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
    """Upload a file to R2 and return the public URL.

    Args:
        key: The storage path within the bucket (e.g. "1/3/source.mp4").
        data: The file content as bytes.
        content_type: The MIME type (e.g. "video/mp4").

    Returns:
        The public URL of the uploaded file.
    """
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


def download_file(key: str) -> bytes:
    """Download a file from R2 and return its content as bytes.

    Args:
        key: The storage path within the bucket.

    Returns:
        The file content as bytes.
    """
    settings = get_settings()
    client = get_r2_client()
    response = client.get_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=f"personalvideo/{key}",
    )
    return response["Body"].read()


def delete_file(key: str) -> None:
    """Delete a file from R2.

    Args:
        key: The storage path within the bucket.
    """
    settings = get_settings()
    client = get_r2_client()
    client.delete_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=f"personalvideo/{key}",
    )
    logger.info(f"Deleted file from R2: personalvideo/{key}")


def delete_prefix(prefix: str) -> None:
    """Delete all files under a given prefix in R2.

    Used when deleting a project to remove all associated files.

    Args:
        prefix: The path prefix (e.g. "1/3/" to delete all files for user 1, project 3).
    """
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


def generate_signed_url(key: str, expiry_seconds: Optional[int] = None) -> str:
    """Generate a time-limited signed URL for downloading a file from R2.

    Args:
        key: The storage path within the bucket.
        expiry_seconds: How long the URL is valid. Defaults to 24 hours.

    Returns:
        A signed URL string.
    """
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
