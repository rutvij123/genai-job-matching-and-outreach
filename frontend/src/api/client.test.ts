import { describe, expect, it, vi } from "vitest";

import { jsonResponse } from "../test/fixtures";
import { ApiError, api } from "./client";

describe("api client", () => {
  it("surfaces the API's error detail", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ detail: "blocked" }, 502)));
    await expect(api.health()).rejects.toMatchObject({ status: 502, message: "blocked" });
  });

  it("joins FastAPI validation errors", async () => {
    const detail = [{ msg: "field required" }, { msg: "bad url" }];
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ detail }, 422)));
    await expect(api.health()).rejects.toThrow("field required; bad url");
  });

  it("reports network failures clearly", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    const err = await api.health().catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(0);
    expect(err.message).toMatch(/can't reach the api/i);
  });

  it("sends the resume and options as multipart form data", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ jobs_found: 0, matches: [] }));
    vi.stubGlobal("fetch", fetchMock);
    const file = new File(["%PDF"], "cv.pdf");
    await api.match("https://acme.com/jobs", file, 3);

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/match");
    const body = init.body as FormData;
    expect(body.get("url")).toBe("https://acme.com/jobs");
    expect(body.get("top_k")).toBe("3");
    expect(body.get("resume")).toBeInstanceOf(File);
  });
});
