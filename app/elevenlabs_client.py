"""ElevenLabs API wrapper for voice cloning and text-to-speech.

Three operations:
- clone_voice: upload audio sample, get a cloned voice ID
- generate_name_audio: speak a first name using the cloned voice
- delete_voice: remove a cloned voice when a project is deleted
"""

import logging
import tempfile
from pathlib import Path

from elevenlabs import ElevenLabs

from app.config import get_settings

logger = logging.getLogger(__name__)

VOICE_STABILITY = 0.7
VOICE_SIMILARITY_BOOST = 0.8


def _get_client() -> ElevenLabs:
    """Create and return an ElevenLabs API client."""
    settings = get_settings()
    return ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)


def clone_voice(audio_data: bytes, project_id: int) -> str:
    """Clone a voice from an audio sample and return the voice ID.

    Uses ElevenLabs Instant Voice Cloning. The audio sample should be
    at least 10 seconds long for good results.

    Args:
        audio_data: The audio file content as bytes (WAV format).
        project_id: The project ID, used to name the voice in ElevenLabs.

    Returns:
        The ElevenLabs voice_id string.

    Raises:
        Exception: If the ElevenLabs API call fails.
    """
    client = _get_client()

    # Write audio to a temp file because the SDK expects a file path
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_data)
        temp_path = temp_file.name

    try:
        voice = client.clone(
            name=f"personalvideo_project_{project_id}",
            description="Voice clone for personalized video",
            files=[temp_path],
        )
        logger.info(f"Voice cloned for project {project_id}: voice_id={voice.voice_id}")
        return voice.voice_id
    except Exception:
        logger.exception(f"ElevenLabs voice clone failed for project {project_id}")
        raise
    finally:
        Path(temp_path).unlink(missing_ok=True)


def generate_name_audio(voice_id: str, first_name: str) -> bytes:
    """Generate audio of a first name spoken in the cloned voice.

    Args:
        voice_id: The ElevenLabs voice ID from clone_voice().
        first_name: The name to speak.

    Returns:
        The generated audio as bytes (MP3 format).

    Raises:
        Exception: If the ElevenLabs API call fails.
    """
    settings = get_settings()
    client = _get_client()

    try:
        audio_generator = client.generate(
            text=first_name,
            voice=voice_id,
            model=settings.ELEVENLABS_MODEL,
            voice_settings={
                "stability": VOICE_STABILITY,
                "similarity_boost": VOICE_SIMILARITY_BOOST,
            },
        )

        # The SDK returns a generator of bytes — collect into a single bytes object
        audio_bytes = b"".join(audio_generator)
        logger.info(f"Generated name audio for '{first_name}': {len(audio_bytes)} bytes")
        return audio_bytes
    except Exception:
        logger.exception(f"ElevenLabs TTS failed for name '{first_name}' with voice {voice_id}")
        raise


def delete_voice(voice_id: str) -> None:
    """Delete a cloned voice from ElevenLabs.

    Called when a project is deleted to stay within the voice limit
    and to respect that voice data is personal biometric data.

    Args:
        voice_id: The ElevenLabs voice ID to delete.
    """
    client = _get_client()

    try:
        client.voices.delete(voice_id)
        logger.info(f"Deleted ElevenLabs voice: {voice_id}")
    except Exception:
        logger.exception(f"Failed to delete ElevenLabs voice: {voice_id}")
        raise
