import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { askQuestion, fetchHealth, type AskResponse, type Source } from "./lib/api";
import { ChatMessage } from "./components/ChatMessage";
import { ExampleQuestions } from "./components/ExampleQuestions";
import { Header } from "./components/Header";
import { SourceCard } from "./components/SourceCard";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">(
    "checking",
  );
  const [chunkCount, setChunkCount] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  const checkBackend = useCallback(async () => {
    try {
      const health = await fetchHealth();
      setBackendStatus(health.ready ? "online" : "offline");
      setChunkCount(health.chunk_count);
    } catch {
      setBackendStatus("offline");
    }
  }, []);

  useEffect(() => {
    checkBackend();
    const interval = setInterval(checkBackend, 15000);
    return () => clearInterval(interval);
  }, [checkBackend]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, sources]);

  const submitQuestion = async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setError(null);
    setSources([]);
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: trimmed },
    ]);
    setInput("");
    setLoading(true);

    try {
      const result: AskResponse = await askQuestion(trimmed);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: result.answer },
      ]);
      setSources(result.sources);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Sorry, I couldn't reach the backend. Make sure the API and Ollama are running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    submitQuestion(input);
  };

  const showWelcome = messages.length === 0 && !loading;

  return (
    <div className="flex min-h-screen flex-col">
      <Header status={backendStatus} chunkCount={chunkCount} />

      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-4 py-6 sm:px-6">
        {showWelcome && (
          <section className="animate-fade-in mb-8 text-center">
            <h2 className="mb-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Ask anything about the course
            </h2>
            <p className="mx-auto mb-6 max-w-lg text-sm text-slate-400">
              Powered by RAG — retrieves real transcript segments and cites the exact
              video and timestamp where topics are taught.
            </p>
            <ExampleQuestions onSelect={submitQuestion} disabled={loading} />
          </section>
        )}

        <div className="flex flex-1 flex-col gap-5 pb-4">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} role={msg.role} content={msg.content} />
          ))}
          {loading && <ChatMessage role="assistant" content="" loading />}
        </div>

        {sources.length > 0 && !loading && (
          <section className="animate-fade-in mb-4">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Retrieved sources
            </h3>
            <div className="grid gap-2 sm:grid-cols-2">
              {sources.map((src, i) => (
                <SourceCard key={`${src.video_number}-${src.start}-${i}`} source={src} />
              ))}
            </div>
          </section>
        )}

        {error && (
          <p className="mb-3 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">
            {error}
          </p>
        )}

        <div ref={bottomRef} />

        <form
          onSubmit={handleSubmit}
          className="glass sticky bottom-4 mt-auto rounded-2xl p-2 shadow-2xl shadow-black/40"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about HTML, CSS, or any course topic..."
              disabled={loading}
              className="flex-1 rounded-xl bg-transparent px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition hover:from-indigo-400 hover:to-violet-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Ask
            </button>
          </div>
        </form>
      </main>

      <footer className="py-4 text-center text-[11px] text-slate-600">
        RAG Demo · Whisper + BGE-M3 + Llama 3.2
      </footer>
    </div>
  );
}
