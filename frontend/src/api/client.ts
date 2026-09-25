import type {
  EmailRequest,
  EmailResponse,
  HealthResponse,
  MatchResponse,
  ResumeResponse,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function readErrorMessage(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json();
    const detail = (body as { detail?: unknown })?.detail;
    if (typeof detail === "string") return detail;
    // FastAPI validation errors: [{ loc, msg, type }, ...]
    if (Array.isArray(detail)) {
      return detail
        .map((d) => (typeof d?.msg === "string" ? d.msg : ""))
        .filter(Boolean)
        .join("; ");
    }
  } catch {
    // body wasn't JSON
  }
  return `Request failed with status ${res.status}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(0, "Can't reach the API. Check that the backend is running.");
  }
  if (!res.ok) throw new ApiError(res.status, await readErrorMessage(res));
  return (await res.json()) as T;
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  parseResume(resume: File) {
    const form = new FormData();
    form.append("resume", resume);
    return request<ResumeResponse>("/api/v1/resume/parse", { method: "POST", body: form });
  },

  match(url: string, resume: File, topK: number) {
    const form = new FormData();
    form.append("url", url);
    form.append("resume", resume);
    form.append("top_k", String(topK));
    return request<MatchResponse>("/api/v1/match", { method: "POST", body: form });
  },

  writeEmail(body: EmailRequest) {
    return request<EmailResponse>("/api/v1/emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
};

export function errorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  return "Something went wrong.";
}
