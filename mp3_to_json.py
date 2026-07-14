"""
Step 3 of the RAG pipeline: transcribe Hindi course audio to English JSON.

Uses OpenAI Whisper to translate each MP3 in `audios/` and saves one JSON
file per audio in `jsons/`, with timestamped subtitle chunks.
"""

import json
import os

import whisper

AUDIOS_DIR = "audios"
JSONS_DIR = "jsons"
WHISPER_MODEL = "large-v2"
SOURCE_LANGUAGE = "hi"  # Hindi audio from the Sigma course


def parse_audio_filename(filename: str) -> tuple[str, str]:
    """Split '03 _ Basic Structure....mp3' into number and title."""
    number = filename.split("_")[0]
    title = filename.split("_", 1)[1].replace(".mp3", "")
    return number, title


def segments_to_chunks(segments, number: str, title: str) -> list[dict]:
    """Convert Whisper segments into our chunk schema."""
    return [
        {
            "number": number,
            "title": title,
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"],
        }
        for segment in segments
    ]


def main() -> None:
    model = whisper.load_model(WHISPER_MODEL)
    os.makedirs(JSONS_DIR, exist_ok=True)

    for audio_file in os.listdir(AUDIOS_DIR):
        if not audio_file.endswith(".mp3"):
            continue

        number, title = parse_audio_filename(audio_file)
        audio_path = os.path.join(AUDIOS_DIR, audio_file)

        print(f"Transcribing: {audio_file}")
        result = model.transcribe(
            audio=audio_path,
            language=SOURCE_LANGUAGE,
            task="translate",  # Hindi -> English
            word_timestamps=False,
        )

        output = {
            "chunks": segments_to_chunks(result["segments"], number, title),
            "full_text": result["text"],
        }

        json_path = os.path.join(JSONS_DIR, f"{audio_file}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
