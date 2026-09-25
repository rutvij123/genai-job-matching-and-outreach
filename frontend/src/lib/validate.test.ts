import { describe, expect, it } from "vitest";

import { validateResume, validateUrl } from "./validate";

describe("validateUrl", () => {
  it("accepts http(s) URLs", () => {
    expect(validateUrl("https://acme.com/careers")).toBeNull();
  });

  it("rejects empty, partial and non-http values", () => {
    expect(validateUrl("")).toMatch(/enter the careers page/i);
    expect(validateUrl("acme.com")).toMatch(/full url/i);
    expect(validateUrl("ftp://acme.com")).toMatch(/full url/i);
  });
});

describe("validateResume", () => {
  it("requires a PDF under the size limit", () => {
    expect(validateResume(null)).toMatch(/choose/i);
    expect(validateResume(new File(["x"], "cv.docx"))).toMatch(/pdf/i);
    expect(validateResume(new File([new Uint8Array(6 * 1024 * 1024)], "cv.pdf"))).toMatch(/5 MB/);
    expect(validateResume(new File(["x"], "CV.PDF"))).toBeNull();
  });
});
