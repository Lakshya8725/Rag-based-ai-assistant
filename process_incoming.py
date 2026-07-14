"""
Step 5 of the RAG pipeline: answer user questions about the course.

Embeds the user's question, finds the most similar subtitle chunks, builds
a teacher-style prompt, and sends it to a local LLM via Ollama.
"""

import joblib
import numpy as np
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "bge-m3"
LLM_MODEL = "llama3.2"
EMBEDDINGS_FILE = "new_embeddings.joblib"
TOP_K_RESULTS = 5

PROMPT_OUTPUT = "prompt.txt"
RESPONSE_OUTPUT = "response.txt"


# --- Helpers ---


def seconds_to_mmss(seconds: float) -> str:
    """Format seconds as mm:ss for display in LLM responses."""
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    return f"{minutes}:{secs:02d}"


def create_embedding(texts: list[str]) -> list[list[float]]:
    """Embed text using Ollama's /api/embed endpoint."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=300,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        print(f"Could not contact Ollama at {OLLAMA_BASE_URL}: {exc}")
        print("Make sure Ollama is running on port 11434.")
        raise SystemExit(1) from exc

    if "embeddings" in data and isinstance(data["embeddings"], list):
        return data["embeddings"]

    print("Unexpected Ollama response:", data)
    return []


def run_inference(prompt: str, model: str = LLM_MODEL) -> str:
    """Generate a response from the local LLM via Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as exc:
        print(f"Could not contact Ollama at {OLLAMA_BASE_URL}: {exc}")
        print("Make sure Ollama is running on port 11434.")
        raise SystemExit(1) from exc


def retrieve_relevant_chunks(
    df: pd.DataFrame,
    question_embedding: list[float],
    top_k: int,
) -> pd.DataFrame:
    """
    Rank all stored chunks by cosine similarity to the question,
    then return the top matches sorted chronologically by start time.
    """
    similarities = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding],
    ).flatten()

    best_indices = similarities.argsort()[::-1][:top_k]
    results = df.loc[best_indices].copy()
    results = results.sort_values("start")

    results["start_mmss"] = results["start"].apply(seconds_to_mmss)
    results["end_mmss"] = results["end"].apply(seconds_to_mmss)
    return results


def build_prompt(query: str, context_df: pd.DataFrame) -> str:
    """Assemble the system prompt with retrieved subtitle chunks."""
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


def main() -> None:
    # Load pre-computed chunk embeddings
    df = joblib.load(EMBEDDINGS_FILE)

    query = input("Ask a question: ")
    question_embedding = create_embedding([query])[0]

    relevant_chunks = retrieve_relevant_chunks(df, question_embedding, TOP_K_RESULTS)
    prompt = build_prompt(query, relevant_chunks)

    # Save prompt for debugging / inspection
    with open(PROMPT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(prompt)

    response = run_inference(prompt)

    print("\n--- ANSWER ---\n")
    print(response)

    with open(RESPONSE_OUTPUT, "w", encoding="utf-8") as f:
        f.write(response)


if __name__ == "__main__":
    main()
