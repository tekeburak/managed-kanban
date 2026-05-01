import { Board } from "./components/Board";
import { Header, TopBar } from "./components/Header";
import { Sidebar } from "./components/Sidebar";

export default function App() {
  return (
    <div className="canvas-bg min-h-screen flex">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <TopBar />
        <div className="flex-1 px-8 py-6 overflow-auto">
          <Header />
          <Board />
        </div>
      </main>
    </div>
  );
}
