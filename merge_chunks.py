"""
Step 3b (optional): merge small Whisper segments into larger retrieval chunks.

Groups every N consecutive segments from `jsons/` into one chunk and writes
the result to `new_jsons/`. Larger chunks give the LLM more context per hit.
"""

import json
import math
import os

CHUNKS_PER_GROUP = 6
INPUT_DIR = "jsons"
OUTPUT_DIR = "new_jsons"


def merge_chunk_group(chunk_group: list[dict]) -> dict:
    """Combine adjacent segments into a single chunk with merged text."""
    return {
        "number": chunk_group[0]["number"],
        "title": chunk_group[0]["title"],
        "start": chunk_group[0]["start"],
        "end": chunk_group[-1]["end"],
        "text": " ".join(chunk["text"] for chunk in chunk_group),
    }


def merge_file_chunks(chunks: list[dict], group_size: int) -> list[dict]:
    """Split a list of segments into groups and merge each group."""
    num_groups = math.ceil(len(chunks) / group_size)
    merged = []

    for i in range(num_groups):
        start = i * group_size
        end = min((i + 1) * group_size, len(chunks))
        merged.append(merge_chunk_group(chunks[start:end]))

    return merged


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = data.get("chunks", [])
        if not chunks:
            continue

        merged_chunks = merge_file_chunks(chunks, CHUNKS_PER_GROUP)

        output_path = os.path.join(OUTPUT_DIR, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {"text": data.get("text", ""), "chunks": merged_chunks},
                f,
                ensure_ascii=False,
                indent=4,
            )

        print(f"Merged {len(chunks)} -> {len(merged_chunks)} chunks: {filename}")


if __name__ == "__main__":
    main()
