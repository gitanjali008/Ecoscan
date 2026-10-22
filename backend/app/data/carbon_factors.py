"""Carbon footprint assumptions, stored in memory.

All numbers are rough, illustrative estimates for a demo, not audited
life-cycle data. They are kept in plain dicts so they are easy to review and
update, and are read only through CarbonFactorRepository.

Model:  actual_kg = base_kg[category] x material_factor x condition_factor
"""

from typing import Protocol

# kg CO2e to produce one NEW item in a conventional material.
BASE_CARBON_KG: dict[str, float] = {
    # Tops
    "t-shirt": 5.0,
    "shirt": 6.0,
    "top": 5.0,
    "crop top": 4.0,
    "tank top": 3.0,
    "sweater": 12.0,
    "hoodie": 11.0,
    # Bottoms
    "jeans": 10.0,
    "trousers": 9.0,
    "shorts": 4.0,
    "skirt": 6.0,
    "leggings": 4.0,
    # One-piece and sets
    "dress": 9.0,
    "tracksuit": 14.0,
    "swimwear": 3.0,
    "underwear": 1.5,
    # Outerwear
    "jacket": 15.0,
    "coat": 20.0,
    "blazer": 14.0,
    # Indian wear
    "saree": 14.0,
    "kurta": 7.0,
    "kurti": 6.0,
    "lehenga": 25.0,
    "salwar": 6.0,
    "dupatta": 4.0,
    "sherwani": 20.0,
    # Footwear
    "shoes": 8.0,
    "sneakers": 14.0,
    "boots": 16.0,
    "sandals": 5.0,
    # Accessories
    "socks": 1.0,
    "hat": 2.0,
    "cap": 1.5,
    "scarf": 3.0,
    "gloves": 2.0,
    "tie": 1.5,
    "belt": 3.0,
    "bag": 8.0,
}

# Used when the item type is not in the table, so a scan never fails on it.
DEFAULT_CARBON_KG = 7.0

# Other words for the same item, mapped to a key in BASE_CARBON_KG.
CATEGORY_ALIASES: dict[str, str] = {
    "tee": "t-shirt",
    "tshirt": "t-shirt",
    "t shirt": "t-shirt",
    "polo": "t-shirt",
    "blouse": "shirt",
    "crop-top": "crop top",
    "cropped top": "crop top",
    "tank-top": "tank top",
    "tanktop": "tank top",
    "camisole": "tank top",
    "singlet": "tank top",
    "jumper": "sweater",
    "pullover": "sweater",
    "cardigan": "sweater",
    "sweatshirt": "hoodie",
    "denim": "jeans",
    "pants": "trousers",
    "chinos": "trousers",
    "jeggings": "leggings",
    "tights": "leggings",
    "yoga pants": "leggings",
    "track suit": "tracksuit",
    "jogging suit": "tracksuit",
    "swimsuit": "swimwear",
    "bikini": "swimwear",
    "swim shorts": "swimwear",
    "swimming trunks": "swimwear",
    "boxers": "underwear",
    "briefs": "underwear",
    "lingerie": "underwear",
    "windbreaker": "jacket",
    "overcoat": "coat",
    "trench": "coat",
    "parka": "coat",
    "sport coat": "blazer",
    "suit jacket": "blazer",
    "sari": "saree",
    "kurta pajama": "kurta",
    "kameez": "kurta",
    "lehnga": "lehenga",
    "ghagra": "lehenga",
    "chaniya choli": "lehenga",
    "salwar kameez": "salwar",
    "salwar suit": "salwar",
    "churidar": "salwar",
    "chunni": "dupatta",
    "achkan": "sherwani",
    "trainers": "sneakers",
    "running shoes": "sneakers",
    "sports shoes": "sneakers",
    "flip flops": "sandals",
    "flip-flops": "sandals",
    "slippers": "sandals",
    "chappals": "sandals",
    "heels": "shoes",
    "loafers": "shoes",
    "beanie": "hat",
    "baseball cap": "cap",
    "muffler": "scarf",
    "shawl": "scarf",
    "stole": "scarf",
    "mittens": "gloves",
    "necktie": "tie",
    "bow tie": "tie",
    "handbag": "bag",
    "backpack": "bag",
    "purse": "bag",
    "tote": "bag",
}

# Multiplier vs a conventional material (1.0). Below 1 = lower impact.
MATERIAL_FACTOR: dict[str, float] = {
    "recycled cotton": 0.5,
    "recycled polyester": 0.6,
    "hemp": 0.6,
    "organic cotton": 0.7,
    "lyocell": 0.7,
    "tencel": 0.7,
    "linen": 0.8,
    "cotton": 1.0,
    "polyester": 1.0,
    "nylon": 1.1,
    "acrylic": 1.1,
    "wool": 1.3,
    "leather": 1.5,
}

DEFAULT_MATERIAL_FACTOR = 1.0

# Reusing an item avoids most of the impact of making a new one.
CONDITION_FACTOR: dict[str, float] = {
    "new": 1.0,
    "second-hand": 0.2,
}

DEFAULT_CONDITION_FACTOR = 1.0


def _best_match(text: str, keys: list[str]) -> str | None:
    """Exact key, else the longest key contained in the text.

    Longest first, so "organic cotton" beats "cotton" and "t-shirt" beats "shirt".
    """
    text = text.strip().lower()
    if text in keys:
        return text
    for key in sorted(keys, key=len, reverse=True):
        if key in text:
            return key
    return None


class CarbonFactorRepository(Protocol):
    """What the carbon service needs. Any data source can implement this."""

    def categories(self) -> list[str]: ...
    def canonical_category(self, category: str) -> str | None: ...
    def base_kg(self, category: str) -> float: ...
    def material_factor(self, material: str) -> float: ...
    def condition_factor(self, condition: str) -> float: ...
    def all_factors(self) -> dict: ...


class InMemoryCarbonFactors:
    """CarbonFactorRepository backed by the dicts in this module."""

    def __init__(
        self,
        base: dict[str, float] = BASE_CARBON_KG,
        aliases: dict[str, str] = CATEGORY_ALIASES,
        materials: dict[str, float] = MATERIAL_FACTOR,
        conditions: dict[str, float] = CONDITION_FACTOR,
    ) -> None:
        self._base = base
        self._aliases = aliases
        self._materials = materials
        self._conditions = conditions

    def categories(self) -> list[str]:
        """The known category names (not the aliases), e.g. for a vision prompt."""
        return list(self._base)

    def canonical_category(self, category: str) -> str | None:
        """Map any wording ("Blue denim", "tee") to a table key, or None if unknown."""
        match = _best_match(category, list(self._base) + list(self._aliases))
        if match is None:
            return None
        return self._aliases.get(match, match)

    def base_kg(self, category: str) -> float:
        key = self.canonical_category(category)
        return self._base[key] if key else DEFAULT_CARBON_KG

    def material_factor(self, material: str) -> float:
        key = _best_match(material, list(self._materials))
        return self._materials[key] if key else DEFAULT_MATERIAL_FACTOR

    def condition_factor(self, condition: str) -> float:
        return self._conditions.get(condition.strip().lower(), DEFAULT_CONDITION_FACTOR)

    def all_factors(self) -> dict:
        """Everything, for the /api/carbon-factors endpoint and the README."""
        return {
            "base_kg": dict(self._base),
            "default_kg": DEFAULT_CARBON_KG,
            "material_factor": dict(self._materials),
            "condition_factor": dict(self._conditions),
        }