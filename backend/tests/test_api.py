"""API tests over HTTP, with dependencies overridden.

Settings and the vision provider are always replaced, so these tests never call
the real OpenAI API and do not depend on the developer's .env.
"""

import struct
import zlib

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.dependencies import get_vision_provider
from app.errors import VisionServiceError
from app.main import create_app
from app.schemas import DetectedItem
from app.services.vision import MockVisionProvider


def tiny_png() -> bytes:
    """A real 1x1 white PNG: signature, IHDR, IDAT and IEND chunks with CRCs."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)  # 1x1, 8-bit RGB
    pixels = zlib.compress(b"\x00\xff\xff\xff")           # filter byte + one white pixel
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


PNG = tiny_png()


class EmptyVision:
    def detect_items(self, image, content_type):
        return []


class FailingVision:
    def detect_items(self, image, content_type):
        raise VisionServiceError()


@pytest.fixture
def make_client():
    def _make(vision=None, **settings) -> TestClient:
        app = create_app()
        app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, **settings)
        app.dependency_overrides[get_vision_provider] = lambda: vision or MockVisionProvider()
        return TestClient(app)

    return _make


@pytest.fixture
def client(make_client):
    return make_client()


def upload(client: TestClient, data: bytes, content_type: str = "image/png", name: str = "photo.png"):
    return client.post("/api/analyze", files={"file": (name, data, content_type)})


def assert_error(response, status: int, code: str) -> None:
    """Every error has the same shape: {"error": {"code": ..., "message": ...}}."""
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"error"}
    error = body["error"]
    assert error["code"] == code
    assert isinstance(error["message"], str) and error["message"]
    # Only validation errors add details.
    assert set(error) <= {"code", "message", "details"}


# /analyze

def test_analyze_happy_path(client):
    response = upload(client, PNG)

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) > 0
    for item in body["items"]:
        assert {"category", "baseline_kg", "actual_kg", "saved_kg", "points"} <= set(item)
    assert body["total_carbon_kg"] == pytest.approx(sum(i["actual_kg"] for i in body["items"]))
    assert body["total_points"] == sum(i["points"] for i in body["items"])
    assert body["offers"]["points"] == body["total_points"]
    assert body["provider"] == "mock"
    assert {"eligible", "locked"} <= set(body["offers"])


def test_analyze_rejects_a_pdf(client):
    assert_error(upload(client, b"%PDF-1.7 ...", "application/pdf", "doc.pdf"), 415, "invalid_image")


def test_analyze_rejects_a_text_file_renamed_to_png(client):
    assert_error(upload(client, b"just text", "image/png", "notes.png"), 415, "invalid_image")


def test_analyze_rejects_an_empty_file(client):
    assert_error(upload(client, b""), 400, "empty_image")


def test_analyze_rejects_a_file_over_the_limit(make_client):
    client = make_client(max_image_mb=0.00001)  # about 10 bytes, smaller than the PNG

    assert_error(upload(client, PNG), 413, "image_too_large")


def test_analyze_with_no_clothing_found(make_client):
    assert_error(upload(make_client(vision=EmptyVision()), PNG), 422, "no_clothing_detected")


def test_analyze_when_the_vision_service_fails(make_client):
    assert_error(upload(make_client(vision=FailingVision()), PNG), 502, "vision_service_error")


def test_analyze_without_a_file(client):
    assert_error(client.post("/api/analyze"), 422, "validation_error")


class LabelledVision:
    name = "gemini"

    def detect_items(self, image, content_type):
        return [DetectedItem(category="kurti", material="cotton", label="yellow block-print kurti")]


def test_analyze_returns_the_item_label(make_client):
    response = upload(make_client(vision=LabelledVision()), PNG)

    assert response.status_code == 200
    [item] = response.json()["items"]
    assert (item["category"], item["label"]) == ("kurti", "yellow block-print kurti")


def test_analyze_says_which_provider_read_the_photo(make_client):
    assert upload(make_client(), PNG).json()["provider"] == "mock"
    assert upload(make_client(vision=LabelledVision()), PNG).json()["provider"] == "gemini"


# /score

def test_score_valid_items(client):
    response = client.post("/api/score", json={"items": [
        {"category": "jeans", "condition": "second-hand"},           # saved 8 kg -> 80 points
        {"category": "t-shirt", "material": "organic cotton"},       # saved 1.5 kg -> 15 points
    ]})

    assert response.status_code == 200
    body = response.json()
    assert [i["points"] for i in body["items"]] == [80, 15]
    assert body["total_saved_kg"] == 9.5
    assert body["total_points"] == 95


def test_score_with_no_items(client):
    assert_error(client.post("/api/score", json={"items": []}), 422, "validation_error")


def test_score_keeps_the_label_and_it_is_optional(client):
    items = [{"category": "saree", "label": "silk saree"}, {"category": "jeans"}]

    response = client.post("/api/score", json={"items": items})

    assert response.status_code == 200
    assert [i["label"] for i in response.json()["items"]] == ["silk saree", None]


# /offers

def test_offers_for_120_points(client):
    response = client.get("/api/offers", params={"points": 120})

    assert response.status_code == 200
    body = response.json()
    assert [o["id"] for o in body["eligible"]] == ["swap-pass", "thrift-10", "repair-free"]
    assert [o["id"] for o in body["locked"]] == ["plant-tree", "rental-20", "organic-15"]
    assert body["locked"][0]["points_needed"] == 30


def test_offers_with_negative_points(client):
    assert_error(client.get("/api/offers", params={"points": -1}), 422, "validation_error")


# /carbon-factors

def test_carbon_factors_show_the_brief_examples(client):
    response = client.get("/api/carbon-factors")

    assert response.status_code == 200
    assert response.json()["base_kg"]["t-shirt"] == 5
    assert response.json()["base_kg"]["jeans"] == 10
