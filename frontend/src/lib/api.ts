import type {
  Column,
  MemoryState,
  SessionInfo,
  Settings,
  Ticket,
} from "./types";

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
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`move failed (${res.status}): ${body || res.statusText}`);
  }
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

export async function listSessions(): Promise<SessionInfo[]> {
  const res = await fetch("/api/sessions");
  if (!res.ok) throw new Error("failed to list sessions");
  return res.json();
}

export async function getMemory(): Promise<MemoryState> {
  const res = await fetch("/api/memory");
  if (!res.ok) throw new Error("failed to read memory");
  return res.json();
}

export async function putMemory(notes: string): Promise<{ notes: string }> {
  const res = await fetch("/api/memory", {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error("failed to write memory");
  return res.json();
}

export async function getSettings(): Promise<Settings> {
  const res = await fetch("/api/settings");
  if (!res.ok) throw new Error("failed to read settings");
  return res.json();
}
