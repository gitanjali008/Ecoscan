import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.data.carbon_factors import InMemoryCarbonFactors
from app.data.offers import InMemoryOffers
from app.dependencies import get_vision_provider
from app.errors import ImageTooLargeError, InvalidImageError, NoClothingDetectedError
from app.main import create_app
from app.schemas import DetectedItem
from app.services.analysis import AnalysisService
from app.services.carbon import CarbonService
from app.services.offers import OffersService
from app.services.rewards import RewardsService
from app.services.scoring import ScoringService
from app.services.tips import EcoTipService
from app.services.vision import MockVisionProvider

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 20
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20


class FakeVision:
    """Returns fixed items and records what it was given."""

    name = "fake"

    def __init__(self, items: list[DetectedItem]) -> None:
        self.items = items
        self.calls: list[tuple[bytes, str]] = []

    def detect_items(self, image: bytes, content_type: str) -> list[DetectedItem]:
        self.calls.append((image, content_type))
        return self.items


def make_service(vision, max_bytes: int = 1024) -> AnalysisService:
    factors = InMemoryCarbonFactors()
    carbon = CarbonService(factors)
    rewards = RewardsService(points_per_kg=10)
    scoring = ScoringService(carbon, rewards, EcoTipService(carbon, factors, rewards))
    return AnalysisService(vision, scoring, OffersService(InMemoryOffers()), max_bytes)


def test_analyze_scores_items_and_finds_offers():
    vision = FakeVision([
        DetectedItem(category="jeans", condition="second-hand"),       # saved 8 kg -> 80 points
        DetectedItem(category="t-shirt", material="organic cotton"),   # saved 1.5 kg -> 15 points
    ])

    result = make_service(vision).analyze(JPEG, "image/jpeg")

    assert [i.category for i in result.items] == ["jeans", "t-shirt"]
    assert result.total_carbon_kg == 5.5
    assert result.total_points == 95
    assert result.offers.points == 95
    assert all(o.points_required <= 95 for o in result.offers.eligible)
    assert all(o.points_required > 95 for o in result.offers.locked)
    assert result.provider == "fake"


def test_no_items_raises_no_clothing_detected():
    with pytest.raises(NoClothingDetectedError):
        make_service(FakeVision([])).analyze(JPEG, "image/jpeg")


def test_invalid_image_never_reaches_vision():
    vision = FakeVision([DetectedItem(category="hat")])

    with pytest.raises(InvalidImageError):
        make_service(vision).analyze(b"plain text", "image/jpeg")

    assert vision.calls == []


def test_size_limit_comes_from_the_service():
    with pytest.raises(ImageTooLargeError):
        make_service(FakeVision([]), max_bytes=10).analyze(JPEG, "image/jpeg")


def test_vision_gets_the_real_image_type():
    vision = FakeVision([DetectedItem(category="hat")])

    make_service(vision).analyze(PNG, "image/jpeg")

    assert vision.calls == [(PNG, "image/png")]


# Route smoke tests. The full API test suite comes in a later step.

@pytest.fixture
def client():
    app = create_app()
    # Fixed settings and the mock provider, whatever the developer's .env says.
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    app.dependency_overrides[get_vision_provider] = MockVisionProvider
    return TestClient(app)


def test_analyze_route_returns_a_full_analysis(client):
    response = client.post("/api/analyze", files={"file": ("photo.jpg", JPEG, "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) > 0
    assert body["total_points"] == body["offers"]["points"]


def test_analyze_route_rejects_a_renamed_text_file(client):
    response = client.post("/api/analyze", files={"file": ("photo.jpg", b"hello", "image/jpeg")})

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "invalid_image"


def test_analyze_route_rejects_an_empty_file(client):
    response = client.post("/api/analyze", files={"file": ("photo.jpg", b"", "image/jpeg")})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "empty_image"


def test_analyze_route_rejects_a_file_over_the_limit(client):
    client.app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, max_image_mb=0.00001)  # ~10 bytes

    response = client.post("/api/analyze", files={"file": ("photo.jpg", JPEG, "image/jpeg")})

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "image_too_large"


def test_analyze_route_without_a_file_is_a_validation_error(client):
    response = client.post("/api/analyze")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
