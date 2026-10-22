# EcoScan – project rules for Claude

## Context
Reewild take-home: clothing carbon footprint scanner. Backend = FastAPI (backend/),
frontend = React + Vite + TypeScript (frontend/). The brief is in docs/brief.md.
Setup and design decisions are in README.md.

## Architecture (follow strictly)
- api/routes.py: HTTP only. Validate, call a service, return a schema. No logic.
- services/: all business logic. Services get their dependencies via __init__.
- data/: in-memory values behind repository classes (Protocol + InMemory impl).
- schemas.py: all Pydantic models. config.py: all settings from .env.

Frontend rules:
- TypeScript.
- Small components in src/components.
- API calls only in src/api.
- Mobile-first (camera is mostly used on phones).

## Status
Project: complete. Not deployed; runs locally (README → Deployment).

Backend: done. 300 pytest tests pass. Endpoints:
- GET  /                     the built frontend (frontend/dist), if it exists
- GET  /api/health
- POST /api/analyze          image upload -> items, carbon, points, offers
- POST /api/score            edited items -> carbon and points
- GET  /api/offers?points=   eligible and locked offers
- GET  /api/carbon-factors   the carbon assumptions
Vision: mock (default), OpenAI or Gemini, chosen with VISION_PROVIDER.

Frontend: done (F1–F9). 48 Vitest tests pass. Upload or camera capture
(resized to a JPEG in the browser), results per item, edit and rescore, offers with progress, loading and error states.

README: done (setup, tests, API, carbon assumptions, eco tips, structure,
screenshots in docs/screenshots/, deployment plan, enhancements).

## Working rules
- Small commits: one commit = one step. Never combine steps.
- Every step: write code + tests, run `pytest` from backend/, all must pass.
- Frontend steps: run npm run build and npm test in frontend/.
- Before committing, show me the diff and explain what and why in simple English.
- Do not commit or push until I say "ok commit".
- Never commit .env or real API keys.
