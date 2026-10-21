"""Smoke tests for /score, /offers and /carbon-factors. The full API suite comes later."""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    # Fixed settings (e.g. points_per_kg=10), whatever the developer's .env says.
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    return TestClient(app)


def test_score_recalculates_edited_items(client):
    response = client.post("/api/score", json={"items": [
        {"category": "jeans", "condition": "second-hand"},
        {"category": "t-shirt", "material": "organic cotton"},
    ]})

    assert response.status_code == 200
    body = response.json()
    assert [i["points"] for i in body["items"]] == [80, 15]
    assert body["total_carbon_kg"] == 5.5
    assert body["total_points"] == 95


@pytest.mark.parametrize(
    "payload",
    [
        {"items": []},                                          # at least one item
        {"items": [{"category": "jeans", "condition": "old"}]},  # unknown condition
        {},                                                     # no items key
    ],
)
def test_score_rejects_bad_input(client, payload):
    response = client.post("/api/score", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_offers_splits_eligible_and_locked(client):
    response = client.get("/api/offers", params={"points": 95})

    assert response.status_code == 200
    body = response.json()
    assert body["points"] == 95
    assert all(o["points_required"] <= 95 for o in body["eligible"])
    assert all(o["points_needed"] == o["points_required"] - 95 for o in body["locked"])


@pytest.mark.parametrize("query", ["?points=-1", "?points=abc", ""])
def test_offers_needs_a_non_negative_whole_number(client, query):
    response = client.get(f"/api/offers{query}")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_carbon_factors_shows_the_assumptions(client):
    response = client.get("/api/carbon-factors")

    assert response.status_code == 200
    body = response.json()
    assert body["base_kg"]["t-shirt"] == 5.0
    assert body["base_kg"]["jeans"] == 10.0
    assert body["condition_factor"] == {"new": 1.0, "second-hand": 0.2}
    assert set(body) == {"base_kg", "default_kg", "material_factor", "condition_factor"}


def test_every_route_has_a_description_in_the_docs(client):
    paths = client.get("/openapi.json").json()["paths"]

    for path in ["/api/health", "/api/analyze", "/api/score", "/api/offers", "/api/carbon-factors"]:
        [operation] = paths[path].values()
        assert operation.get("description"), path
