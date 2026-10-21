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
10 feat(backend): OpenAI vision provider with strict JSON parsing
11 feat(backend): custom errors and JSON error handlers
12 feat(backend): /analyze endpoint with image validation (jpeg/png/webp, ≤5MB, not empty)
13 feat(backend): /score, /offers and /carbon-factors endpoints
14 test(backend): API tests using mock vision via dependency override
15 docs: backend setup, assumptions and API reference in README

## Working rules
- Small commits: one commit = one step above. Never combine steps.
- Every step: write code + tests, run `pytest` from backend/, all must pass.
- Before committing, show me the diff and explain what and why in simple Hinglish.
- Do not commit or push until I say "ok commit".
- Never commit .env or real API keys.