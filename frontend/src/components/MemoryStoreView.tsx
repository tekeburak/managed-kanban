import { useEffect, useState } from "react";
import { getMemory, putMemory } from "../lib/api";

export function MemoryStoreView() {
  const [notes, setNotes] = useState("");
  const [saved, setSaved] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  useEffect(() => {
    getMemory()
      .then((m) => {
        setNotes(m.notes);
        setSaved(m.notes);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

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
        Standing notes prepended to every ticket prompt. Use this to inject
        constraints, conventions, or context the agent should always honor.
      </p>

      {error && (
        <div className="mb-4 p-3 rounded-md bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl border border-ink-300/40 p-5">
        <label className="block text-xs font-semibold uppercase tracking-wider text-ink-500 mb-2">
          Notes
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={loading}
          placeholder='e.g. "Always write tests with pytest, prefer black formatting, never commit secrets."'
          className="w-full min-h-[260px] font-mono text-sm leading-relaxed bg-canvas border border-ink-300/50 rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
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

      <p className="text-xs text-ink-500 mt-4">
        Tip: this is in-memory only — restarting the backend resets it. For
        cross-restart persistence, swap the in-memory note in{" "}
        <code className="font-mono">backend/app/store.py</code> for a SQLite
        row.
      </p>
    </div>
  );
}
