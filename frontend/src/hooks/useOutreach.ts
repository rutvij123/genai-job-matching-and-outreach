import { useCallback, useRef, useState } from "react";

import { api, errorMessage } from "../api/client";
import type { Match } from "../api/types";

export type Step = "resume" | "match" | "email";

export interface RunInput {
  url: string;
  resume: File;
  topK: number;
  name: string;
}

export type RunStatus =
  | { kind: "idle" }
  | { kind: "running"; step: Step }
  | { kind: "done" }
  | { kind: "error"; step: Step; message: string };

export type EmailState =
  | { kind: "empty" }
  | { kind: "writing"; match: Match }
  | { kind: "ready"; match: Match; text: string }
  | { kind: "error"; match: Match; message: string };

export interface RunResult {
  jobsFound: number;
  matches: Match[];
  resumeText: string;
  name: string;
}

/**
 * Drives the three API calls (parse resume → match → write email) and lets the user
 * re-draft the email for any other match. Stale responses from an earlier run or an
 * earlier email request are ignored.
 */
export function useOutreach() {
  const [status, setStatus] = useState<RunStatus>({ kind: "idle" });
  const [result, setResult] = useState<RunResult | null>(null);
  const [selected, setSelected] = useState(0);
  const [email, setEmail] = useState<EmailState>({ kind: "empty" });
  const runId = useRef(0);
  const emailId = useRef(0);

  const draft = useCallback(async (res: RunResult, index: number) => {
    const id = ++emailId.current;
    const match = res.matches[index];
    setEmail({ kind: "writing", match });
    try {
      const { email: text } = await api.writeEmail({
        job: match.job,
        resume_text: res.resumeText,
        candidate_name: res.name || null,
      });
      if (emailId.current === id) setEmail({ kind: "ready", match, text });
    } catch (err) {
      if (emailId.current === id) setEmail({ kind: "error", match, message: errorMessage(err) });
    }
  }, []);

  const run = useCallback(
    async (input: RunInput) => {
      const id = ++runId.current;
      emailId.current++;
      setResult(null);
      setSelected(0);
      setEmail({ kind: "empty" });

      let step: Step = "resume";
      const isCurrent = () => runId.current === id;
      try {
        setStatus({ kind: "running", step });
        const { text } = await api.parseResume(input.resume);
        if (!isCurrent()) return;

        step = "match";
        setStatus({ kind: "running", step });
        const matched = await api.match(input.url.trim(), input.resume, input.topK);
        if (!isCurrent()) return;

        const res: RunResult = {
          jobsFound: matched.jobs_found,
          matches: matched.matches,
          resumeText: text,
          name: input.name.trim(),
        };
        setResult(res);

        if (res.matches.length > 0) {
          step = "email";
          setStatus({ kind: "running", step });
          await draft(res, 0);
          if (!isCurrent()) return;
        }
        setStatus({ kind: "done" });
      } catch (err) {
        if (isCurrent()) setStatus({ kind: "error", step, message: errorMessage(err) });
      }
    },
    [draft],
  );

  const select = useCallback(
    (index: number) => {
      if (!result) return;
      setSelected(index);
      void draft(result, index);
    },
    [draft, result],
  );

  const rewrite = useCallback(() => {
    if (result) void draft(result, selected);
  }, [draft, result, selected]);

  return { status, result, selected, email, run, select, rewrite };
}
