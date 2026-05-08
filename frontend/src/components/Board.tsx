import { useCallback, useEffect, useMemo, useState } from "react";
import {
  DndContext,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import { Column } from "./Column";
import { listTickets, moveTicket, subscribeTicket } from "../lib/api";
import type { Column as ColumnId, Ticket } from "../lib/types";
import { COLUMNS } from "../lib/types";

export function Board({ search }: { search: string }) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [error, setError] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
  );

  useEffect(() => {
    listTickets().then(setTickets).catch((e) => setError(String(e)));
  }, []);

  const upsert = useCallback((next: Ticket) => {
    setTickets((prev) => {
      const idx = prev.findIndex((t) => t.id === next.id);
      if (idx === -1) return [...prev, next];
      const copy = prev.slice();
      copy[idx] = next;
      return copy;
    });
  }, []);

  // Subscribe to every ticket that's currently "active" so we get live updates.
  // When a ticket transitions out of in_progress/review the effect re-runs and
  // closes its EventSource; new ones get subscribed automatically.
  const activeIds = useMemo(
    () =>
      tickets
        .filter((t) => t.column === "in_progress" || t.column === "review")
        .map((t) => t.id)
        .join(","),
    [tickets],
  );

  useEffect(() => {
    if (!activeIds) return;
    const ids = activeIds.split(",").filter(Boolean);
    const closers = ids.map((id) => subscribeTicket(id, upsert));
    return () => closers.forEach((c) => c());
  }, [activeIds, upsert]);

  const onDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;
    const target = over.id as ColumnId;
    const ticket = tickets.find((t) => t.id === active.id);
    if (!ticket || ticket.column === target) return;

    // Optimistic update — server confirms via PATCH response and SSE.
    setTickets((prev) =>
      prev.map((t) => (t.id === active.id ? { ...t, column: target } : t)),
    );
    try {
      const updated = await moveTicket(String(active.id), target);
      upsert(updated);
    } catch (e) {
      setError(String(e));
    }
  };

  if (error) {
    return (
      <div className="p-6 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md">
        {error}
      </div>
    );
  }

  const q = search.trim().toLowerCase();
  const visibleTickets = q
    ? tickets.filter(
        (t) =>
          t.id.toLowerCase().includes(q) ||
          t.title.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q) ||
          (t.tag ?? "").toLowerCase().includes(q),
      )
    : tickets;

  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd}>
      <div className="flex gap-5 overflow-x-auto lg:overflow-visible snap-x snap-mandatory lg:snap-none -mx-4 px-4 sm:mx-0 sm:px-0 pb-2">
        {COLUMNS.map((col) => (
          <div
            key={col.id}
            className="snap-start shrink-0 w-[85vw] max-w-[320px] lg:w-auto lg:max-w-none lg:flex-1 lg:min-w-0 lg:basis-0"
          >
            <Column
              id={col.id}
              tickets={visibleTickets.filter((t) => t.column === col.id)}
            />
          </div>
        ))}
      </div>
    </DndContext>
  );
}
