"""Application settings loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration for the Personal Video application.

    Every required variable must be set in the environment or .env file.
    Missing values will cause a startup error with a clear message.
    """

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Cloudflare R2
    R2_ENDPOINT_URL: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str = "personalvideo"
    R2_PUBLIC_URL: str

    # Email (Resend)
    RESEND_API_KEY: str
    EMAIL_FROM: str = "noreply@superstories.nl"

    # Auth
    APP_SECRET_KEY: str
    APP_BASE_URL: str

    # ElevenLabs
    ELEVENLABS_API_KEY: str
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def get_settings() -> Settings:
    """Return the application settings singleton.

    Raises a clear error if any required environment variable is missing.
    """
    return Settings()
