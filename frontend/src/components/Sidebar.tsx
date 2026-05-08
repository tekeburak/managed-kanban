import type { View } from "../lib/types";

type Item = { id: View; label: string; icon: string };

const items: Item[] = [
  { id: "sessions", label: "Sessions", icon: "📋" },
  { id: "board", label: "Board", icon: "▤" },
  { id: "memory", label: "Memory Store", icon: "⌬" },
  { id: "settings", label: "Settings", icon: "⚙" },
];

export function Sidebar({
  activeView,
  onChange,
  open,
  onClose,
}: {
  activeView: View;
  onChange: (v: View) => void;
  open: boolean;
  onClose: () => void;
}) {
  return (
    <>
      {open && (
        <button
          type="button"
          aria-label="Close menu"
          onClick={onClose}
          className="lg:hidden fixed inset-0 z-30 bg-ink-900/40"
        />
      )}
      <aside
        className={
          "fixed lg:static inset-y-0 left-0 z-40 w-56 shrink-0 bg-canvas border-r border-ink-300/40 flex flex-col transform transition-transform lg:transform-none " +
          (open ? "translate-x-0" : "-translate-x-full lg:translate-x-0")
        }
      >
        <div className="px-5 pt-7 pb-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-md bg-ink-900 text-canvas grid place-items-center text-sm">
              ▤
            </div>
            <div>
              <div className="font-bold text-ink-900 leading-tight">Managed</div>
              <div className="font-bold text-ink-900 leading-tight">Agents</div>
              <div className="text-xs text-ink-500 mt-0.5">managed-kanban</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-3 space-y-1">
          {items.map((it) => {
            const active = activeView === it.id;
            return (
              <button
                key={it.id}
                type="button"
                onClick={() => onChange(it.id)}
                className={
                  "w-full text-left px-3 py-2 rounded-md flex items-center gap-3 text-sm transition-colors " +
                  (active
                    ? "bg-white text-ink-900 font-semibold shadow-sm border border-ink-300/60"
                    : "text-ink-700 hover:bg-white/60")
                }
              >
                <span className="text-base w-4 inline-block text-center">
                  {it.icon}
                </span>
                <span>{it.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="px-3 pb-5 space-y-1 text-sm">
          <a
            href="https://platform.claude.com/docs/en/managed-agents/overview"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-2 flex items-center gap-3 text-ink-700 hover:bg-white/60 rounded-md"
          >
            <span className="text-base w-4 inline-block text-center">📄</span>
            <span>API Docs</span>
          </a>
          <a
            href="https://github.com/tekeburak/managed-kanban/issues"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-2 flex items-center gap-3 text-ink-700 hover:bg-white/60 rounded-md"
          >
            <span className="text-base w-4 inline-block text-center">?</span>
            <span>Support</span>
          </a>
        </div>
      </aside>
    </>
  );
}
