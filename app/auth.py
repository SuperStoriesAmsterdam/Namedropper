"""Magic link authentication: token generation, verification, and session management.

Flow:
1. User requests a magic link → we generate a short-lived JWT and email it
2. User clicks the link → we verify the JWT, mark it as used, and issue a session token
3. Session token is sent as a Bearer token on subsequent requests

Magic link tokens expire after 15 minutes and are single-use.
Session tokens expire after 7 days.
"""

import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User

logger = logging.getLogger(__name__)

MAGIC_LINK_EXPIRY_MINUTES = 15
SESSION_TOKEN_EXPIRY_DAYS = 7

security = HTTPBearer()

# Track used magic link tokens in memory.
# In production with multiple workers, this should be Redis or a database column.
# For V1 with a single worker, this is sufficient.
_used_magic_tokens: set[str] = set()


def create_magic_link_token(email: str) -> str:
    """Generate a short-lived JWT for a magic link login.

    Args:
        email: The email address to create the token for.

    Returns:
        A signed JWT string valid for 15 minutes.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "type": "magic_link",
        "iat": now,
        "exp": now + timedelta(minutes=MAGIC_LINK_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm="HS256")


def verify_magic_link_token(token: str) -> str:
    """Verify a magic link token and return the email address.

    Checks that the token is valid, not expired, and has not been used before.
    Marks the token as used after successful verification.

    Args:
        token: The JWT token from the magic link URL.

    Returns:
        The email address from the token.

    Raises:
        HTTPException: If the token is invalid, expired, or already used.
    """
    if token in _used_magic_tokens:
        raise HTTPException(
            status_code=400,
            detail={"code": "MAGIC_LINK_USED", "message": "This magic link has already been used."},
        )

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail={"code": "MAGIC_LINK_EXPIRED", "message": "This magic link has expired. Please request a new one."},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail={"code": "MAGIC_LINK_INVALID", "message": "This magic link is invalid."},
        )

    if payload.get("type") != "magic_link":
        raise HTTPException(
            status_code=400,
            detail={"code": "MAGIC_LINK_INVALID", "message": "This magic link is invalid."},
        )

    _used_magic_tokens.add(token)
    return payload["sub"]


def create_session_token(user_id: int, email: str) -> str:
    """Generate a session token after successful magic link verification.

    Args:
        user_id: The database ID of the authenticated user.
        email: The user's email address.

    Returns:
        A signed JWT string valid for 7 days.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "session",
        "iat": now,
        "exp": now + timedelta(days=SESSION_TOKEN_EXPIRY_DAYS),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that extracts and validates the current user from a Bearer token.

    Use as: current_user = Depends(get_current_user)

    Args:
        credentials: The Bearer token from the Authorization header.
        db: The database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: If the token is invalid, expired, or the user does not exist.
    """
    settings = get_settings()
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={"code": "SESSION_EXPIRED", "message": "Your session has expired. Please log in again."},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_TOKEN", "message": "Invalid authentication token."},
        )

    if payload.get("type") != "session":
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_TOKEN", "message": "Invalid authentication token."},
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "USER_NOT_FOUND", "message": "User account not found."},
        )

    return user
