// Aliases over the types generated from the FastAPI OpenAPI schema (`npm run gen:api`).
import type { components } from "./schema";

type Schemas = components["schemas"];

export type Job = Schemas["Job"];
export type Match = Schemas["Match"];
export type MatchResponse = Schemas["MatchResponse"];
export type ResumeResponse = Schemas["ResumeResponse"];
export type EmailRequest = Schemas["EmailRequest"];
export type EmailResponse = Schemas["EmailResponse"];
export type HealthResponse = Schemas["HealthResponse"];
