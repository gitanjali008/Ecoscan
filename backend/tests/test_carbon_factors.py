import pytest

from app.data.carbon_factors import BASE_CARBON_KG, CATEGORY_ALIASES, DEFAULT_CARBON_KG, InMemoryCarbonFactors

repo = InMemoryCarbonFactors()


def test_brief_examples_are_in_the_table():
    assert repo.base_kg("t-shirt") == 5
    assert repo.base_kg("jeans") == 10


@pytest.mark.parametrize(
    "text, expected",
    [
        ("tee", "t-shirt"),
        ("Blue denim", "jeans"),
        ("running sneakers", "sneakers"),
        ("grey sweatshirt", "hoodie"),  # alias beats the shorter "shirt"
        ("striped t-shirt", "t-shirt"),  # "t-shirt" beats the shorter "shirt"
    ],
)
def test_category_wording_is_mapped(text, expected):
    assert repo.canonical_category(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("silk saree", "saree"),
        ("Sari", "saree"),
        ("cotton kurta", "kurta"),
        ("printed kurti", "kurti"),  # not confused with "kurta"
        ("bridal lehenga", "lehenga"),
        ("salwar kameez", "salwar"),
        ("chiffon dupatta", "dupatta"),
        ("wedding sherwani", "sherwani"),
        ("wool coat", "coat"),  # coat is no longer a jacket
        ("navy blazer", "blazer"),
        ("black leggings", "leggings"),
        ("tracksuit", "tracksuit"),
        ("one-piece swimsuit", "swimwear"),
        ("cotton boxers", "underwear"),
        ("silk scarf", "scarf"),
        ("leather gloves", "gloves"),
        ("bow tie", "tie"),
        ("leather belt", "belt"),
        ("tote bag", "bag"),
        ("baseball cap", "cap"),
        ("flip flops", "sandals"),
        ("ankle boots", "boots"),
        ("trainers", "sneakers"),
        ("high heels", "shoes"),
    ],
)
def test_new_categories_are_mapped(text, expected):
    assert repo.canonical_category(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("white crop top", "crop top"),  # beats the shorter "top"
        ("cropped top", "crop top"),
        ("black tank top", "tank top"),
        ("floral top", "top"),
        ("raincoat", "coat"),
        ("yoga pants", "leggings"),  # beats the shorter alias "pants"
        ("swim shorts", "swimwear"),  # beats the shorter "shorts"
        ("tie-dye hoodie", "hoodie"),  # beats the shorter "tie"
        ("baggy jeans", "jeans"),  # beats the shorter "bag"
        ("belted dress", "dress"),  # beats the shorter "belt"
        ("suit jacket", "blazer"),  # beats the shorter "jacket"
    ],
)
def test_longest_match_wins_for_new_categories(text, expected):
    assert repo.canonical_category(text) == expected


def test_every_alias_points_to_a_category():
    assert set(CATEGORY_ALIASES.values()) <= set(BASE_CARBON_KG)
    assert not set(CATEGORY_ALIASES) & set(BASE_CARBON_KG)


@pytest.mark.parametrize("category", list(BASE_CARBON_KG))
def test_every_category_maps_to_itself(category):
    assert repo.canonical_category(category) == category


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