import { useEffect, useState } from "react";
import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import type { Ticket } from "../lib/types";
import { ActiveCardBody } from "./ActiveCardBody";

const PRIORITY_BADGE: Record<Ticket["priority"], string> = {
  high: "bg-red-600 text-white",
  medium: "bg-blue-100 text-blue-700",
  low: "bg-gray-100 text-gray-600",
};

const TAG_COLORS: Record<string, string> = {
  Performance: "bg-rose-100 text-rose-700",
  Research: "bg-blue-100 text-blue-700",
  Incident: "bg-red-600 text-white",
};

export function TicketCard({ ticket }: { ticket: Ticket }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id: ticket.id });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.4 : 1,
  };

  const isActive =
    ticket.column === "in_progress" || ticket.column === "review";

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-white rounded-xl border border-ink-300/60 shadow-sm p-4 cursor-grab active:cursor-grabbing select-none"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700">
          {ticket.id}
        </span>
        {isActive ? (
          <Timer
            startedAt={ticket.started_at}
            finishedAt={ticket.finished_at}
          />
        ) : (
          <span
            className={
              "text-[10px] font-bold px-2 py-0.5 rounded " +
              PRIORITY_BADGE[ticket.priority]
            }
          >
            {ticket.priority.toUpperCase()}
          </span>
        )}
      </div>

      <h3 className="font-semibold text-ink-900 leading-snug mb-2">
        {ticket.title}
      </h3>

      {isActive ? (
        <ActiveCardBody ticket={ticket} />
      ) : (
        <>
          <p className="text-sm text-ink-700 leading-relaxed line-clamp-3 mb-3">
            {ticket.description}
          </p>
          <div className="flex items-center justify-between">
            <span
              className={
                "text-[11px] font-medium px-2 py-1 rounded " +
                (TAG_COLORS[ticket.tag] ?? "bg-gray-100 text-gray-700")
              }
            >
              {ticket.tag}
            </span>
            <span className="text-ink-300 text-lg leading-none">⋮⋮</span>
          </div>
        </>
      )}
    </div>
  );
}

function Timer({
  startedAt,
  finishedAt,
}: {
  startedAt: string | null;
  finishedAt: string | null;
}) {
  const [, setNow] = useState(0);
  // Only tick when the session is actively running. If it's finished, the
  // displayed value is fixed (finishedAt - startedAt) and re-rendering once
  // a second is wasted work — and the visible bug the user reported.
  const isRunning = !!startedAt && !finishedAt;
  useEffect(() => {
    if (!isRunning) return;
    const id = setInterval(() => setNow((n) => n + 1), 1000);
    return () => clearInterval(id);
  }, [isRunning]);

  if (!startedAt) {
    return <span className="text-xs font-mono text-ink-500">0:00</span>;
  }
  const start = new Date(startedAt).getTime();
  const end = finishedAt ? new Date(finishedAt).getTime() : Date.now();
  const elapsed = Math.max(0, Math.floor((end - start) / 1000));
  const m = Math.floor(elapsed / 60);
  const s = (elapsed % 60).toString().padStart(2, "0");
  return (
    <span
      className={
        "text-xs font-mono " + (finishedAt ? "text-ink-500" : "text-ink-700")
      }
    >
      {m}:{s}
    </span>
  );
}
