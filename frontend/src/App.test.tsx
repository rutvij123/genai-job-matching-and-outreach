import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import App from "./App";
import { MATCHES, jsonResponse, mockApi } from "./test/fixtures";

const resumeFile = new File(["%PDF-1.4"], "resume.pdf", { type: "application/pdf" });

async function submitForm() {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/careers page/i), "https://acme.com/careers");
  await user.upload(screen.getByLabelText(/resume/i), resumeFile);
  await user.type(screen.getByLabelText(/sign the email as/i), "Ritz");
  await user.click(screen.getByRole("button", { name: /find matches/i }));
  return user;
}

describe("App", () => {
  it("runs the full flow and lets the user re-draft for another match", async () => {
    const emailBodies: unknown[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(
        mockApi({
          "/health": () => jsonResponse({ status: "ok", version: "0.2.0", llm_configured: true }),
          "/api/v1/resume/parse": () => jsonResponse({ chars: 900, text: "Resume text ".repeat(20) }),
          "/api/v1/match": () => jsonResponse(MATCHES),
          "/api/v1/emails": (init) => {
            const body = JSON.parse(String(init?.body));
            emailBodies.push(body);
            return jsonResponse({ email: `Subject: About ${body.job.role}\n\nHello from Ritz.` });
          },
        }),
      ),
    );

    render(<App />);
    expect(await screen.findByText("API connected")).toBeInTheDocument();
    const user = await submitForm();

    expect(await screen.findByRole("heading", { name: "About Data Engineer" })).toBeInTheDocument();
    expect(screen.getByText(/top 2 of 7 openings/i)).toBeInTheDocument();
    expect(emailBodies[0]).toMatchObject({ candidate_name: "Ritz", job: { role: "Data Engineer" } });

    const matches = screen.getByRole("region", { name: "Best fits" });
    await user.click(within(matches).getByRole("button", { name: /analytics engineer/i }));

    expect(
      await screen.findByRole("heading", { name: "About Analytics Engineer" }),
    ).toBeInTheDocument();
    expect(emailBodies).toHaveLength(2);
  });

  it("validates inputs before calling the API", async () => {
    const fetchMock = vi.fn(
      mockApi({ "/health": () => jsonResponse({ status: "ok", version: "0", llm_configured: true }) }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    render(<App />);
    await user.click(screen.getByRole("button", { name: /find matches/i }));

    expect(screen.getByText(/enter the careers page url/i)).toBeInTheDocument();
    expect(screen.getByText(/choose your resume/i)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1); // only the health check
  });

  it("shows the API error and which step failed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        mockApi({
          "/health": () => jsonResponse({ status: "ok", version: "0", llm_configured: true }),
          "/api/v1/resume/parse": () => jsonResponse({ chars: 900, text: "Resume" }),
          "/api/v1/match": () =>
            jsonResponse({ detail: "Page returned no visible text", error: "ScrapeError" }, 502),
        }),
      ),
    );

    render(<App />);
    await submitForm();

    expect(await screen.findByRole("alert")).toHaveTextContent("Page returned no visible text");
    const failedStep = screen.getByText("Finding and ranking jobs");
    expect(failedStep).toHaveClass("text-error");
  });
});
