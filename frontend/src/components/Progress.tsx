import type { RunStatus, Step } from "../hooks/useOutreach";

const STEPS: { key: Step; label: string }[] = [
  { key: "resume", label: "Reading your resume" },
  { key: "match", label: "Finding and ranking jobs" },
  { key: "email", label: "Writing the email" },
];

export function Progress({ status }: { status: RunStatus }) {
  if (status.kind !== "running" && status.kind !== "error") return null;
  const current = STEPS.findIndex((s) => s.key === status.step);

  return (
    <div className="mt-6 border-t border-rule pt-5">
      <ol className="space-y-2.5 text-sm" aria-label="Progress">
        {STEPS.map((step, i) => {
          const failed = status.kind === "error" && i === current;
          const done = i < current;
          const active = status.kind === "running" && i === current;
          return (
            <li
              key={step.key}
              className={`flex items-center gap-2.5 ${done || active ? "text-ink" : "text-muted"} ${failed ? "text-error" : ""}`}
              aria-current={active ? "step" : undefined}
            >
              <StepMark done={done} active={active} failed={failed} />
              {step.label}
            </li>
          );
        })}
      </ol>
      {status.kind === "error" && (
        <p role="alert" className="mt-4 rounded-md bg-error-wash px-3 py-2.5 text-sm text-error">
          {status.message}
        </p>
      )}
    </div>
  );
}

function StepMark({ done, active, failed }: { done: boolean; active: boolean; failed: boolean }) {
  if (failed) return <span className="grid size-4 place-items-center text-xs" aria-hidden="true">✕</span>;
  if (done)
    return (
      <svg viewBox="0 0 16 16" className="size-4 text-cobalt" aria-hidden="true">
        <path d="M3 8.5l3 3 7-7" fill="none" stroke="currentColor" strokeWidth="2" />
      </svg>
    );
  if (active)
    return (
      <span
        className="size-4 animate-spin rounded-full border-2 border-cobalt/25 border-t-cobalt"
        aria-hidden="true"
      />
    );
  return <span className="size-4 rounded-full border-2 border-rule" aria-hidden="true" />;
}
