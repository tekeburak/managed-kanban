import { useEffect, useState } from "react";
import { getSettings } from "../lib/api";
import type { Settings } from "../lib/types";

export function SettingsView() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSettings()
      .then(setSettings)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) {
    return (
      <div className="p-3 rounded-md bg-red-50 border border-red-200 text-sm text-red-700">
        {error}
      </div>
    );
  }

  if (!settings) {
    return <div className="text-sm text-ink-500">Loading...</div>;
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-extrabold text-ink-900 mb-1">Settings</h1>
      <p className="text-sm text-ink-500 mb-6">
        Read-only view of the Anthropic resources this app is bound to. To
        rotate them, run{" "}
        <code className="font-mono">make reset && make setup</code>.
      </p>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <Stat label="Total sessions" value={settings.total_sessions} />
        <Stat label="Active sessions" value={settings.active_sessions} />
      </div>

      <Section title="Anthropic resources">
        <Field label="Agent ID" value={settings.agent_id ?? "(not set)"} mono />
        <Field
          label="Environment ID"
          value={settings.environment_id ?? "(not set)"}
          mono
        />
        <Field label="Model" value={settings.model} mono />
      </Section>

      <Section title="System prompt">
        <pre className="font-mono text-xs leading-relaxed text-ink-700 bg-canvas border border-ink-300/50 rounded-lg p-4 whitespace-pre-wrap break-words max-h-[420px] overflow-auto">
          {settings.system_prompt}
        </pre>
        <p className="text-xs text-ink-500 mt-2">
          Edit{" "}
          <code className="font-mono">backend/app/agent_setup.py</code>, then{" "}
          <code className="font-mono">make reset && make setup</code> to apply.
        </p>
      </Section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-xl border border-ink-300/40 p-4">
      <div className="text-xs uppercase tracking-wider text-ink-500 font-semibold">
        {label}
      </div>
      <div className="text-3xl font-bold text-ink-900 mt-1 font-mono">
        {value}
      </div>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-xl border border-ink-300/40 p-5 mb-5">
      <h2 className="text-xs font-bold uppercase tracking-wider text-ink-500 mb-3">
        {title}
      </h2>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

function Field({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-xs text-ink-500 mb-1">{label}</div>
      <div
        className={
          "text-sm text-ink-900 break-all " + (mono ? "font-mono" : "")
        }
      >
        {value}
      </div>
    </div>
  );
}
