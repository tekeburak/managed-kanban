export type Column = "backlog" | "in_progress" | "review" | "done";

export type Priority = "low" | "medium" | "high";

export type LogEntry = {
  kind: "status" | "tool_use" | "agent_text" | "score" | "system";
  text: string;
  at: string;
};

export type Ticket = {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  tag: string;
  column: Column;

  session_id: string | null;
  started_at: string | null;
  finished_at: string | null;

  status_pill: string | null;
  score_before: number | null;
  score_after: number | null;
  log: LogEntry[];
};

export const COLUMNS: { id: Column; label: string; dot: string }[] = [
  { id: "backlog", label: "BACKLOG", dot: "bg-gray-400" },
  { id: "in_progress", label: "IN PROGRESS", dot: "bg-blue-500" },
  { id: "review", label: "REVIEW", dot: "bg-amber-500" },
  { id: "done", label: "DONE", dot: "bg-emerald-500" },
];
