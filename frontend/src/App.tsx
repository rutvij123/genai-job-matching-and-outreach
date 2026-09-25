import { useRef } from "react";

import { ApiStatus } from "./components/ApiStatus";
import { Letter } from "./components/Letter";
import { MatchList } from "./components/MatchList";
import { Progress } from "./components/Progress";
import { RunForm } from "./components/RunForm";
import { useOutreach } from "./hooks/useOutreach";

export default function App() {
  const { status, result, selected, email, run, select, rewrite } = useOutreach();
  const busy = status.kind === "running";
  const letterRef = useRef<HTMLDivElement>(null);

  function handleSelect(index: number) {
    select(index);
    // In the single-column layout the email sits below the list, so bring it into view
    if (!window.matchMedia?.("(min-width: 80rem)").matches) {
      const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
      letterRef.current?.scrollIntoView?.({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-rule bg-paper">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-5 py-4 sm:px-8">
          <h1 className="text-lg font-semibold">Job match & outreach</h1>
          <ApiStatus />
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-10 px-5 py-8 sm:px-8 lg:grid-cols-[21rem_minmax(0,1fr)]">
        <aside className="lg:sticky lg:top-8 lg:self-start">
          <p className="mb-6 max-w-prose text-[15px] leading-relaxed text-muted">
            Give it a company's careers page and your resume. It ranks the open roles by fit and
            drafts a cold email for the one you choose.
          </p>
          <RunForm busy={busy} onSubmit={run} />
          <Progress status={status} />
        </aside>

        <div aria-live="polite">
          {!result && <EmptyState running={busy} />}

          {result && result.matches.length === 0 && (
            <p className="max-w-prose text-muted">
              No job postings were found on that page. Try the page that lists the openings
              directly, since sites that load jobs with JavaScript can come back empty.
            </p>
          )}

          {result && result.matches.length > 0 && (
            <div className="grid gap-10 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
              <MatchList
                matches={result.matches}
                jobsFound={result.jobsFound}
                selected={selected}
                onSelect={handleSelect}
              />
              <div ref={letterRef} className="scroll-mt-6">
                <Letter email={email} onRewrite={rewrite} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function EmptyState({ running }: { running: boolean }) {
  return (
    <div className="grid min-h-64 place-items-center rounded-md border border-dashed border-rule px-6 py-16 text-center">
      <p className="max-w-sm text-muted">
        {running
          ? "Matches will appear here once the jobs are ranked."
          : "Your ranked matches and email draft will appear here."}
      </p>
    </div>
  );
}
