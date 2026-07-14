import type { Source } from "../lib/api";

interface Props {
  source: Source;
}

export function SourceCard({ source }: Props) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/60 p-3">
      <div className="mb-1 flex flex-wrap items-center gap-2">
        <span className="rounded-md bg-indigo-500/20 px-2 py-0.5 text-xs font-semibold text-indigo-300">
          Video {source.video_number}
        </span>
        <span className="rounded-md bg-slate-800 px-2 py-0.5 font-mono text-xs text-emerald-400">
          {source.start} – {source.end}
        </span>
        <span className="text-[10px] text-slate-500">match {source.score}</span>
      </div>
      <p className="text-sm font-medium text-slate-200">{source.title}</p>
      <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-400">
        {source.excerpt}
      </p>
    </div>
  );
}
