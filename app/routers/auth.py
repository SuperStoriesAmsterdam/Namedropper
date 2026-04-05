"""Authentication endpoints: magic link send, verify, and logout."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import (
    create_magic_link_token,
    create_session_token,
    get_current_user,
    verify_magic_link_token,
)
from app.config import get_settings
from app.database import get_db
from app.email import send_magic_link_email
from app.models import User
from app.schemas import AuthVerifyResponse, MagicLinkRequest, MagicLinkResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(body: MagicLinkRequest, db: Session = Depends(get_db)):
    """Send a magic link login email to the given address."""
    settings = get_settings()

    # Create user if they do not exist yet (self-registration)
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        user = User(email=body.email)
        db.add(user)
        db.commit()
        logger.info(f"New user registered: {body.email}")

    token = create_magic_link_token(body.email)
    magic_link_url = f"{settings.APP_BASE_URL}/auth/verify?token={token}"

    try:
        await send_magic_link_email(body.email, magic_link_url)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail={"code": "EMAIL_SEND_FAILED", "message": "Could not send the login email. Please try again."},
        )

    return MagicLinkResponse(message="Magic link sent. Check your email.")


@router.get("/verify", response_model=AuthVerifyResponse)
async def verify_magic_link(token: str, db: Session = Depends(get_db)):
    """Verify a magic link token and return a session token."""
    email = verify_magic_link_token(token)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "USER_NOT_FOUND", "message": "User account not found."},
        )

    session_token = create_session_token(user.id, user.email)
    logger.info(f"User logged in: {email}")

    return AuthVerifyResponse(token=session_token, user_id=user.id, email=user.email)


@router.post("/dev-login", response_model=AuthVerifyResponse)
async def dev_login(body: MagicLinkRequest, db: Session = Depends(get_db)):
    """Dev-only: log in directly without sending an email."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        user = User(email=body.email)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Dev login — new user created: {body.email}")

    session_token = create_session_token(user.id, user.email)
    logger.info(f"Dev login: {body.email}")
    return AuthVerifyResponse(token=session_token, user_id=user.id, email=user.email)


@router.post("/logout", response_model=MagicLinkResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """End the current session.

    Since we use stateless JWTs, logout is handled client-side by discarding the token.
    This endpoint exists for API completeness and future server-side session invalidation.
    """
    logger.info(f"User logged out: {current_user.email}")
    return MagicLinkResponse(message="Logged out successfully.")
