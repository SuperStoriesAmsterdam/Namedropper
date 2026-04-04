"""Video file upload endpoint with validation.

Validates file type (by magic bytes, not Content-Type header), file size,
and uploads to Cloudflare R2.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import UploadResponse
from app.storage import upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".webm"}

# Magic bytes for supported video formats
MAGIC_BYTES = {
    b"\x00\x00\x00": "mp4/mov",  # ftyp box (MP4/MOV start with a box size then "ftyp")
    b"\x1a\x45\xdf": "webm",     # EBML header (WebM/Matroska)
}


def _validate_magic_bytes(header: bytes) -> bool:
    """Check if the file header matches a known video format.

    Args:
        header: The first 12 bytes of the uploaded file.

    Returns:
        True if the file matches a known video format.
    """
    # MP4/MOV: bytes 4-7 should be "ftyp"
    if len(header) >= 8 and header[4:8] == b"ftyp":
        return True

    # WebM: starts with EBML header 0x1A45DFA3
    if len(header) >= 4 and header[0:4] == b"\x1a\x45\xdf\xa3":
        return True

    return False


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a source video file to R2 and return the storage URL.

    Validates:
    - File extension is MP4, MOV, or WebM
    - File magic bytes match a known video format
    - File size does not exceed 50 MB
    """
    # Validate file extension
    filename = file.filename or ""
    extension = ""
    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_VIDEO_FORMAT",
                "message": f"Unsupported file format. Accepted formats: MP4, MOV, WebM.",
            },
        )

    # Read the file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "VIDEO_TOO_LARGE",
                "message": "Video file exceeds the 50 MB limit.",
            },
        )

    # Validate magic bytes (don't trust Content-Type header)
    if len(content) < 12 or not _validate_magic_bytes(content[:12]):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_VIDEO_FORMAT",
                "message": "File does not appear to be a valid video. Accepted formats: MP4, MOV, WebM.",
            },
        )

    # Determine content type for R2
    content_type_map = {
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
    }
    content_type = content_type_map.get(extension, "video/mp4")

    # Upload to R2
    storage_key = f"{current_user.id}/source{extension}"
    try:
        url = upload_file(storage_key, content, content_type)
    except Exception:
        logger.exception(f"Failed to upload video to R2 for user {current_user.id}")
        raise HTTPException(
            status_code=502,
            detail={
                "code": "UPLOAD_FAILED",
                "message": "Failed to upload the video. Please try again.",
            },
        )

    logger.info(f"User {current_user.id} uploaded video: {len(content)} bytes")

    return UploadResponse(url=url, size_bytes=len(content), content_type=content_type)
