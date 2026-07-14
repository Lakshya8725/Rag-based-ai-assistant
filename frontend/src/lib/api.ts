export interface Source {
  video_number: string;
  title: string;
  start: string;
  end: string;
  score: number;
  excerpt: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: Source[];
}

export interface HealthResponse {
  ready: boolean;
  embeddings_loaded: boolean;
  ollama_reachable: boolean;
  chunk_count: number;
}

const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/$/,
  "",
);

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || "Failed to get an answer.");
  }

  return data;
}

export { API_URL };
