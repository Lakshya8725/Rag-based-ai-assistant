"""
Core RAG engine: embed query, retrieve chunks, generate answer via Ollama.
Shared by the CLI (process_incoming.py) and the FastAPI server (api.py).
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", "new_embeddings.joblib")
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

_df_cache: pd.DataFrame | None = None


class RagEngineError(Exception):
    """Base error for RAG pipeline failures."""


class OllamaUnavailableError(RagEngineError):
    """Raised when the local Ollama server cannot be reached."""


class EmbeddingsNotFoundError(RagEngineError):
    """Raised when the embeddings index file is missing."""


def seconds_to_mmss(seconds: float) -> str:
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    return f"{minutes}:{secs:02d}"


def load_embeddings() -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None:
        return _df_cache

    path = Path(EMBEDDINGS_FILE)
    if not path.exists():
        raise EmbeddingsNotFoundError(
            f"Embeddings file not found: {path.resolve()}. "
            "Run preprocess_new_json.py after indexing your course data."
        )

    _df_cache = joblib.load(path)
    return _df_cache


def create_embedding(texts: list[str]) -> list[list[float]]:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=300,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise OllamaUnavailableError(
            f"Could not contact Ollama at {OLLAMA_BASE_URL}. "
            "Make sure Ollama is running with bge-m3 pulled."
        ) from exc

    if "embeddings" in data and isinstance(data["embeddings"], list):
        return data["embeddings"]

    raise RagEngineError(f"Unexpected Ollama embed response: {data}")


def run_inference(prompt: str, model: str = LLM_MODEL) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as exc:
        raise OllamaUnavailableError(
            f"Could not contact Ollama at {OLLAMA_BASE_URL}. "
            "Make sure Ollama is running with llama3.2 pulled."
        ) from exc


def retrieve_relevant_chunks(
    df: pd.DataFrame,
    question_embedding: list[float],
    top_k: int,
) -> pd.DataFrame:
    similarities = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding],
    ).flatten()

    best_indices = similarities.argsort()[::-1][:top_k]

    results = df.loc[best_indices].copy()
    results["score"] = [float(similarities[i]) for i in best_indices]
    results = results.sort_values("start")
    results["start_mmss"] = results["start"].apply(seconds_to_mmss)
    results["end_mmss"] = results["end"].apply(seconds_to_mmss)

    return results


def build_prompt(query: str, context_df: pd.DataFrame) -> str:
    context_json = context_df[
        ["title", "number", "start_mmss", "end_mmss", "text"]
    ].to_json(orient="records")

    return f"""\
I am teaching web development using the Sigma Web Development Course.

Below are subtitle chunks containing:
video title, video number, start time, end time, and text.

{context_json}

--------------------------------------------------------------

User question:
"{query}"

Instructions:
- Answer like a human teacher
- Clearly mention WHICH video to watch
- Mention WHAT topic is taught
- Mention the EXACT timestamp (mm:ss format)
- Suggest ONLY the most relevant video
- Do NOT use raw seconds
- Do NOT add unnecessary words

If the question is unrelated to the course, clearly say that you can only answer questions related to the course.
"""


def chunks_to_sources(context_df: pd.DataFrame) -> list[dict]:
    sources = []
    for _, row in context_df.iterrows():
        sources.append(
            {
                "video_number": str(row["number"]).strip(),
                "title": str(row["title"]).strip(),
                "start": row["start_mmss"],
                "end": row["end_mmss"],
                "score": round(float(row.get("score", 0)), 3),
                "excerpt": str(row["text"]).strip()[:200],
            }
        )
    return sources


def ask_question(query: str, top_k: int = TOP_K_RESULTS) -> dict:
    query = query.strip()
    if not query:
        raise RagEngineError("Question cannot be empty.")

    df = load_embeddings()
    question_embedding = create_embedding([query])[0]
    relevant_chunks = retrieve_relevant_chunks(df, question_embedding, top_k)
    prompt = build_prompt(query, relevant_chunks)
    answer = run_inference(prompt)

    return {
        "question": query,
        "answer": answer.strip(),
        "sources": chunks_to_sources(relevant_chunks),
    }


def check_health() -> dict:
    status = {"embeddings_loaded": False, "ollama_reachable": False, "chunk_count": 0}

    try:
        df = load_embeddings()
        status["embeddings_loaded"] = True
        status["chunk_count"] = len(df)
    except EmbeddingsNotFoundError:
        pass

    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        status["ollama_reachable"] = response.ok
    except requests.exceptions.RequestException:
        pass

    status["ready"] = status["embeddings_loaded"] and status["ollama_reachable"]
    return status
