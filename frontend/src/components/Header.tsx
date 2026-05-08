import type { View } from "../lib/types";

const PLACEHOLDER: Record<View, string> = {
  board: "Search tickets by ID, title, or description...",
  sessions: "Search sessions by ID or ticket title...",
  memory: "Search disabled in Memory Store",
  settings: "Search disabled in Settings",
};

export function TopBar({
  view,
  search,
  onSearch,
  onMenu,
}: {
  view: View;
  search: string;
  onSearch: (s: string) => void;
  onMenu: () => void;
}) {
  const disabled = view === "memory" || view === "settings";
  return (
    <div className="flex items-center gap-3 px-4 sm:px-6 py-3 border-b border-ink-300/40 bg-canvas">
      <button
        type="button"
        onClick={onMenu}
        aria-label="Open menu"
        className="lg:hidden text-2xl text-ink-700 leading-none px-1"
      >
        ☰
      </button>
      <div className="flex-1 min-w-0 max-w-2xl">
        <div className="bg-white border border-ink-300/50 rounded-full px-4 py-2 text-sm flex items-center gap-2">
          <span className="text-ink-500">🔍</span>
          <input
            type="text"
            value={disabled ? "" : search}
            onChange={(e) => onSearch(e.target.value)}
            disabled={disabled}
            placeholder={PLACEHOLDER[view]}
            className="bg-transparent flex-1 min-w-0 outline-none text-ink-900 placeholder:text-ink-500 disabled:cursor-not-allowed"
          />
          {!disabled && search && (
            <button
              type="button"
              onClick={() => onSearch("")}
              className="text-xs text-ink-500 hover:text-ink-900"
            >
              clear
            </button>
          )}
        </div>
      </div>
      <div className="flex items-center gap-3 text-ink-700">
        <span className="text-lg hidden sm:inline" title="Notifications">
          🔔
        </span>
        <span className="text-lg hidden sm:inline" title="Keyboard shortcuts">
          ⌨
        </span>
        <span className="text-xs font-mono text-ink-700 hidden md:inline">
          DEMO-001
        </span>
        <div className="w-7 h-7 rounded-full bg-ink-900 text-canvas text-xs font-bold grid place-items-center">
          MA
        </div>
      </div>
    </div>
  );
}

export function BoardHeader() {
  return (
    <div className="flex items-start sm:items-center justify-between gap-3 mb-6">
      <div className="min-w-0">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-ink-900">
          Development Board
        </h1>
        <p className="text-xs sm:text-sm text-ink-500 mt-1">
          Managed Agents — Drag tickets to{" "}
          <span className="font-semibold text-ink-700">"In Progress"</span> to
          start an agent
        </p>
      </div>

      <div className="shrink-0 flex items-center gap-2 text-xs text-ink-700 bg-white border border-ink-300/60 rounded-full px-3 py-1.5">
        <span className="w-2 h-2 rounded-full bg-emerald-500" />
        <span className="hidden sm:inline">Agents Online</span>
        <span className="sm:hidden">Online</span>
      </div>
    </div>
  );
}
