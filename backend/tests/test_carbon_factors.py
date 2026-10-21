import pytest

from app.data.carbon_factors import DEFAULT_CARBON_KG, InMemoryCarbonFactors

repo = InMemoryCarbonFactors()


def test_brief_examples_are_in_the_table():
    assert repo.base_kg("t-shirt") == 5
    assert repo.base_kg("jeans") == 10


@pytest.mark.parametrize(
    "text, expected",
    [
        ("tee", "t-shirt"),
        ("Blue denim", "jeans"),
        ("running sneakers", "shoes"),
        ("grey sweatshirt", "hoodie"),  # alias beats the shorter "shirt"
        ("striped t-shirt", "t-shirt"),  # "t-shirt" beats the shorter "shirt"
    ],
)
def test_category_wording_is_mapped(text, expected):
    assert repo.canonical_category(text) == expected


def test_unknown_category_uses_default():
    assert repo.canonical_category("kimono") is None
    assert repo.base_kg("kimono") == DEFAULT_CARBON_KG


def test_material_longest_match_wins():
    assert repo.material_factor("100% Organic Cotton") == 0.7
    assert repo.material_factor("cotton") == 1.0


def test_unknown_material_is_neutral():
    assert repo.material_factor("unknown") == 1.0


def test_condition_factors():
    assert repo.condition_factor("new") == 1.0
    assert repo.condition_factor("second-hand") == 0.2
    assert repo.condition_factor("something else") == 1.0


def test_repository_accepts_custom_data():
    custom = InMemoryCarbonFactors(base={"saree": 12.0}, aliases={})

    assert custom.base_kg("silk saree") == 12.0


def test_all_factors_exposes_the_tables():
    factors = repo.all_factors()

    assert factors["base_kg"]["jacket"] == 15
    assert "organic cotton" in factors["material_factor"]