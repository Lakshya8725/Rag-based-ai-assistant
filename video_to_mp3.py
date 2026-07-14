"""
Step 2 of the RAG pipeline: extract audio from course videos as MP3 files.

Expects video files in `videos/` and writes one MP3 per video to `audios/`.
Filenames are derived from the tutorial number and title in the source filename.
"""

import os
import subprocess

VIDEOS_DIR = "videos"
AUDIOS_DIR = "audios"


def parse_video_filename(filename: str) -> tuple[str, str]:
    """Split '03 - Basic Structure...webm' into ('03', 'Basic Structure...')."""
    tutorial_number = filename.split("-")[0].strip()
    title_part = filename.split("-", 1)[1]
    title = title_part.split("｜")[0].strip()
    return tutorial_number, title


def convert_video_to_mp3(video_path: str, output_path: str) -> None:
    """Extract the audio track from a video file using ffmpeg."""
    subprocess.run(
        ["ffmpeg", "-i", video_path, output_path],
        check=True,
    )


def main() -> None:
    os.makedirs(AUDIOS_DIR, exist_ok=True)

    for filename in os.listdir(VIDEOS_DIR):
        tutorial_number, title = parse_video_filename(filename)
        output_name = f"{tutorial_number}_{title}.mp3"
        output_path = os.path.join(AUDIOS_DIR, output_name)

        print(f"Converting: {filename} -> {output_name}")
        convert_video_to_mp3(
            os.path.join(VIDEOS_DIR, filename),
            output_path,
        )


if __name__ == "__main__":
    main()
