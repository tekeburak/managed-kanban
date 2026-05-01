import type { Column, Ticket } from "./types";

export async function listTickets(): Promise<Ticket[]> {
  const res = await fetch("/api/tickets");
  if (!res.ok) throw new Error("failed to list tickets");
  return res.json();
}

export async function moveTicket(id: string, column: Column): Promise<Ticket> {
  const res = await fetch(`/api/tickets/${id}/move`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ column }),
  });
  if (!res.ok) throw new Error("failed to move ticket");
  return res.json();
}

export function subscribeTicket(
  id: string,
  onTicket: (t: Ticket) => void,
): () => void {
  const es = new EventSource(`/api/tickets/${id}/stream`);
  es.addEventListener("ticket", (ev) => {
    try {
      onTicket(JSON.parse((ev as MessageEvent).data));
    } catch {
      // ignore malformed frame; the next snapshot supersedes it
    }
  });
  return () => es.close();
}
