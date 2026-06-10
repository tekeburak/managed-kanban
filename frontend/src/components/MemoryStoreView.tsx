import { useCallback, useEffect, useState } from "react";
import { getMemory, putMemory } from "../lib/api";
import type { MemoryItem } from "../lib/types";

export function MemoryStoreView() {
  const [notes, setNotes] = useState("");
  const [saved, setSaved] = useState("");
  const [storeId, setStoreId] = useState<string | null>(null);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [memError, setMemError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  const load = useCallback(async (initial: boolean) => {
    if (!initial) setRefreshing(true);
    try {
      const m = await getMemory();
      setStoreId(m.store_id);
      setMemories(m.memories);
      setMemError(m.error);
      if (initial) {
        setNotes(m.notes);
        setSaved(m.notes);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load(true);
  }, [load]);

  const dirty = notes !== saved;

  const save = async () => {
    setError(null);
    try {
      const result = await putMemory(notes);
      setSaved(result.notes);
      setSavedAt(new Date().toLocaleTimeString());
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-extrabold text-ink-900 mb-1">Memory Store</h1>
      <p className="text-sm text-ink-500 mb-6">
        A Managed Agents memory store is attached to every session read-write.
        The agent recalls these memories before starting a ticket and saves new
        learnings when it finishes.
      </p>

      {error && (
        <div className="mb-4 p-3 rounded-md bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl border border-ink-300/40 p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-xs font-semibold uppercase tracking-wider text-ink-500">
              Agent memories
            </span>
            {storeId && (
              <span className="text-[10px] font-mono text-ink-500 bg-canvas border border-ink-300/50 rounded-full px-2 py-0.5 truncate">
                {storeId}
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={() => load(false)}
            disabled={refreshing}
            className="text-xs font-semibold px-3 py-1 rounded-md text-ink-700 border border-ink-300/60 hover:bg-canvas disabled:opacity-40"
          >
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {memError && (
          <div className="mb-3 p-2 rounded-md bg-amber-50 border border-amber-200 text-xs text-amber-700">
            {memError}
          </div>
        )}

        {loading ? (
          <div className="text-sm text-ink-500 py-6 text-center">Loading...</div>
        ) : !storeId ? (
          <div className="text-sm text-ink-500 py-6 text-center">
            Memory store not created yet — it is provisioned on the first agent
            session.
          </div>
        ) : memories.length === 0 ? (
          <div className="text-sm text-ink-500 py-6 text-center font-mono">
            No memories yet. Run a ticket — the agent saves learnings here.
          </div>
        ) : (
          <div className="space-y-2">
            {memories.map((m) => (
              <div
                key={m.path}
                className="bg-canvas border border-ink-300/40 rounded-lg px-3 py-2"
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-[11px] font-mono font-semibold text-blue-700 truncate">
                    {m.path}
                  </span>
                  {m.updated_at && (
                    <span className="text-[10px] text-ink-500 shrink-0">
                      {new Date(m.updated_at).toLocaleString()}
                    </span>
                  )}
                </div>
                {m.content && (
                  <pre className="text-xs text-ink-700 whitespace-pre-wrap break-words font-mono leading-relaxed max-h-40 overflow-y-auto">
                    {m.content}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-ink-300/40 p-5">
        <label className="block text-xs font-semibold uppercase tracking-wider text-ink-500 mb-2">
          Standing notes (prepended to every ticket prompt)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={loading}
          placeholder='e.g. "Always write tests with pytest, prefer black formatting, never commit secrets."'
          className="w-full min-h-[160px] font-mono text-sm leading-relaxed bg-canvas border border-ink-300/50 rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />

        <div className="flex items-center justify-between mt-4">
          <div className="text-xs text-ink-500">
            {loading
              ? "Loading..."
              : dirty
                ? "Unsaved changes"
                : savedAt
                  ? `Saved at ${savedAt}`
                  : "Up to date"}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setNotes(saved)}
              disabled={!dirty}
              className="text-sm px-4 py-1.5 rounded-md text-ink-700 hover:bg-ink-300/20 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Revert
            </button>
            <button
              type="button"
              onClick={save}
              disabled={!dirty}
              className="text-sm font-semibold px-4 py-1.5 rounded-md bg-ink-900 text-canvas hover:bg-ink-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
