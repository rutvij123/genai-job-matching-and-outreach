export interface EmailParts {
  subject: string | null;
  body: string;
}

/** The API asks the LLM to put "Subject: ..." on the first line. Split it off if present. */
export function splitEmail(text: string): EmailParts {
  const match = text.match(/^\s*subject:\s*(.+?)\s*(?:\r?\n)+/i);
  if (!match) return { subject: null, body: text.trim() };
  return { subject: match[1], body: text.slice(match[0].length).trim() };
}

export function slugify(text: string): string {
  return (
    text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "") || "email"
  );
}
