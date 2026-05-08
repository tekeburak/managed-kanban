import { useDroppable } from "@dnd-kit/core";
import type { Column as ColumnId, Ticket } from "../lib/types";
import { TicketCard } from "./TicketCard";

const DOT: Record<ColumnId, string> = {
  backlog: "bg-gray-400",
  in_progress: "bg-blue-500",
  review: "bg-amber-500",
  done: "bg-emerald-500",
};

const LABEL: Record<ColumnId, string> = {
  backlog: "BACKLOG",
  in_progress: "IN PROGRESS",
  review: "REVIEW",
  done: "DONE",
};

export function Column({
  id,
  tickets,
}: {
  id: ColumnId;
  tickets: Ticket[];
}) {
  const { isOver, setNodeRef } = useDroppable({ id });

  return (
    <div className="w-full min-w-0">
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <span className={"w-2 h-2 rounded-full " + DOT[id]} />
          <span className="text-xs font-bold tracking-wider text-ink-700">
            {LABEL[id]}
          </span>
        </div>
        <span className="text-xs text-ink-500 bg-white border border-ink-300/50 rounded-full px-2 py-0.5 min-w-[24px] text-center">
          {tickets.length}
        </span>
      </div>

      <div
        ref={setNodeRef}
        className={
          "min-h-[140px] rounded-xl p-2 transition-colors " +
          (isOver
            ? "bg-blue-50/70 border-2 border-blue-200 border-dashed"
            : "border-2 border-dashed border-transparent")
        }
      >
        {tickets.length === 0 ? (
          <div className="grid place-items-center min-h-[140px] rounded-lg border-2 border-dashed border-ink-300/50 text-xs text-ink-500 font-mono">
            {id === "in_progress"
              ? "Drag tickets here to start agents"
              : "No tasks"}
          </div>
        ) : (
          <div className="space-y-3">
            {tickets.map((t) => (
              <TicketCard key={t.id} ticket={t} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
