import { useEffect } from "react";
import type { View } from "../lib/types";

const VIEW_KEYS: Record<string, View> = {
  "1": "board",
  "2": "sessions",
  "3": "memory",
  "4": "settings",
};

function isTypingInForm(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (target.isContentEditable) return true;
  return false;
}

/**
 * Global keyboard shortcuts:
 *   1-4   switch view (Board, Sessions, Memory, Settings)
 *   /     focus the top search input
 *
 * Suppressed while the user is typing in any form field so we don't hijack
 * keystrokes meant for textareas or search itself.
 */
export function useKeyboardShortcuts({
  onView,
  onFocusSearch,
}: {
  onView: (v: View) => void;
  onFocusSearch: () => void;
}) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (isTypingInForm(e.target)) return;

      const view = VIEW_KEYS[e.key];
      if (view) {
        e.preventDefault();
        onView(view);
        return;
      }

      if (e.key === "/") {
        e.preventDefault();
        onFocusSearch();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onView, onFocusSearch]);
}
