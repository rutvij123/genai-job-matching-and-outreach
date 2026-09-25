import { type FormEvent, useId, useState } from "react";

import type { RunInput } from "../hooks/useOutreach";
import { validateResume, validateUrl } from "../lib/validate";

interface Props {
  busy: boolean;
  onSubmit: (input: RunInput) => void;
}

interface Errors {
  url?: string | null;
  resume?: string | null;
}

const inputClass =
  "mt-1.5 block w-full rounded-md border border-rule bg-paper px-3 py-2 text-[15px] " +
  "placeholder:text-muted/70 focus:border-cobalt focus:outline-none focus:ring-2 focus:ring-cobalt/25 " +
  "aria-invalid:border-error";

export function RunForm({ busy, onSubmit }: Props) {
  const id = useId();
  const [url, setUrl] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [topK, setTopK] = useState(5);
  const [name, setName] = useState("");
  const [errors, setErrors] = useState<Errors>({});

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const next = { url: validateUrl(url), resume: validateResume(resume) };
    setErrors(next);
    if (next.url || next.resume || !resume) return;
    onSubmit({ url, resume, topK, name });
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-5">
      <div>
        <label htmlFor={`${id}-url`} className="text-sm font-medium">
          Careers page
        </label>
        <input
          id={`${id}-url`}
          type="url"
          inputMode="url"
          placeholder="https://company.com/careers"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          aria-invalid={!!errors.url}
          aria-describedby={errors.url ? `${id}-url-error` : undefined}
          className={inputClass}
        />
        {errors.url && (
          <p id={`${id}-url-error`} className="mt-1.5 text-sm text-error">
            {errors.url}
          </p>
        )}
      </div>

      <div>
        <label htmlFor={`${id}-resume`} className="text-sm font-medium">
          Resume (PDF)
        </label>
        <input
          id={`${id}-resume`}
          type="file"
          accept="application/pdf,.pdf"
          onChange={(e) => setResume(e.target.files?.[0] ?? null)}
          aria-invalid={!!errors.resume}
          aria-describedby={errors.resume ? `${id}-resume-error` : undefined}
          className={
            "mt-1.5 block w-full text-sm text-muted file:mr-3 file:rounded-md file:border " +
            "file:border-rule file:bg-paper file:px-3 file:py-2 file:text-sm file:font-medium " +
            "file:text-ink hover:file:bg-desk"
          }
        />
        {errors.resume && (
          <p id={`${id}-resume-error`} className="mt-1.5 text-sm text-error">
            {errors.resume}
          </p>
        )}
      </div>

      <div className="grid grid-cols-[1fr_6rem] gap-3">
        <div>
          <label htmlFor={`${id}-name`} className="text-sm font-medium">
            Sign the email as
          </label>
          <input
            id={`${id}-name`}
            type="text"
            autoComplete="name"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={inputClass}
          />
        </div>
        <div>
          <label htmlFor={`${id}-topk`} className="text-sm font-medium">
            Matches
          </label>
          <input
            id={`${id}-topk`}
            type="number"
            min={1}
            max={20}
            value={topK}
            onChange={(e) => setTopK(Math.min(20, Math.max(1, Number(e.target.value) || 1)))}
            className={inputClass}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={busy}
        className={
          "w-full rounded-md bg-cobalt px-4 py-2.5 text-[15px] font-medium text-white " +
          "hover:bg-cobalt-dark disabled:cursor-not-allowed disabled:opacity-60"
        }
      >
        {busy ? "Working…" : "Find matches"}
      </button>
    </form>
  );
}
