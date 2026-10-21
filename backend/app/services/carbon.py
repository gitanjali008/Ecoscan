"""Carbon scoring: how much CO2 an item cost, and how much the user saved.

    baseline_kg = footprint of the same item bought new, in a conventional material
    actual_kg   = baseline_kg x material_factor x condition_factor
    saved_kg    = baseline_kg - actual_kg   (never below 0)

The service only talks to a CarbonFactorRepository, so the numbers can come
from memory today and from a database or external API later.
"""

from dataclasses import dataclass

from app.data.carbon_factors import CarbonFactorRepository
from app.schemas import DetectedItem


@dataclass(frozen=True)
class CarbonBreakdown:
    """Carbon numbers for one item. Points are added later by the rewards service."""

    item: DetectedItem
    baseline_kg: float
    actual_kg: float
    saved_kg: float


class CarbonService:
    def __init__(self, factors: CarbonFactorRepository) -> None:
        self._factors = factors

    def score_item(self, item: DetectedItem) -> CarbonBreakdown:
        baseline = self._factors.base_kg(item.category)
        multiplier = self._factors.material_factor(item.material) * self._factors.condition_factor(item.condition)
        actual = baseline * multiplier
        # A higher-impact material (e.g. wool) raises actual_kg but is not a negative saving.
        saved = max(baseline - actual, 0.0)

        # Report a consistent name ("blue denim" -> "jeans") when we recognise the item.
        category = self._factors.canonical_category(item.category) or item.category

        return CarbonBreakdown(
            item=item.model_copy(update={"category": category}),
            baseline_kg=round(baseline, 2),
            actual_kg=round(actual, 2),
            saved_kg=round(saved, 2),
        )

    def score_items(self, items: list[DetectedItem]) -> list[CarbonBreakdown]:
        return [self.score_item(item) for item in items]