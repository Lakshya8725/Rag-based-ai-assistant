"""
Step 4 of the RAG pipeline: embed raw Whisper JSON chunks via Ollama.

Reads segment-level JSON from `jsons/`, calls the bge-m3 embedding model,
and saves a pandas DataFrame to `embeddings.joblib` for retrieval.
"""

import json
import os

import joblib
import pandas as pd
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "bge-m3"
BATCH_SIZE = 8

INPUT_DIR = "jsons"
OUTPUT_FILE = "embeddings.joblib"


def create_embedding(texts: list[str]) -> list[list[float]]:
    """Request embeddings for a batch of texts from the local Ollama server."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "input": texts},
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()

    if "embeddings" in data and isinstance(data["embeddings"], list):
        return data["embeddings"]

    print("Unexpected Ollama response:", data)
    return []


def batch_items(items: list, size: int):
    """Yield (start_index, slice) pairs for fixed-size batches."""
    for i in range(0, len(items), size):
        yield i, items[i : i + size]


def load_valid_chunks(content: dict) -> list[dict]:
    """Keep only chunks that have non-empty text."""
    return [
        chunk
        for chunk in content.get("chunks", [])
        if isinstance(chunk, dict) and chunk.get("text", "").strip()
    ]


def main() -> None:
    records = []
    chunk_id = 0

    for file_name in os.listdir(INPUT_DIR):
        if not file_name.endswith(".json"):
            continue

        print(f"\nProcessing: {file_name}")
        file_path = os.path.join(INPUT_DIR, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        valid_chunks = load_valid_chunks(content)
        if not valid_chunks:
            print("No valid chunks found, skipping.")
            continue

        texts = [chunk["text"] for chunk in valid_chunks]

        for start_idx, text_batch in batch_items(texts, BATCH_SIZE):
            print(f"Embedding batch of {len(text_batch)} texts...")
            embeddings = create_embedding(text_batch)

            if not embeddings:
                print("Empty embeddings returned, skipping batch.")
                continue

            for chunk, embedding in zip(
                valid_chunks[start_idx : start_idx + len(embeddings)],
                embeddings,
            ):
                chunk["chunk_id"] = chunk_id
                chunk["embedding"] = embedding
                records.append(chunk)
                chunk_id += 1

    print(f"\nDone. Total embedded chunks: {len(records)}")

    df = pd.DataFrame.from_records(records)
    joblib.dump(df, OUTPUT_FILE)
    print(f"Saved embeddings to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
