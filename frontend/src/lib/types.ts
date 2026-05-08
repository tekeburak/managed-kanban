export type Column = "backlog" | "in_progress" | "review" | "done";

export type Priority = "low" | "medium" | "high";

export type LogEntry = {
  kind: "status" | "tool_use" | "agent_text" | "score" | "system" | "failed";
  text: string;
  at: string;
};

export type FailedAttempt = {
  number: number;
  reason: string;
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
  attempt_number: number;
  failed_attempt: FailedAttempt | null;
  log: LogEntry[];
};

export const COLUMNS: { id: Column; label: string; dot: string }[] = [
  { id: "backlog", label: "BACKLOG", dot: "bg-gray-400" },
  { id: "in_progress", label: "IN PROGRESS", dot: "bg-blue-500" },
  { id: "review", label: "REVIEW", dot: "bg-amber-500" },
  { id: "done", label: "DONE", dot: "bg-emerald-500" },
];

export type View = "board" | "sessions" | "memory" | "settings";

export type SessionStatus = "running" | "completed" | "failed";

export type SessionInfo = {
  id: string;
  ticket_id: string;
  ticket_title: string;
  status: SessionStatus;
  started_at: string;
  finished_at: string | null;
  tool_calls: number;
  log_entries: number;
};

export type Settings = {
  agent_id: string | null;
  environment_id: string | null;
  model: string;
  system_prompt: string;
  total_sessions: number;
  active_sessions: number;
};
