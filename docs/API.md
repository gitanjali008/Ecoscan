# EcoScan API

All endpoints are under `/api`. Local base URL: `http://localhost:8000/api`.
Interactive docs (Swagger) are at `http://localhost:8000/docs`.

Response shapes come from `backend/app/schemas.py`. The examples below were
produced by the running app with the `mock` vision provider.

| Method | Path | What |
|---|---|---|
| `GET` | [`/api/health`](#get-apihealth) | Check that the API is running |
| `POST` | [`/api/analyze`](#post-apianalyze) | Scan a photo |
| `POST` | [`/api/score`](#post-apiscore) | Score a list of items again, without a photo |
| `GET` | [`/api/offers`](#get-apioffers) | Offers for a points balance |
| `GET` | [`/api/carbon-factors`](#get-apicarbon-factors) | The carbon assumptions |

---

## `GET /api/health`

```bash
curl http://localhost:8000/api/health
```

```json
{"status": "ok"}
```

---

## `POST /api/analyze`

Upload a photo. Returns the items found, each item's carbon, points and tip, the
totals, the offers for those points, and which vision provider read the photo.

**Request:** `multipart/form-data` with one field, `file`: a JPEG, PNG or WebP
image, at most `MAX_IMAGE_MB` (default 10 MB).

```bash
curl -X POST http://localhost:8000/api/analyze -F "file=@photo.jpg;type=image/jpeg"
```

**Response `200`** (`AnalysisResponse`). Every scanned item starts as `"new"`,
so nothing is saved yet. `label` is `null` from the mock provider; Gemini and
OpenAI fill it in, e.g. `"faded blue straight-leg jeans"`.

```json
{
  "items": [
    {
      "category": "t-shirt",
      "material": "cotton",
      "condition": "new",
      "confidence": 0.94,
      "label": null,
      "baseline_kg": 5.0,
      "actual_kg": 5.0,
      "saved_kg": 0.0,
      "points": 0,
      "tip": "Bought second-hand, this would save 4 kg CO2 (+40 pts). Organic cotton would save about 1.5 kg."
    },
    {
      "category": "jeans",
      "material": "cotton",
      "condition": "new",
      "confidence": 0.91,
      "label": null,
      "baseline_kg": 10.0,
      "actual_kg": 10.0,
      "saved_kg": 0.0,
      "points": 0,
      "tip": "Bought second-hand, this would save 8 kg CO2 (+80 pts). Organic cotton would save about 3 kg."
    }
  ],
  "total_carbon_kg": 15.0,
  "total_saved_kg": 0.0,
  "total_points": 0,
  "offers": {
    "points": 0,
    "eligible": [],
    "locked": [
      {
        "id": "swap-pass",
        "title": "Free clothing swap entry",
        "partner": "Swap Circle",
        "description": "One free ticket to a local clothing swap event.",
        "points_required": 30,
        "points_needed": 30
      },
      {
        "id": "thrift-10",
        "title": "10% off second-hand fashion",
        "partner": "ReLoop Thrift",
        "description": "10% off your next purchase at a partner thrift store.",
        "points_required": 50,
        "points_needed": 50
      }
    ]
  },
  "provider": "mock"
}
```

_`locked` shortened: the full list has six offers, up to 400 points._

**Errors:** `400 empty_image`, `413 image_too_large`, `415 invalid_image`,
`422 no_clothing_detected`, `422 validation_error` (no `file` field),
`502 vision_service_error`.

---

## `POST /api/score`

Recalculate carbon and points for items the user has corrected (e.g. marked
second-hand, or changed the material). No photo, no vision call.

**Request:** JSON (`ScoreRequest`). At least one item. Only `category` is
required: `material` defaults to `"unknown"`, `condition` to `"new"`,
`confidence` to `1.0`, `label` to `null`. `condition` also accepts `"used"`,
`"thrifted"`, `"vintage"`, `"pre-owned"` and similar, read as `"second-hand"`.

```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"category": "jeans", "material": "cotton", "condition": "second-hand",
       "confidence": 0.91, "label": "faded blue straight-leg jeans"},
      {"category": "t-shirt", "material": "organic cotton"}
    ]
  }'
```

**Response `200`** (`ScoreResponse`):

```json
{
  "items": [
    {
      "category": "jeans",
      "material": "cotton",
      "condition": "second-hand",
      "confidence": 0.91,
      "label": "faded blue straight-leg jeans",
      "baseline_kg": 10.0,
      "actual_kg": 2.0,
      "saved_kg": 8.0,
      "points": 80,
      "tip": "Great choice! Buying it second-hand saved about 8 kg of CO2."
    },
    {
      "category": "t-shirt",
      "material": "organic cotton",
      "condition": "new",
      "confidence": 1.0,
      "label": null,
      "baseline_kg": 5.0,
      "actual_kg": 3.5,
      "saved_kg": 1.5,
      "points": 15,
      "tip": "Nice pick! Organic cotton saved about 1.5 kg of CO2 compared with a conventional material."
    }
  ],
  "total_carbon_kg": 5.5,
  "total_saved_kg": 9.5,
  "total_points": 95
}
```

**Errors:** `422 validation_error` (empty `items`, blank `category`,
`confidence` outside 0–1, unknown `condition`).

---

## `GET /api/offers`

Offers the user can redeem now (`eligible`) and the rest (`locked`), cheapest
first. Each locked offer says how many more points it needs.

**Request:** query parameter `points`, an integer ≥ 0.

```bash
curl "http://localhost:8000/api/offers?points=80"
```

**Response `200`** (`OffersResponse`):

```json
{
  "points": 80,
  "eligible": [
    {
      "id": "swap-pass",
      "title": "Free clothing swap entry",
      "partner": "Swap Circle",
      "description": "One free ticket to a local clothing swap event.",
      "points_required": 30
    },
    {
      "id": "thrift-10",
      "title": "10% off second-hand fashion",
      "partner": "ReLoop Thrift",
      "description": "10% off your next purchase at a partner thrift store.",
      "points_required": 50
    }
  ],
  "locked": [
    {
      "id": "repair-free",
      "title": "Free clothing repair",
      "partner": "StitchBack Repairs",
      "description": "One free basic repair: a zip, a hem or a seam.",
      "points_required": 100,
      "points_needed": 20
    },
    {
      "id": "plant-tree",
      "title": "Plant a tree",
      "partner": "Green Roots",
      "description": "We plant a tree in your name.",
      "points_required": 150,
      "points_needed": 70
    }
  ]
}
```

_`locked` shortened: `rental-20` (250) and `organic-15` (400) follow._

**Errors:** `422 validation_error` (missing, negative or non-integer `points`).

---

## `GET /api/carbon-factors`

The numbers every score is based on:
`actual_kg = base_kg × material_factor × condition_factor`.

```bash
curl http://localhost:8000/api/carbon-factors
```

**Response `200`** (`CarbonFactorsResponse`, maps shortened):

```json
{
  "base_kg": {"t-shirt": 5.0, "shirt": 6.0, "jeans": 10.0, "dress": 9.0, "coat": 20.0, "sneakers": 14.0},
  "default_kg": 7.0,
  "material_factor": {"recycled cotton": 0.5, "organic cotton": 0.7, "cotton": 1.0, "wool": 1.3, "leather": 1.5},
  "condition_factor": {"new": 1.0, "second-hand": 0.2}
}
```

---

## Errors

Every error the API reports on purpose has the same shape:

```json
{
  "error": {
    "code": "invalid_image",
    "message": "The file is not a valid JPEG, PNG or WebP image."
  }
}
```

Validation errors (`422 validation_error`) add a `details` list from Pydantic
saying which field is wrong:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request data is invalid.",
    "details": [
      {
        "type": "greater_than_equal",
        "loc": ["query", "points"],
        "msg": "Input should be greater than or equal to 0",
        "input": "-1",
        "ctx": {"ge": 0}
      }
    ]
  }
}
```

| Status | Code | Message (default) |
|---|---|---|
| 400 | `empty_image` | The uploaded image is empty. |
| 413 | `image_too_large` | The image is too large. The limit is 10 MB. |
| 415 | `invalid_image` | Unsupported file type '…'. Upload a JPEG, PNG or WebP image. / The file is not a valid JPEG, PNG or WebP image. |
| 422 | `no_clothing_detected` | No clothing items were found in the image. |
| 422 | `validation_error` | The request data is invalid. |
| 502 | `vision_service_error` | The image recognition service failed. Please try again. |
