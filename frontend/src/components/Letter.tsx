import { useState } from "react";

import type { EmailState } from "../hooks/useOutreach";
import { slugify, splitEmail } from "../lib/email";

interface Props {
  email: EmailState;
  onRewrite: () => void;
}

const actionClass =
  "rounded-md border border-rule bg-paper px-3 py-1.5 text-sm font-medium hover:bg-desk " +
  "disabled:cursor-not-allowed disabled:opacity-50";

export function Letter({ email, onRewrite }: Props) {
  const [copied, setCopied] = useState(false);
  if (email.kind === "empty") return null;

  const role = email.match.job.role || "this role";
  const text = email.kind === "ready" ? email.text : "";
  const parts = splitEmail(text);

  async function copy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function download() {
    const url = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `email-${slugify(role)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section aria-labelledby="letter-heading" aria-busy={email.kind === "writing"}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="letter-heading" className="text-lg font-semibold">
          Your email
        </h2>
        <div className="flex gap-2">
          <button type="button" onClick={copy} disabled={email.kind !== "ready"} className={actionClass}>
            {copied ? "Copied" : "Copy email"}
          </button>
          <button type="button" onClick={download} disabled={email.kind !== "ready"} className={actionClass}>
            Download .txt
          </button>
          <button
            type="button"
            onClick={onRewrite}
            disabled={email.kind === "writing"}
            className={actionClass}
          >
            Rewrite
          </button>
        </div>
      </div>

      <article className="mt-4 rounded-sm bg-paper px-7 py-8 shadow-[0_1px_2px_rgba(23,32,51,0.08),0_8px_24px_-12px_rgba(23,32,51,0.18)] sm:px-12 sm:py-11">
        <p className="text-sm text-muted">To the hiring manager for {role}</p>

        {email.kind === "writing" && (
          <div className="mt-6 space-y-3" aria-label="Writing email">
            <p className="text-muted">Writing an email for {role}…</p>
            {[92, 100, 85, 97, 60].map((w, i) => (
              <div key={i} className="h-3 animate-pulse rounded bg-desk" style={{ width: `${w}%` }} />
            ))}
          </div>
        )}

        {email.kind === "error" && (
          <p role="alert" className="mt-6 text-error">
            {email.message} Try Rewrite, or pick another job.
          </p>
        )}

        {email.kind === "ready" && (
          <>
            {parts.subject && (
              <h3 className="mt-3 border-b border-rule pb-4 text-xl font-semibold leading-snug">
                {parts.subject}
              </h3>
            )}
            <div className="mt-6 max-w-[62ch] whitespace-pre-wrap font-serif text-[17px] leading-[1.7]">
              {parts.body}
            </div>
          </>
        )}
      </article>
    </section>
  );
}
