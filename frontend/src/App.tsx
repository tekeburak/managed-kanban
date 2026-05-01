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

  const handleViewChange = (v: View) => {
    setView(v);
    setSearch("");
  };

  return (
    <div className="canvas-bg min-h-screen flex">
      <Sidebar activeView={view} onChange={handleViewChange} />
      <main className="flex-1 flex flex-col min-w-0">
        <TopBar view={view} search={search} onSearch={setSearch} />
        <div className="flex-1 px-8 py-6 overflow-auto">
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
