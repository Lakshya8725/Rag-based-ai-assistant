interface Props {
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
}

export function ChatMessage({ role, content, loading }: Props) {
  const isUser = role === "user";

  return (
    <div
      className={`animate-fade-in flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
          isUser
            ? "bg-slate-700 text-slate-200"
            : "bg-gradient-to-br from-indigo-500 to-violet-600 text-white"
        }`}
      >
        {isUser ? "You" : "AI"}
      </div>

      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed sm:max-w-[75%] ${
          isUser
            ? "rounded-tr-sm bg-indigo-600 text-white"
            : "glass rounded-tl-sm text-slate-100"
        }`}
      >
        {loading ? (
          <div className="flex items-center gap-2 text-slate-400">
            <span className="flex gap-1">
              <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-400 [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-400 [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-400" />
            </span>
            Searching course content...
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{content}</p>
        )}
      </div>
    </div>
  );
}
