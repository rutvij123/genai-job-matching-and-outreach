import { describe, expect, it } from "vitest";

import { slugify, splitEmail } from "./email";

describe("splitEmail", () => {
  it("splits the subject line from the body", () => {
    expect(splitEmail("Subject: Hello there\n\nDear team,\nThanks")).toEqual({
      subject: "Hello there",
      body: "Dear team,\nThanks",
    });
  });

  it("returns the whole text as body when there is no subject", () => {
    expect(splitEmail("  Dear team  ")).toEqual({ subject: null, body: "Dear team" });
  });
});

describe("slugify", () => {
  it("makes a filename-safe slug", () => {
    expect(slugify("Sr. Data Engineer (Remote)")).toBe("sr-data-engineer-remote");
    expect(slugify("!!!")).toBe("email");
  });
});
