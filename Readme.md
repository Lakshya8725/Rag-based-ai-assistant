# RAG-Based AI Teaching Assistant

A local **Retrieval-Augmented Generation (RAG)** pipeline that turns course videos into a searchable teaching assistant. Ask a question in natural language and get an answer with the **exact video number and timestamp**.

## Tech Stack

- **ffmpeg** — video to audio extraction
- **OpenAI Whisper** — Hindi speech to English transcripts
- **BGE-M3** (Ollama) — text embeddings
- **Llama 3.2** (Ollama) — answer generation
- **scikit-learn** — cosine similarity retrieval

## Prerequisites

1. [ffmpeg](https://ffmpeg.org/) installed and on your `PATH`
2. [Ollama](https://ollama.com/) running locally with models pulled:
   ```bash
   ollama pull bge-m3
   ollama pull llama3.2
   ```

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Pipeline

Place course videos in `videos/`, then run each step in order:

| Step | Script | Input → Output |
|------|--------|----------------|
| 1 | `video_to_mp3.py` | `videos/` → `audios/` |
| 2 | `mp3_to_json.py` | `audios/` → `jsons/` |
| 3 | `merge_chunks.py` | `jsons/` → `new_jsons/` (optional, recommended) |
| 4 | `preprocess_new_json.py` | `new_jsons/` → `new_embeddings.joblib` |
| 5 | `process_incoming.py` | user query + embeddings → answer |

```bash
python video_to_mp3.py
python mp3_to_json.py
python merge_chunks.py
python preprocess_new_json.py
python process_incoming.py
```

## Project Structure

```
├── video_to_mp3.py          # Step 1: extract audio
├── mp3_to_json.py           # Step 2: transcribe & translate
├── merge_chunks.py          # Step 3: merge segments for retrieval
├── preprocess_json.py       # Step 4a: embed raw segments
├── preprocess_new_json.py   # Step 4b: embed merged chunks (used by Q&A)
├── process_incoming.py      # Step 5: RAG question answering
├── videos/                  # input videos (not committed)
├── audios/                  # extracted MP3s (not committed)
├── jsons/                   # Whisper transcripts (not committed)
└── new_jsons/               # merged chunks (not committed)
```

## Notes

- `preprocess_json.py` embeds raw Whisper segments into `embeddings.joblib`.
- `preprocess_new_json.py` embeds merged chunks into `new_embeddings.joblib` (used by the Q&A script).
- Large generated files (audio, JSON, embeddings) are gitignored — regenerate locally after cloning.
