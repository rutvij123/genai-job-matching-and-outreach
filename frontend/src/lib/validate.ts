export const MAX_RESUME_MB = 5;

export function validateUrl(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) return "Enter the careers page URL.";
  try {
    const url = new URL(trimmed);
    if (url.protocol !== "http:" && url.protocol !== "https:") throw new Error();
  } catch {
    return "Enter a full URL starting with https://";
  }
  return null;
}

export function validateResume(file: File | null): string | null {
  if (!file) return "Choose your resume.";
  if (!file.name.toLowerCase().endsWith(".pdf")) return "Your resume needs to be a PDF.";
  if (file.size > MAX_RESUME_MB * 1024 * 1024) return `Keep the PDF under ${MAX_RESUME_MB} MB.`;
  return null;
}
