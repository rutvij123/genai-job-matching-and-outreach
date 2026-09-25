"""Write the API's OpenAPI schema to frontend/openapi.json (source for the TS types)."""

import json
from pathlib import Path

from job_outreach.api.main import app

out = Path(__file__).resolve().parents[1] / "frontend" / "openapi.json"
out.write_text(json.dumps(app.openapi(), indent=2) + "\n")
print(f"wrote {out}")
