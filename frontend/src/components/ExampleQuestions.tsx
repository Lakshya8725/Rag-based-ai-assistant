const EXAMPLES = [
  "Where is the quotation tag taught?",
  "Explain CSS box model",
  "What are semantic HTML tags?",
  "How do CSS selectors work?",
];

interface Props {
  onSelect: (question: string) => void;
  disabled?: boolean;
}

export function ExampleQuestions({ onSelect, disabled }: Props) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {EXAMPLES.map((q) => (
        <button
          key={q}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(q)}
          className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:border-indigo-500/40 hover:bg-indigo-500/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
