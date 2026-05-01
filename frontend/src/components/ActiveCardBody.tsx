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
        <div className="flex items-center justify-between bg-gray-50 rounded-md px-3 py-2 mb-3 border border-ink-300/40">
          <span className="text-[11px] uppercase tracking-wider text-ink-500 font-semibold">
            Score
          </span>
          <span className="font-mono">
            <span className="text-red-600 font-bold">{ticket.score_before}</span>
            <span className="text-ink-500 mx-2">→</span>
            <span
              className={
                "font-bold " +
                (ticket.score_after > ticket.score_before
                  ? "text-emerald-600"
                  : "text-red-600")
              }
            >
              {ticket.score_after}
            </span>
          </span>
        </div>
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
