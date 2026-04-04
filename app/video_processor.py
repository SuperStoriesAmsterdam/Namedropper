"""FFmpeg video and audio processing operations.

Three operations:
- extract_audio: pull the audio track out of a video file
- splice_name: insert a name audio clip at the pause point in the source video
- get_duration: get the duration of a video file in seconds

Uses the ffmpeg-python wrapper for a clean Python API over FFmpeg CLI.
FFmpeg must be installed on the system (see Dockerfile and PRD section 12).
"""

import logging
import tempfile
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


def extract_audio(video_data: bytes) -> bytes:
    """Extract the audio track from a video file as WAV.

    Args:
        video_data: The video file content as bytes.

    Returns:
        The extracted audio as WAV bytes.

    Raises:
        RuntimeError: If FFmpeg fails or the video has no audio track.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_file.write(video_data)
        video_path = video_file.name

    audio_path = video_path.replace(".mp4", "_audio.wav")

    try:
        ffmpeg.input(video_path).output(
            audio_path,
            vn=None,
            acodec="pcm_s16le",
        ).overwrite_output().run(quiet=True)

        audio_data = Path(audio_path).read_bytes()

        if len(audio_data) < 1000:
            raise RuntimeError("Video appears to have no audio track.")

        logger.info(f"Extracted audio: {len(audio_data)} bytes")
        return audio_data
    except ffmpeg.Error as error:
        logger.exception("FFmpeg audio extraction failed")
        raise RuntimeError(f"FFmpeg audio extraction failed: {error.stderr}") from error
    finally:
        Path(video_path).unlink(missing_ok=True)
        Path(audio_path).unlink(missing_ok=True)


def get_duration(video_data: bytes) -> float:
    """Get the duration of a video file in seconds.

    Args:
        video_data: The video file content as bytes.

    Returns:
        The duration in seconds as a float.

    Raises:
        RuntimeError: If FFmpeg cannot probe the file.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_file.write(video_data)
        video_path = video_file.name

    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe["format"]["duration"])
        logger.info(f"Video duration: {duration:.1f} seconds")
        return duration
    except (ffmpeg.Error, KeyError) as error:
        logger.exception("FFmpeg probe failed")
        raise RuntimeError(f"Could not determine video duration: {error}") from error
    finally:
        Path(video_path).unlink(missing_ok=True)


def splice_name(source_video_data: bytes, name_audio_data: bytes, pause_timestamp_ms: int) -> bytes:
    """Insert a name audio clip at the pause point in the source video.

    Steps:
    1. Extract audio from the source video
    2. Split the audio at the pause timestamp
    3. Concatenate: before_pause + name_audio + after_pause
    4. Merge the new audio back onto the original video track
    5. Return the final MP4 as bytes

    Args:
        source_video_data: The original video file as bytes.
        name_audio_data: The generated name audio as bytes (MP3 from ElevenLabs).
        pause_timestamp_ms: Where to insert the name, in milliseconds.

    Returns:
        The final personalized video as MP4 bytes.

    Raises:
        RuntimeError: If any FFmpeg step fails.
    """
    pause_seconds = pause_timestamp_ms / 1000.0

    # Write all inputs to temp files
    with tempfile.TemporaryDirectory() as temp_dir:
        source_video_path = Path(temp_dir) / "source.mp4"
        name_audio_path = Path(temp_dir) / "name.mp3"
        before_path = Path(temp_dir) / "before.wav"
        after_path = Path(temp_dir) / "after.wav"
        combined_audio_path = Path(temp_dir) / "combined.wav"
        output_path = Path(temp_dir) / "output.mp4"

        source_video_path.write_bytes(source_video_data)
        name_audio_path.write_bytes(name_audio_data)

        try:
            # Step 1: Extract audio before the pause point
            ffmpeg.input(str(source_video_path)).output(
                str(before_path),
                vn=None,
                acodec="pcm_s16le",
                t=pause_seconds,
            ).overwrite_output().run(quiet=True)

            # Step 2: Extract audio after the pause point
            ffmpeg.input(str(source_video_path)).output(
                str(after_path),
                vn=None,
                acodec="pcm_s16le",
                ss=pause_seconds,
            ).overwrite_output().run(quiet=True)

            # Step 3: Concatenate before + name + after using the concat filter
            before_input = ffmpeg.input(str(before_path))
            name_input = ffmpeg.input(str(name_audio_path))
            after_input = ffmpeg.input(str(after_path))

            (
                ffmpeg.concat(
                    before_input.audio,
                    name_input.audio,
                    after_input.audio,
                    v=0,
                    a=1,
                )
                .output(str(combined_audio_path), acodec="pcm_s16le")
                .overwrite_output()
                .run(quiet=True)
            )

            # Step 4: Merge new audio back onto the original video track
            video_input = ffmpeg.input(str(source_video_path))
            audio_input = ffmpeg.input(str(combined_audio_path))

            (
                ffmpeg.output(
                    video_input.video,
                    audio_input.audio,
                    str(output_path),
                    vcodec="copy",
                    acodec="aac",
                )
                .overwrite_output()
                .run(quiet=True)
            )

            output_data = output_path.read_bytes()
            logger.info(f"Spliced video created: {len(output_data)} bytes")
            return output_data

        except ffmpeg.Error as error:
            stderr_output = error.stderr.decode() if error.stderr else "unknown error"
            logger.exception(f"FFmpeg splice failed: {stderr_output}")
            raise RuntimeError(f"FFmpeg video splice failed: {stderr_output}") from error
