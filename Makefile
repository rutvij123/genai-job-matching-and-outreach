.PHONY: install test lint format api openapi web web-install web-test web-lint up down

# Backend
install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check . && ruff format --check .

format:
	ruff check --fix . && ruff format .

api:
	uvicorn job_outreach.api.main:app --reload

# Regenerate the OpenAPI schema and the frontend's TypeScript types after changing the API
openapi:
	python scripts/export_openapi.py
	cd frontend && npm run gen:api

# Frontend
web-install:
	cd frontend && npm ci

web:
	cd frontend && npm run dev

web-test:
	cd frontend && npm test

web-lint:
	cd frontend && npm run lint && npm run typecheck

# Everything
up:
	docker compose up --build

down:
	docker compose down
