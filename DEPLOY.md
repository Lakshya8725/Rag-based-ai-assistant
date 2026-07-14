# Public Demo Deployment Guide

Deploy the **frontend** for free on Vercel. Run the **backend** on your Mac and expose it with a free Cloudflare Tunnel.

```
[Vercel - Frontend]  --->  [Cloudflare Tunnel URL]  --->  [Your Mac: FastAPI + Ollama]
```

---

## Part 1 — Backend (your Mac)

### 1. Prerequisites running locally

```bash
# Terminal 1 — Ollama
ollama serve
ollama pull bge-m3
ollama pull llama3.2

# Make sure you have embeddings (one-time, after indexing course data)
# ls new_embeddings.joblib
```

### 2. Install API dependencies

```bash
cd /Users/lakshyaarora/Desktop/rag-based-ai
source venv/bin/activate
pip install fastapi uvicorn pydantic
```

### 3. Start the API

```bash
# Replace with your future Vercel URL once deployed
export ALLOWED_ORIGINS="http://localhost:5173,https://YOUR-APP.vercel.app"

uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Test: open http://localhost:8000/health — should show `"ready": true`.

### 4. Expose localhost with Cloudflare Tunnel (free)

```bash
# Install once: brew install cloudflared

# Terminal 2 — tunnel (keep running during demo)
cloudflared tunnel --url http://localhost:8000
```

Copy the URL it prints, e.g. `https://random-words.trycloudflare.com`.

> Keep this terminal open. The URL changes each time unless you set up a named tunnel.

### 5. Update CORS with your Vercel URL

```bash
export ALLOWED_ORIGINS="https://YOUR-APP.vercel.app,http://localhost:5173"
# restart uvicorn after changing this
```

---

## Part 2 — Frontend (Vercel, free)

### 1. Local test first

```bash
cd frontend
cp .env.example .env
# Edit .env — set VITE_API_URL to your cloudflared URL
npm install
npm run dev
```

Open http://localhost:5173 and ask a question.

### 2. Deploy to Vercel

1. Push this repo to GitHub.
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → import your repo.
3. Set **Root Directory** to `frontend`.
4. Add environment variable:
   - `VITE_API_URL` = `https://your-cloudflared-url.trycloudflare.com`
5. Deploy.

### 3. After deploy

1. Copy your Vercel URL (e.g. `https://rag-assistant.vercel.app`).
2. Update `ALLOWED_ORIGINS` on your Mac to include that URL.
3. Restart `uvicorn`.
4. Share the **Vercel URL** as your public demo.

---

## Demo checklist

Before sharing the link, verify:

- [ ] Ollama running (`ollama serve`)
- [ ] `new_embeddings.joblib` exists in project root
- [ ] `uvicorn api:app --host 0.0.0.0 --port 8000` running
- [ ] `cloudflared tunnel --url http://localhost:8000` running
- [ ] Vercel `VITE_API_URL` matches current tunnel URL
- [ ] `ALLOWED_ORIGINS` includes your Vercel domain
- [ ] http://localhost:8000/health shows `"ready": true`
- [ ] Frontend status badge shows **Backend online**

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| CORS error in browser | Add Vercel URL to `ALLOWED_ORIGINS`, restart uvicorn |
| Backend offline badge | Tunnel expired — restart cloudflared, update Vercel env |
| 503 embeddings not found | Run `preprocess_new_json.py` to create `new_embeddings.joblib` |
| 503 Ollama error | Run `ollama serve` and pull models |
| Slow first answer | Normal — LLM cold start on first query |

---

## Alternative tunnel: ngrok

```bash
brew install ngrok
ngrok http 8000
```

Use the `https://....ngrok-free.app` URL as `VITE_API_URL`.
