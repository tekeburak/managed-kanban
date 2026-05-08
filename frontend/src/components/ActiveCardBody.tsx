import { useState } from "react";
import type { Ticket } from "../lib/types";

export function ActiveCardBody({ ticket }: { ticket: Ticket }) {
  const [logOpen, setLogOpen] = useState(true);

  const pill = ticket.status_pill ?? "Starting agent session...";
  const isReview = ticket.column === "review";

  return (
    <>
      <div
        className={
          "flex items-center gap-2 text-sm rounded-md px-3 py-2 mb-3 " +
          (isReview
            ? "bg-amber-50 text-amber-700 border border-amber-200"
            : "bg-blue-50 text-blue-700")
        }
      >
        <span
          className={
            "w-1.5 h-1.5 rounded-full " +
            (isReview ? "bg-amber-500" : "bg-blue-500 animate-pulse")
          }
        />
        <span className="font-medium">{pill}</span>
      </div>

      {ticket.score_before != null && ticket.score_after != null && (
        <ScoreWidget
          before={ticket.score_before}
          after={ticket.score_after}
        />
      )}

      {ticket.log.length > 0 && (
        <ToolStrip log={ticket.log} />
      )}

      {ticket.log.length > 0 && (
        <div className="border-t border-ink-300/40 pt-2">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setLogOpen((v) => !v);
            }}
            className="text-xs text-ink-700 hover:text-ink-900 flex items-center gap-1"
          >
            <span>{logOpen ? "▾" : "▸"}</span>
            <span>
              {logOpen ? "Hide log" : `Show log (${ticket.log.length})`}
            </span>
          </button>

          {logOpen && (
            <div className="mt-2 max-h-44 overflow-y-auto space-y-1.5 font-mono text-[11px] leading-relaxed text-ink-700 bg-gray-50 rounded p-2 border border-ink-300/30">
              {ticket.log.slice(-30).map((entry, i) => (
                <LogLine key={i} kind={entry.kind} text={entry.text} />
              ))}
            </div>
          )}
        </div>
      )}

      {ticket.session_id && (
        <div className="mt-2 text-[10px] text-ink-500 font-mono truncate">
          Session: {ticket.session_id}
        </div>
      )}
    </>
  );
}

function ScoreWidget({ before, after }: { before: number; after: number }) {
  const positive = after > before;
  const neutral = after === before;
  const afterTone = positive
    ? "text-emerald-600"
    : neutral
      ? "text-ink-700"
      : "text-red-600";

  return (
    <div className="flex items-center justify-between bg-white rounded-md px-3 py-2 mb-3 border border-ink-300/50">
      <span className="text-[10px] uppercase tracking-[0.18em] text-ink-500 font-semibold">
        Score
      </span>
      <span className="font-mono text-base flex items-baseline gap-2">
        <span className="text-red-600 font-bold">{before}</span>
        <span className="text-ink-300">→</span>
        <span className={"font-bold " + afterTone}>{after}</span>
      </span>
    </div>
  );
}

function ToolStrip({ log }: { log: { kind: string; text: string }[] }) {
  const tools = log.filter((e) => e.kind === "tool_use");
  if (tools.length === 0) return null;
  const counts = new Map<string, number>();
  for (const t of tools) {
    const name = t.text.replace(/^Running:\s*/, "");
    counts.set(name, (counts.get(name) ?? 0) + 1);
  }
  return (
    <div className="flex items-center flex-wrap gap-1.5 mb-3">
      {[...counts.entries()].map(([name, count]) => (
        <span
          key={name}
          className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-violet-50 text-violet-700 border border-violet-200"
        >
          <span className="opacity-70">⚙</span>
          <span>{name}</span>
          {count > 1 && (
            <span className="text-[9px] bg-violet-200 px-1 rounded-sm">
              {count}
            </span>
          )}
        </span>
      ))}
    </div>
  );
}

function LogLine({ kind, text }: { kind: string; text: string }) {
  const icon =
    kind === "tool_use"
      ? "⚙"
      : kind === "score"
        ? "📊"
        : kind === "status"
          ? "●"
          : kind === "system"
            ? "ⓘ"
            : "▸";
  const color =
    kind === "tool_use"
      ? "text-violet-700"
      : kind === "score"
        ? "text-emerald-700"
        : kind === "system"
          ? "text-ink-500"
          : "text-ink-900";
  return (
    <div className={"flex gap-2 " + color}>
      <span className="opacity-70">{icon}</span>
      <span className="break-words">{text}</span>
    </div>
  );
}
