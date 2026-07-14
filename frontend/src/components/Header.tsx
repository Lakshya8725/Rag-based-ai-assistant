import { API_URL } from "../lib/api";

type Status = "checking" | "online" | "offline";

interface Props {
  status: Status;
  chunkCount?: number;
}

export function Header({ status, chunkCount }: Props) {
  const statusConfig = {
    checking: { dot: "bg-amber-400 animate-pulse-soft", label: "Connecting..." },
    online: { dot: "bg-emerald-400", label: "Backend online" },
    offline: { dot: "bg-rose-400", label: "Backend offline" },
  }[status];

  return (
    <header className="glass sticky top-0 z-10 border-b border-white/10">
      <div className="mx-auto flex max-w-4xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-500/25">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-white">
              Course AI Assistant
            </h1>
            <p className="text-xs text-slate-400">
              RAG-powered · Sigma Web Development Course
            </p>
          </div>
        </div>

        <div className="hidden text-right sm:block">
          <div className="flex items-center justify-end gap-2">
            <span className={`h-2 w-2 rounded-full ${statusConfig.dot}`} />
            <span className="text-xs font-medium text-slate-300">{statusConfig.label}</span>
          </div>
          {chunkCount !== undefined && chunkCount > 0 && (
            <p className="mt-0.5 text-[11px] text-slate-500">{chunkCount} indexed segments</p>
          )}
        </div>
      </div>

      {status === "offline" && (
        <div className="border-t border-rose-500/20 bg-rose-500/10 px-4 py-2 text-center text-xs text-rose-200 sm:px-6">
          Start the API locally and expose it via Cloudflare Tunnel. API: {API_URL}
        </div>
      )}
    </header>
  );
}
