# 🌍 EcoScan - Clothing Carbon Footprint Scanner

EcoScan lets you snap or upload a photo of your clothes, identifies each item,
estimates its carbon footprint, rewards eco-friendly choices with points, and
shows offers you can unlock with those points.

> 🚧 Work in progress: backend and frontend are complete, deployment is next.

## Contents
- [Tech stack](#-tech-stack)
- [Quick start](#-quick-start)
- [Backend setup](#-backend-setup)
- [Frontend setup](#-frontend-setup)
- [Running the tests](#-running-the-tests)
- [API reference](#-api-reference)
- [Carbon footprint assumptions](#-carbon-footprint-assumptions)
- [Code structure](#-code-structure)
- [Frontend](#-frontend)
- [Deployment](#-deployment)
- [Enhancements](#-enhancements)

## 🔧 Tech stack
- **Backend**: Python 3.10+, FastAPI, Pydantic
- **Image recognition**: an OpenAI vision model (default `gpt-4o-mini`), with a mock provider for development and tests
- **Frontend**: React 19 + TypeScript, Vite, Tailwind CSS v4
- **Tests**: pytest (backend), Vitest + React Testing Library (frontend)

## ⚡ Quick start

You need **Python 3.10+** and **Node.js 22.12+**. Run the backend and the frontend
in two terminals, from the repo root:

| Terminal 1: backend | Terminal 2: frontend |
|---|---|
| `cd backend` | `cd frontend` |
| create and activate a venv ([details](#-backend-setup)) | `npm install` |
| `pip install -r requirements.txt` | `npm run dev` |
| `copy .env.example .env` (Windows) or `cp .env.example .env` | |
| `uvicorn app.main:app --reload` | |

Then open **http://localhost:5173**. The frontend sends `/api` requests to the
backend on port 8000 through the Vite dev proxy, so no extra setup is needed.
Both run on the mock vision provider by default, without an API key.

### Local URLs

| URL | What |
|---|---|
| http://localhost:5173 | The EcoScan app |
| http://localhost:8000/docs | Interactive API docs (Swagger): try every endpoint in the browser |
| http://localhost:8000 | Redirects to `/docs` |
| http://localhost:8000/api/health | Health check, returns `{"status": "ok"}` |

## 🚀 Backend setup

All backend commands run from the `backend/` folder: that is where `.env` and `pytest.ini` are read from.

**Windows (PowerShell)**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

**macOS / Linux**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The default `.env` uses the **mock** vision provider, so the app runs without an API key.

### Environment variables (`backend/.env`)

| Variable | Default | What it does |
|---|---|---|
| `VISION_PROVIDER` | `mock` | `mock` (no key, predictable demo results), `openai` or `gemini` |
| `OPENAI_API_KEY` | *(empty)* | Required when `VISION_PROVIDER=openai`. Never commit it. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Any OpenAI model that accepts images and JSON mode |
| `OPENAI_TIMEOUT_SECONDS` | `30` | Timeout for one OpenAI request |
| `GEMINI_API_KEY` | *(empty)* | Required when `VISION_PROVIDER=gemini`. Get a free key in [Google AI Studio](https://aistudio.google.com/apikey). Never commit it. |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Any Gemini model that accepts images and JSON output |
| `GEMINI_TIMEOUT_SECONDS` | `30` | Timeout for one Gemini request |
| `MAX_IMAGE_MB` | `10` | Largest upload accepted (a safety net: the web app sends resized JPEGs, usually under 1 MB) |
| `POINTS_PER_KG` | `10` | Reward points per kg of CO2e saved |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins allowed to call the API (the Vite dev server) |

## 🎨 Frontend setup

Needs **Node.js 22.12 or newer** (22 LTS or later). The app itself runs on Node
20.19+, but Vitest and jsdom need 22.12+ for the tests.

```bash
cd frontend
npm install
npm run dev
```

The app opens at http://localhost:5173. Start the backend too (see [Quick start](#-quick-start)).

| Command | What it does |
|---|---|
| `npm run dev` | Dev server with hot reload, proxies `/api` to `http://localhost:8000` |
| `npm test` | Runs the tests once (`npm run test:watch` re-runs them on save) |
| `npm run build` | Type-checks (including tests) and builds to `frontend/dist` |
| `npm run lint` | Lints with oxlint |
| `npm run preview` | Serves the production build locally |

### Environment variables (`frontend/.env`, optional)

| Variable | Default | What it does |
|---|---|---|
| `VITE_API_URL` | `/api` | Where the app sends API requests. Leave it empty locally. Set it when the backend is deployed elsewhere, e.g. `https://ecoscan-api.example.com/api` |

**Trying it on your phone:** run `npm run dev -- --host` and open the "Network"
URL it prints on your phone (same Wi-Fi). "Take photo" uses the phone's own
camera app, so it works over plain HTTP. The desktop webcam view needs
`localhost` or HTTPS, as browsers require for camera access.

## 🧪 Running the tests

**Backend** (257 tests)
```bash
cd backend
pytest
```
Tests never call the real OpenAI or Gemini APIs: both providers are tested with a fake
client, and API tests replace the vision provider and settings through
FastAPI's `dependency_overrides`. They also ignore your local `.env`.

**Frontend** (40 tests)
```bash
cd frontend
npm test
```
Tests run in jsdom with React Testing Library. `fetch` and the API client are
mocked, so the backend does not need to be running. They cover client-side file
checks, resizing photos before upload, API error parsing, the results summary,
offers (including redeeming) and editing items before recalculating.

## 📡 API reference

All endpoints are under `/api`.

| Method | Path | Input | Output | Error codes |
|---|---|---|---|---|
| `GET` | `/api/health` | none | `{"status": "ok"}` | none |
| `POST` | `/api/analyze` | multipart form, field `file`: JPEG, PNG or WebP, max 10 MB | Items with carbon and points, totals, and offers | `400 empty_image`, `413 image_too_large`, `415 invalid_image`, `422 no_clothing_detected`, `422 validation_error`, `502 vision_service_error` |
| `POST` | `/api/score` | JSON `{"items": [{"category", "material", "condition", "confidence", "label"}]}`, at least one item (only `category` is required) | Items with carbon and points, and totals | `422 validation_error` |
| `GET` | `/api/offers?points=<int ≥ 0>` | Query `points` | `{"points", "eligible": [...], "locked": [... with points_needed]}` | `422 validation_error` |
| `GET` | `/api/carbon-factors` | none | The carbon tables below, as JSON | none |

`/api/score` exists so the user can correct what the scan detected (e.g. mark an
item as second-hand) and get a new score without uploading the photo again.

**Every error has the same shape**, so the frontend only needs to read `error.code`:
```json
{"error": {"code": "image_too_large", "message": "The image is too large. The limit is 10 MB."}}
```
Validation errors also include a `details` list showing which field is wrong.

**Image checks** for `/api/analyze`, in order: allowed content type → not empty →
within the size limit → the file's first bytes really are a JPEG, PNG or WebP
(so a `.txt` renamed to `.png` is rejected).

**The web app resizes photos before upload.** It accepts any image the browser
can decode (including HEIC on Safari), scales it so the longest side is at most
1600 px (never up), keeps the EXIF orientation, and uploads a JPEG at quality
0.85. A typical phone photo ends up well under 1 MB, so the API's size limit is
only a safety net. Originals over 30 MB are refused in the browser.

<details>
<summary>Example <code>/api/analyze</code> response (lists shortened)</summary>

```json
{
  "items": [
    {"category": "jeans", "material": "cotton", "condition": "second-hand", "confidence": 0.91,
     "label": "faded blue straight-leg jeans",
     "baseline_kg": 10.0, "actual_kg": 2.0, "saved_kg": 8.0, "points": 80}
  ],
  "total_carbon_kg": 2.0,
  "total_saved_kg": 8.0,
  "total_points": 80,
  "offers": {
    "points": 80,
    "eligible": [{"id": "swap-pass", "title": "Free clothing swap entry", "partner": "Swap Circle",
                  "description": "...", "points_required": 30}],
    "locked": [{"id": "repair-free", "title": "Free clothing repair", "partner": "StitchBack Repairs",
                "description": "...", "points_required": 100, "points_needed": 20}]
  }
}
```
</details>

## 🌱 Carbon footprint assumptions

> ⚠️ **These numbers are illustrative estimates for a demo, not audited
> life-cycle data.** They are in the right range for the brief's examples
> (T-shirt = 5 kg, Jeans = 10 kg) and are easy to replace (see [Code structure](#-code-structure)).

### Formula
```
baseline_kg = base_kg[category]                          the same item bought new, in a conventional material
actual_kg   = base_kg × material_factor × condition_factor
saved_kg    = baseline_kg − actual_kg                    never below 0
points      = saved_kg × 10                              rounded half up, per item (POINTS_PER_KG)
```

**Why reward savings, not low totals?** Most of a garment's footprint comes from
producing it: growing or making the fibre, dyeing and manufacturing. Buying
second-hand avoids almost all of that, and lower-impact materials avoid part of it.
Points reward the choice the user made compared with buying the same item new.

**Example:** second-hand jeans → `10 × 1.0 × 0.2 = 2 kg`, saved `10 − 2 = 8 kg` → **80 points**.

A higher-impact material (e.g. wool, factor 1.3) raises `actual_kg` but never gives negative savings or points.

### Base footprint per new item (kg CO2e)

| Group | Category (kg) |
|---|---|
| Tops | t-shirt 5 · shirt 6 · top 5 · crop top 4 · tank top 3 · sweater 12 · hoodie 11 |
| Bottoms | jeans 10 · trousers 9 · shorts 4 · skirt 6 · leggings 4 |
| One-piece and sets | dress 9 · tracksuit 14 · swimwear 3 · underwear 1.5 |
| Outerwear | jacket 15 · coat 20 · blazer 14 |
| Indian wear | saree 14 · kurta 7 · kurti 6 · lehenga 25 · salwar 6 · dupatta 4 · sherwani 20 |
| Footwear | shoes 8 · sneakers 14 · boots 16 · sandals 5 |
| Accessories | socks 1 · hat 2 · cap 1.5 · scarf 3 · gloves 2 · tie 1.5 · belt 3 · bag 8 |
| *Anything else* | **7** (default) |

Common synonyms are mapped to these categories, e.g. tee → t-shirt, denim → jeans,
trainers → sneakers, parka → coat, sari → saree, salwar kameez → salwar,
flip flops → sandals, jumper / cardigan → sweater. The longest matching name
wins, so "crop top" is not read as "top" and "yoga pants" is not read as "pants".

### Material factors (× base)

| Material | Factor | | Material | Factor |
|---|---|---|---|---|
| recycled cotton | 0.5 | | cotton | 1.0 |
| recycled polyester | 0.6 | | polyester | 1.0 |
| hemp | 0.6 | | nylon | 1.1 |
| organic cotton | 0.7 | | acrylic | 1.1 |
| lyocell / tencel | 0.7 | | wool | 1.3 |
| linen | 0.8 | | leather | 1.5 |
| | | | *unknown* | **1.0** |

The most specific match wins: "organic cotton" uses 0.7, not cotton's 1.0.

### Condition factors (× base)

| Condition | Factor | Why |
|---|---|---|
| new | 1.0 | Full production impact |
| second-hand | 0.2 | Assumes reuse avoids about 80% of the impact. The remaining 0.2 stands for shipping, washing and the item's share of its first life. |

"used", "thrifted", "vintage" and "pre-owned" all count as second-hand.

The live values are always available at `GET /api/carbon-factors`.

## 🏗️ Code structure

```
backend/
├── app/
│   ├── main.py              create_app(): CORS, error handlers, routes
│   ├── config.py            all settings, read from .env
│   ├── schemas.py           all Pydantic models (request and response shapes)
│   ├── errors.py            custom errors → {"error": {"code", "message"}}
│   ├── dependencies.py      wires repositories and services together
│   ├── api/routes.py        HTTP only: validate, call a service, return a schema
│   ├── services/            all business logic
│   │   ├── analysis.py          one scan: validate → detect → score → offers
│   │   ├── image_validation.py  type, size and file-signature checks
│   │   ├── carbon.py            carbon per item
│   │   ├── rewards.py           saved kg → points
│   │   ├── scoring.py           carbon + rewards → totals
│   │   ├── offers.py            eligible and locked offers
│   │   └── vision/              VisionProvider interface, mock, OpenAI and Gemini providers, shared prompt
│   └── data/                in-memory data behind repository interfaces
│       ├── carbon_factors.py    the carbon tables above
│       └── offers.py            demo offers
└── tests/                   unit tests per service + API tests
```

| Layer | Knows about | Does not know about |
|---|---|---|
| **routes** | HTTP, requests, responses | how anything is calculated |
| **services** | the business rules | HTTP, or where data is stored |
| **data** | the stored values | how they are used |
| **schemas** | the shape of every piece of data | everything else |

**Why it is built this way:**
- **Swap the data source easily.** Services read carbon factors and offers through
  small repository interfaces (`CarbonFactorRepository`, `OfferRepository`). To use
  a database or a live carbon API, write one new class with the same methods and
  change one line in `dependencies.py`. The carbon logic does not change.
- **Swap the AI model easily.** Everything depends on the `VisionProvider`
  interface (`detect_items(image, content_type) -> list[DetectedItem]`). Changing
  model means a new class plus one entry in `PROVIDERS`, chosen with `VISION_PROVIDER`.
- **Model output is never trusted blindly.** Both the OpenAI and Gemini providers send
  the same prompt (`vision/prompt.py`), and the reply must be JSON checked with Pydantic. Invalid items are skipped, and a broken reply becomes a clean `502`.
- **Easy to test.** Services get their dependencies through `__init__`, so tests
  pass in fakes. API tests swap dependencies with `dependency_overrides`.
- **No database**, as the brief requires: all data lives in memory.

## 🖥️ Frontend

A mobile-first single page: most people will scan clothes with a phone camera.

### Screenshots

<!-- Add screenshots to docs/screenshots/ and replace the placeholders below, e.g.
     ![Upload screen](docs/screenshots/upload.png) -->

| Upload | Results | Rewards |
|---|---|---|
| _Screenshot coming soon: upload or take a photo_ | _Screenshot coming soon: per-item carbon and points_ | _Screenshot coming soon: offers and progress_ |

### User flow
1. **Add a photo**: drag and drop, "Choose photo", or "Take photo" (the phone's
   camera, or a webcam view on desktop). The file type and size are checked
   before uploading.
2. **Scan**: a friendly loading message while the backend analyses the photo. The scan can be cancelled.
3. **Results**: totals for carbon, CO2 saved and points, then one card per item
   comparing its footprint with buying it new.
4. **Fix mistakes**: edit an item's type, material or condition, or remove it,
   then recalculate. This calls `/api/score` and `/api/offers`.
5. **Rewards**: offers ready to redeem, and progress bars for the rest.

Every backend error code has its own message, with "Try again" only where a retry can help.

### Frontend structure

```
frontend/src/
├── api/                 the only code that talks to the backend
│   ├── config.ts            API_BASE from VITE_API_URL (default "/api")
│   ├── types.ts             TypeScript versions of the backend schemas
│   └── client.ts            analyzeImage, scoreItems, getOffers, getCarbonFactors + ApiError
├── components/          small components, one job each
│   ├── ScanPanel.tsx        photo → preview → scan, with loading and errors
│   ├── PhotoPicker.tsx      drag and drop, choose photo, take photo
│   ├── CameraModal.tsx      desktop webcam capture
│   ├── ResultsView.tsx      summary, items, edit mode and offers
│   ├── EditItemsPanel.tsx   edit or remove items, then recalculate
│   ├── OffersSection.tsx    ready to redeem and almost there
│   └── ...                  cards, bars, badges, toast, error notice
├── lib/                 plain helpers: file checks, formatting, error wording
├── test/                test setup and shared fixtures
├── App.tsx              switches between the scan screen and the results
└── index.css            Tailwind and the design tokens
```

**Design decisions:**
- **API calls only in `src/api`.** Components never call `fetch`. Every failure becomes one `ApiError` with a `code`, so the UI handles errors in one way.
- **Types mirror the backend schemas**, so a renamed field is caught when you build, not by a user.
- **Design tokens in one place.** Colours and fonts live in `@theme` in `index.css`.
  Colours have a meaning across the app: clay = CO2, fern and moss = savings, ochre = points.
- **The backend has the final word.** The client repeats the file checks only to give faster
  feedback. Carbon and points always come from the API.
- **Accessible by default.** Real buttons and labels, a native `<dialog>` for the
  camera, `role="progressbar"`, `role="alert"` and `role="status"` for live updates.
  Tests find elements the same way a screen reader would.

## ☁️ Deployment
_To be added._

## 💡 Enhancements

Each idea builds on seams that already exist in the code: the repository
interfaces in `backend/app/data/`, the `VisionProvider` interface and its
`PROVIDERS` registry, the wiring in `dependencies.py`, and settings in `config.py`.

### Technical Scaling

- **Run several API instances behind a load balancer.** The API keeps no per-user state in memory (the data is read-only), so any instance can serve any request. Once users and points exist, they must live in the database (below), not in memory.
  *Why:* scale out by adding instances, with no sticky sessions.
- **Cache vision results by image hash (Redis).** Add a `CachingVisionProvider` that wraps the real provider: it looks up the SHA-256 of the image (plus model and prompt version) and calls OpenAI only on a miss. Register it in `PROVIDERS`; routes and services do not change. Cache carbon factors too once they come from a database or API (today `get_carbon_factors` is an in-process `lru_cache`).
  *Why:* the same photo should never pay for a second GPT call, and repeat scans become instant.
- **Move vision calls to a background queue.** `POST /api/analyze` returns `202` with a job id, a worker (e.g. Celery, RQ or arq) runs the `AnalysisService`, and the app polls `GET /api/analyze/{job_id}`. Keep `OPENAI_TIMEOUT_SECONDS` and add retries with backoff for `429` and `5xx` only.
  *Why:* slow model calls no longer tie up web workers, and spikes queue up instead of failing.
- **Postgres behind the existing repositories.** Write `PostgresCarbonFactors` and `PostgresOffers` with the same methods as `CarbonFactorRepository` and `OfferRepository`, swap them in `dependencies.py`, and add tables for users and an append-only **points ledger**. Keep images in object storage (e.g. S3) with a short retention period, or do not store them at all.
  *Why:* factors and offers can change without a deploy, and redeeming can really deduct points.
- **Protect and observe the API.** Add rate limiting per user and IP, strictest on `/api/analyze` because every call costs money. Add structured JSON logs with a request id, metrics (scan latency, vision error rate, cost per scan), error tracking (e.g. Sentry) on both apps, and CI that runs `pytest` and `npm test` on every push.
  *Why:* limits control cost and abuse, monitoring finds problems before users report them, and CI keeps `main` green.

### Product Improvements

- **A better carbon model.** Add material mix (e.g. 60% cotton and 40% polyester), garment weight or size, country of manufacture, brand data and expected lifetime (cost-per-wear: footprint ÷ expected wears), plus washing impact. Show a range (e.g. 4–7 kg) instead of one number. This extends `DetectedItem` and `CarbonFactorRepository`, and `CarbonService` keeps doing the maths.
  *Why:* one number per category hides most of the real difference between garments, and a range is more honest.
- **Real data through APIs.** Use an emission-factor API (e.g. Climatiq) behind `CarbonFactorRepository`, with a cache and the in-memory tables as a fallback. Use brand or retailer product data for materials and weights. Use partner offer APIs behind `OfferRepository`, so that "Redeem" returns a real code.
  *Why:* numbers and offers stay current without code changes.
- **Read the care label.** Add an optional second photo of the label. Its text (OCR, or the vision model) gives the exact materials and percentages.
  *Why:* the label is far more accurate than guessing the material from a photo.
- **Make the impact tangible and keep users coming back.**
  - Comparisons such as "8 kg CO2 saved ≈ N km not driven".
  - A wardrobe history across scans.
  - Streaks and badges.
  - A shareable scan card.
  - Accounts with a points history, built on the points ledger.

  *Why:* kilograms of CO2 are abstract, and progress over time is what changes habits.
- **Learn from user corrections.** Users can already fix items before recalculating (`EditItemsPanel` → `/api/score`). With consent, log the detected item next to the corrected one. Use these pairs to measure accuracy, add missing words to `CATEGORY_ALIASES`, tune the prompt, and later fine-tune a model.
  *Why:* every correction becomes free training and evaluation data.
