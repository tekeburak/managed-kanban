import { useEffect, useState } from "react";
import { listSessions } from "../lib/api";
import type { SessionInfo } from "../lib/types";

const STATUS_STYLES: Record<SessionInfo["status"], string> = {
  running: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
};

export function SessionsView({ search }: { search: string }) {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const data = await listSessions();
        if (!cancelled) setSessions(data);
      } catch (e) {
        if (!cancelled) setError(String(e));
      }
    };
    tick();
    const id = setInterval(tick, 3000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const q = search.trim().toLowerCase();
  const filtered = q
    ? sessions.filter(
        (s) =>
          s.id.toLowerCase().includes(q) ||
          s.ticket_id.toLowerCase().includes(q) ||
          s.ticket_title.toLowerCase().includes(q),
      )
    : sessions;

  return (
    <div>
      <h1 className="text-3xl font-extrabold text-ink-900 mb-1">Sessions</h1>
      <p className="text-sm text-ink-500 mb-6">
        Every Managed Agents session this app has launched, newest first.
      </p>

      {error && (
        <div className="mb-4 p-3 rounded-md bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      {filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-ink-300/60 bg-white p-10 text-center text-sm text-ink-500">
          {sessions.length === 0
            ? "No sessions yet — drag a ticket to In Progress to start one."
            : `No sessions matching "${search}"`}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-ink-300/40 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-ink-300/10 text-ink-500 text-xs uppercase tracking-wider">
              <tr>
                <th className="text-left px-4 py-2 font-semibold">Ticket</th>
                <th className="text-left px-4 py-2 font-semibold">Session</th>
                <th className="text-left px-4 py-2 font-semibold">Status</th>
                <th className="text-right px-4 py-2 font-semibold">Tools</th>
                <th className="text-right px-4 py-2 font-semibold">Events</th>
                <th className="text-right px-4 py-2 font-semibold">Duration</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.id} className="border-t border-ink-300/30">
                  <td className="px-4 py-3">
                    <div className="font-mono text-xs text-blue-700">
                      {s.ticket_id}
                    </div>
                    <div className="text-ink-900">{s.ticket_title}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-ink-700 truncate max-w-[200px]">
                    {s.id}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        "text-[11px] font-bold px-2 py-0.5 rounded uppercase tracking-wider " +
                        STATUS_STYLES[s.status]
                      }
                    >
                      {s.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-ink-700">
                    {s.tool_calls}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-ink-700">
                    {s.log_entries}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-ink-700">
                    {durationLabel(s.started_at, s.finished_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function durationLabel(startedAt: string, finishedAt: string | null): string {
  const start = new Date(startedAt).getTime();
  const end = finishedAt ? new Date(finishedAt).getTime() : Date.now();
  const seconds = Math.max(0, Math.floor((end - start) / 1000));
  const m = Math.floor(seconds / 60);
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}
