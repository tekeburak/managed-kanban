import { useState } from "react";
import { Board } from "./components/Board";
import { BoardHeader, TopBar } from "./components/Header";
import { MemoryStoreView } from "./components/MemoryStoreView";
import { SessionsView } from "./components/SessionsView";
import { SettingsView } from "./components/SettingsView";
import { Sidebar } from "./components/Sidebar";
import type { View } from "./lib/types";

export default function App() {
  const [view, setView] = useState<View>("board");
  const [search, setSearch] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleViewChange = (v: View) => {
    setView(v);
    setSearch("");
    setSidebarOpen(false);
  };

  return (
    <div className="canvas-bg min-h-screen flex">
      <Sidebar
        activeView={view}
        onChange={handleViewChange}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <main className="flex-1 flex flex-col min-w-0">
        <TopBar
          view={view}
          search={search}
          onSearch={setSearch}
          onMenu={() => setSidebarOpen(true)}
        />
        <div className="flex-1 px-4 py-4 sm:px-8 sm:py-6 overflow-auto">
          {view === "board" && (
            <>
              <BoardHeader />
              <Board search={search} />
            </>
          )}
          {view === "sessions" && <SessionsView search={search} />}
          {view === "memory" && <MemoryStoreView />}
          {view === "settings" && <SettingsView />}
        </div>
      </main>
    </div>
  );
}
