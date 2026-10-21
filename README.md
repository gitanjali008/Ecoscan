# 🌍 EcoScan - Clothing Carbon Footprint Scanner

EcoScan lets you snap or upload a photo of your clothes, identifies each item,
estimates its carbon footprint, rewards eco-friendly choices with points, and
shows offers you can unlock with those points.

> 🚧 Work in progress: the backend is complete, the frontend is next.

## Contents
- [Tech stack](#-tech-stack)
- [Backend setup](#-backend-setup)
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
- **Frontend**: React + Vite
- **Tests**: pytest

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
| `VISION_PROVIDER` | `mock` | `mock` (no key, predictable demo results) or `openai` |
| `OPENAI_API_KEY` | *(empty)* | Required when `VISION_PROVIDER=openai`. Never commit it. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Any OpenAI model that accepts images and JSON mode |
| `OPENAI_TIMEOUT_SECONDS` | `30` | Timeout for one OpenAI request |
| `MAX_IMAGE_MB` | `5` | Largest upload accepted |
| `POINTS_PER_KG` | `10` | Reward points per kg of CO2e saved |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins allowed to call the API (the Vite dev server) |

### Local URLs

| URL | What |
|---|---|
| http://localhost:8000/docs | Interactive API docs (Swagger): try every endpoint in the browser |
| http://localhost:8000/api/health | Health check, returns `{"status": "ok"}` |

## 🧪 Running the tests
```bash
cd backend
pytest
```
Tests never call the real OpenAI API: the OpenAI provider is tested with a fake
client, and API tests replace the vision provider and settings through
FastAPI's `dependency_overrides`. They also ignore your local `.env`.

## 📡 API reference

All endpoints are under `/api`.

| Method | Path | Input | Output | Error codes |
|---|---|---|---|---|
| `GET` | `/api/health` | none | `{"status": "ok"}` | none |
| `POST` | `/api/analyze` | multipart form, field `file`: JPEG, PNG or WebP, max 5 MB | Items with carbon and points, totals, and offers | `400 empty_image`, `413 image_too_large`, `415 invalid_image`, `422 no_clothing_detected`, `422 validation_error`, `502 vision_service_error` |
| `POST` | `/api/score` | JSON `{"items": [{"category", "material", "condition", "confidence"}]}`, at least one item | Items with carbon and points, and totals | `422 validation_error` |
| `GET` | `/api/offers?points=<int ≥ 0>` | Query `points` | `{"points", "eligible": [...], "locked": [... with points_needed]}` | `422 validation_error` |
| `GET` | `/api/carbon-factors` | none | The carbon tables below, as JSON | none |

`/api/score` exists so the user can correct what the scan detected (e.g. mark an
item as second-hand) and get a new score without uploading the photo again.

**Every error has the same shape**, so the frontend only needs to read `error.code`:
```json
{"error": {"code": "image_too_large", "message": "The image is too large. The limit is 5 MB."}}
```
Validation errors also include a `details` list showing which field is wrong.

**Image checks** for `/api/analyze`, in order: allowed content type → not empty →
within the size limit → the file's first bytes really are a JPEG, PNG or WebP
(so a `.txt` renamed to `.png` is rejected).

<details>
<summary>Example <code>/api/analyze</code> response (lists shortened)</summary>

```json
{
  "items": [
    {"category": "jeans", "material": "cotton", "condition": "second-hand", "confidence": 0.91,
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

| Category | kg | | Category | kg |
|---|---|---|---|---|
| t-shirt | 5 | | sweater | 12 |
| shirt | 6 | | hoodie | 11 |
| jeans | 10 | | jacket | 15 |
| trousers | 9 | | shoes | 8 |
| shorts | 4 | | socks | 1 |
| skirt | 6 | | hat | 2 |
| dress | 9 | | *anything else* | **7** (default) |

Common synonyms are mapped to these categories, e.g. tee → t-shirt, denim → jeans,
sneakers / boots → shoes, coat / blazer → jacket, jumper / cardigan → sweater.

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
│   │   └── vision/              VisionProvider interface, mock and OpenAI providers
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
- **Model output is never trusted blindly.** The OpenAI reply must be JSON and is
  checked with Pydantic. Invalid items are skipped, and a broken reply becomes a clean `502`.
- **Easy to test.** Services get their dependencies through `__init__`, so tests
  pass in fakes. API tests swap dependencies with `dependency_overrides`.
- **No database**, as the brief requires: all data lives in memory.

## 🖥️ Frontend
_To be added._

## ☁️ Deployment
_To be added._

## 💡 Enhancements
_To be added: Product Improvements and Technical Scaling._
