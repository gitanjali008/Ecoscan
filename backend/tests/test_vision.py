import pytest

from app.schemas import DetectedItem
from app.services.vision import MockVisionProvider, VisionProvider
from app.services.vision.mock import DEFAULT_SCENARIOS

vision = MockVisionProvider()


def test_returns_detected_items():
    items = vision.detect_items(b"fake image bytes", "image/jpeg")

    assert len(items) > 0
    assert all(isinstance(item, DetectedItem) for item in items)


def test_same_image_gives_same_items():
    first = vision.detect_items(b"same photo", "image/png")
    second = vision.detect_items(b"same photo", "image/png")

    assert first == second


def test_different_images_cover_every_scenario():
    results = [vision.detect_items(f"photo {i}".encode(), "image/jpeg") for i in range(50)]

    for scenario in DEFAULT_SCENARIOS:
        assert scenario in results


def test_custom_scenario_is_used():
    only = [DetectedItem(category="hat", material="wool")]

    items = MockVisionProvider(scenarios=[only]).detect_items(b"anything", "image/webp")

    assert items == only


def test_changing_returned_items_does_not_change_the_scenario():
    only = [DetectedItem(category="hat")]
    provider = MockVisionProvider(scenarios=[only])

    provider.detect_items(b"x", "image/jpeg")[0].category = "changed"

    assert provider.detect_items(b"x", "image/jpeg")[0].category == "hat"


def test_needs_at_least_one_scenario():
    with pytest.raises(ValueError):
        MockVisionProvider(scenarios=[])


def test_mock_matches_the_provider_interface():
    provider: VisionProvider = MockVisionProvider()

    assert callable(provider.detect_items)


def test_every_mock_scenario_starts_as_new():
    # Like the real providers: the user marks second-hand items, not the scan.
    assert {item.condition for scenario in DEFAULT_SCENARIOS for item in scenario} == {"new"}
