import type { Match } from "../api/types";

interface Props {
  matches: Match[];
  jobsFound: number;
  selected: number;
  onSelect: (index: number) => void;
}

export function MatchList({ matches, jobsFound, selected, onSelect }: Props) {
  return (
    <section aria-labelledby="matches-heading">
      <h2 id="matches-heading" className="text-lg font-semibold">
        Best fits
      </h2>
      <p className="mt-1 text-sm text-muted">
        Top {matches.length} of {jobsFound} {jobsFound === 1 ? "opening" : "openings"}, ranked by
        how closely each matches your resume. Pick one to write its email.
      </p>

      <ol className="mt-4 divide-y divide-rule border-y border-rule">
        {matches.map((m, i) => {
          const isSelected = i === selected;
          const pct = Math.round(Math.max(0, Math.min(1, m.score)) * 100);
          const skills = m.job.skills ?? [];
          return (
            <li key={`${m.rank}-${m.job.role}`}>
              <button
                type="button"
                onClick={() => onSelect(i)}
                aria-pressed={isSelected}
                className={
                  "grid w-full grid-cols-[1.75rem_1fr_auto] items-start gap-x-3 px-2 py-3.5 text-left " +
                  (isSelected ? "bg-cobalt-wash" : "hover:bg-paper")
                }
              >
                <span className="pt-0.5 text-sm tabular-nums text-muted">{m.rank}</span>
                <span className="min-w-0">
                  <span className="block font-medium leading-snug">
                    {m.job.role || "Untitled role"}
                  </span>
                  {m.job.experience && (
                    <span className="mt-0.5 block text-sm text-muted">{m.job.experience}</span>
                  )}
                </span>
                <span className="flex w-24 flex-col items-end gap-1.5 pt-1">
                  <span className="text-sm tabular-nums">{pct}% fit</span>
                  <span className="h-1.5 w-full overflow-hidden rounded-full bg-rule" aria-hidden="true">
                    <span className="block h-full rounded-full bg-cobalt" style={{ width: `${pct}%` }} />
                  </span>
                </span>
              </button>

              {isSelected && (skills.length > 0 || m.job.description) && (
                <div className="bg-cobalt-wash px-2 pb-4 pl-[2.75rem] text-sm">
                  {skills.length > 0 && (
                    <ul className="flex flex-wrap gap-1.5" aria-label="Skills">
                      {skills.map((s) => (
                        <li key={s} className="rounded bg-paper px-2 py-0.5 text-ink">
                          {s}
                        </li>
                      ))}
                    </ul>
                  )}
                  {m.job.description && (
                    <p className="mt-2.5 max-w-prose leading-relaxed text-muted">
                      {m.job.description}
                    </p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
