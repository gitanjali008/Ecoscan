import pytest

from app.data.carbon_factors import DEFAULT_CARBON_KG, InMemoryCarbonFactors
from app.schemas import DetectedItem
from app.services.carbon import CarbonService

service = CarbonService(InMemoryCarbonFactors())


@pytest.mark.parametrize(
    "category, material, condition, baseline, actual, saved",
    [
        ("t-shirt", "cotton", "new", 5.0, 5.0, 0.0),                      # nothing saved
        ("jeans", "unknown", "second-hand", 10.0, 2.0, 8.0),              # reuse
        ("t-shirt", "organic cotton", "new", 5.0, 3.5, 1.5),              # better material
        ("jacket", "recycled polyester", "second-hand", 15.0, 1.8, 13.2),  # both combine
    ],
)
def test_score_item(category, material, condition, baseline, actual, saved):
    item = DetectedItem(category=category, material=material, condition=condition)

    result = service.score_item(item)

    assert result.baseline_kg == baseline
    assert result.actual_kg == actual
    assert result.saved_kg == saved


def test_higher_impact_material_never_gives_negative_savings():
    result = service.score_item(DetectedItem(category="sweater", material="wool"))

    assert result.actual_kg > result.baseline_kg
    assert result.saved_kg == 0


def test_category_is_reported_with_its_canonical_name():
    result = service.score_item(DetectedItem(category="Blue denim"))

    assert result.item.category == "jeans"


def test_unknown_category_keeps_its_name_and_uses_default():
    result = service.score_item(DetectedItem(category="kimono"))

    assert result.item.category == "kimono"
    assert result.baseline_kg == DEFAULT_CARBON_KG


def test_score_items_keeps_order():
    items = [DetectedItem(category="jeans"), DetectedItem(category="t-shirt")]

    results = service.score_items(items)

    assert [r.item.category for r in results] == ["jeans", "t-shirt"]


def test_score_items_with_no_items():
    assert service.score_items([]) == []


class FakeFactors:
    """Any object with the repository methods works: proof the service is decoupled from storage."""

    def canonical_category(self, category):
        return category

    def base_kg(self, category):
        return 100.0

    def material_factor(self, material):
        return 0.5

    def condition_factor(self, condition):
        return 0.5

    def all_factors(self):
        return {}


def test_service_works_with_any_repository():
    result = CarbonService(FakeFactors()).score_item(DetectedItem(category="anything"))

    assert result.actual_kg == 25.0
    assert result.saved_kg == 75.0