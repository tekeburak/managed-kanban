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

export function Board() {
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

  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd}>
      <div className="flex gap-5">
        {COLUMNS.map((col) => (
          <Column
            key={col.id}
            id={col.id}
            tickets={tickets.filter((t) => t.column === col.id)}
          />
        ))}
      </div>
    </DndContext>
  );
}
