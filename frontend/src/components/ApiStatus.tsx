import { useEffect, useState } from "react";

import { api } from "../api/client";

type State = "checking" | "ready" | "no-key" | "offline";

const LABELS: Record<State, string> = {
  checking: "Checking API",
  ready: "API connected",
  "no-key": "API connected, LLM key missing",
  offline: "API offline",
};

const DOT: Record<State, string> = {
  checking: "bg-rule",
  ready: "bg-emerald-600",
  "no-key": "bg-amber-500",
  offline: "bg-error",
};

export function ApiStatus() {
  const [state, setState] = useState<State>("checking");

  useEffect(() => {
    let active = true;
    api
      .health()
      .then((h) => active && setState(h.llm_configured ? "ready" : "no-key"))
      .catch(() => active && setState("offline"));
    return () => {
      active = false;
    };
  }, []);

  return (
    <p className="flex items-center gap-2 text-sm text-muted" role="status">
      <span className={`size-2 rounded-full ${DOT[state]}`} aria-hidden="true" />
      {LABELS[state]}
    </p>
  );
}
