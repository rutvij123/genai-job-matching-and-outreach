import type { MatchResponse } from "../api/types";

export const MATCHES: MatchResponse = {
  jobs_found: 7,
  matches: [
    {
      rank: 1,
      score: 0.82,
      job: {
        role: "Data Engineer",
        experience: "3+ years",
        skills: ["python", "spark"],
        description: "Build Spark pipelines.",
      },
    },
    {
      rank: 2,
      score: 0.61,
      job: { role: "Analytics Engineer", experience: "", skills: [], description: "" },
    },
  ],
};

export function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/** Routes fetch calls by path so tests read like a fake backend. */
export function mockApi(routes: Record<string, (init?: RequestInit) => Response | Promise<Response>>) {
  return async (input: RequestInfo | URL, init?: RequestInit) => {
    const path = new URL(String(input), "http://localhost").pathname;
    const handler = routes[path];
    if (!handler) throw new Error(`Unexpected request to ${path}`);
    return handler(init);
  };
}
