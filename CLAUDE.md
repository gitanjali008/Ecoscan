# EcoScan – project rules for Claude

## Context
Reewild take-home: clothing carbon footprint scanner. Backend = FastAPI (backend/),
frontend = React + Vite (frontend/, not built yet). The brief is in docs/brief.md.

## Architecture (follow strictly)
- api/routes.py: HTTP only. Validate, call a service, return a schema. No logic.
- services/: all business logic. Services get their dependencies via __init__.
- data/: in-memory values behind repository classes (Protocol + InMemory impl).
- schemas.py: all Pydantic models. config.py: all settings from .env.

## Done so far (commits 1–8)
Skeleton + /api/health, schemas, carbon factors repo, CarbonService,
RewardsService, ScoringService, offers repo + OffersService. 49 tests pass.

## Remaining backend commits (one at a time)
9  feat(backend): vision provider interface and mock provider
10 feat(backend): custom errors and JSON error handlers
11 feat(backend): OpenAI vision provider with strict JSON parsing
12 feat(backend): dependencies and /analyze endpoint with image validation
13 feat(backend): /score, /offers and /carbon-factors endpoints
14 test(backend): API tests using dependency overrides
15 docs: backend setup, assumptions and API reference in README

## Frontend plan (one at a time)
F1 chore(frontend): scaffold Vite + React + TypeScript (done, commit 4f3a523)
F2 chore(frontend): Tailwind, Vite proxy /api -> localhost:8000, clean template
F3 feat(frontend): types and API client for backend endpoints
F4 feat(frontend): image upload and camera capture
F5 feat(frontend): scan results with per-item carbon and points
F6 feat(frontend): offers with progress to unlock
F7 feat(frontend): edit items and rescore, loading and error states
F8 test(frontend): Vitest + Testing Library tests
F9 docs: frontend setup and full run guide in README

Frontend rules:
- TypeScript.
- Small components in src/components.
- API calls only in src/api.
- Mobile-first (camera is mostly used on phones).

## Working rules
- Small commits: one commit = one step above. Never combine steps.
- Every step: write code + tests, run `pytest` from backend/, all must pass.
- Frontend steps: run npm run build in frontend/ (and npm test from F8 onwards)
- Before committing, show me the diff and explain what and why in simple Hinglish.
- Do not commit or push until I say "ok commit".
- Never commit .env or real API keys.