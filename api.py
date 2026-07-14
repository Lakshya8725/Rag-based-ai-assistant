"""
FastAPI server for the RAG teaching assistant.

Run locally and expose via Cloudflare Tunnel for the deployed frontend:
  uvicorn api:app --host 0.0.0.0 --port 8000
  cloudflared tunnel --url http://localhost:8000
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag_engine import (
    EmbeddingsNotFoundError,
    OllamaUnavailableError,
    RagEngineError,
    ask_question,
    check_health,
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Sigma Course RAG Assistant",
    description="Ask questions about the web development course and get video timestamps.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class Source(BaseModel):
    video_number: str
    title: str
    start: str
    end: str
    score: float
    excerpt: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]


@app.get("/")
def root():
    return {"message": "Sigma Course RAG API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return check_health()


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    try:
        result = ask_question(body.question)
        return result
    except EmbeddingsNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RagEngineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error.") from exc
