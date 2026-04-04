"""Email sending via the Resend API.

Used for magic link login emails and batch completion notifications.
"""

import logging

import resend

from app.config import get_settings

logger = logging.getLogger(__name__)


def _configure_resend():
    """Set the Resend API key from application settings."""
    settings = get_settings()
    resend.api_key = settings.RESEND_API_KEY


async def send_magic_link_email(email: str, magic_link_url: str) -> None:
    """Send a magic link login email to the given address.

    Args:
        email: The recipient's email address.
        magic_link_url: The full URL the user clicks to log in.
    """
    _configure_resend()

    try:
        resend.Emails.send({
            "from": get_settings().EMAIL_FROM,
            "to": email,
            "subject": "Your Namedropper login link",
            "html": (
                f"<p>Click the link below to log in to Namedropper:</p>"
                f'<p><a href="{magic_link_url}">Log in to Namedropper</a></p>'
                f"<p>This link expires in 15 minutes and can only be used once.</p>"
                f"<p>If you did not request this, you can ignore this email.</p>"
            ),
        })
        logger.info(f"Magic link email sent to {email}")
    except Exception:
        logger.exception(f"Failed to send magic link email to {email}")
        raise


async def send_batch_complete_email(email: str, project_title: str, total_videos: int, project_url: str) -> None:
    """Send a notification email when all videos in a project are finished.

    Args:
        email: The recipient's email address.
        project_title: The name of the completed project.
        total_videos: How many personalized videos were generated.
        project_url: The URL to view and download the completed videos.
    """
    _configure_resend()

    display_title = project_title or "Your project"

    try:
        resend.Emails.send({
            "from": get_settings().EMAIL_FROM,
            "to": email,
            "subject": f"Your {total_videos} personalized videos are ready",
            "html": (
                f"<p>{display_title} is complete.</p>"
                f"<p>{total_videos} personalized videos have been generated and are ready for download.</p>"
                f'<p><a href="{project_url}">View and download your videos</a></p>'
            ),
        })
        logger.info(f"Batch complete email sent to {email} for project '{display_title}'")
    except Exception:
        logger.exception(f"Failed to send batch complete email to {email}")
        raise
