type Item = { label: string; active?: boolean; icon: string };

const items: Item[] = [
  { label: "Sessions", icon: "📋" },
  { label: "Board", active: true, icon: "▤" },
  { label: "Memory Store", icon: "⌬" },
  { label: "Settings", icon: "⚙" },
];

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-canvas border-r border-ink-300/40 flex flex-col">
      <div className="px-5 pt-7 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-ink-900 text-canvas grid place-items-center text-sm">▤</div>
          <div>
            <div className="font-bold text-ink-900 leading-tight">Managed</div>
            <div className="font-bold text-ink-900 leading-tight">Agents</div>
            <div className="text-xs text-ink-500 mt-0.5">managed-kanban</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {items.map((it) => (
          <div
            key={it.label}
            className={
              "px-3 py-2 rounded-md flex items-center gap-3 text-sm cursor-default " +
              (it.active
                ? "bg-white text-ink-900 font-semibold shadow-sm border border-ink-300/60"
                : "text-ink-700 hover:bg-white/60")
            }
          >
            <span className="text-base w-4 inline-block text-center">{it.icon}</span>
            <span>{it.label}</span>
          </div>
        ))}
      </nav>

      <div className="px-3 pb-5 space-y-1 text-sm text-ink-700">
        <div className="px-3 py-2 flex items-center gap-3">
          <span className="text-base w-4 inline-block text-center">📄</span>
          <span>API Docs</span>
        </div>
        <div className="px-3 py-2 flex items-center gap-3">
          <span className="text-base w-4 inline-block text-center">?</span>
          <span>Support</span>
        </div>
      </div>
    </aside>
  );
}
