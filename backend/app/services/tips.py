"""Eco tips: one short, friendly tip per scored item.

Rule-based on purpose: free, instant and easy to test. All rules live in
TIP_RULES, checked in order; the first one that applies writes the tip.
To add a tip, add a TipRule in the right place in the list.
"""

from collections.abc import Callable
from dataclasses import dataclass

from app.data.carbon_factors import CarbonFactorRepository
from app.schemas import DetectedItem
from app.services.carbon import CarbonBreakdown, CarbonService
from app.services.rewards import RewardsService

# A lower-impact choice of the same kind of material. Checked in order, so a
# "cotton/polyester blend" gets the polyester tip.
MATERIAL_ALTERNATIVES: list[tuple[str, str]] = [
    ("polyester", "recycled polyester"),
    ("cotton", "organic cotton"),
]

# How to make a high-impact item last longer.
CARE_TIPS: dict[str, str] = {
    "wool": "air it between wears and wash it cool by hand",
    "leather": "clean and condition it, and repair it instead of replacing it",
}
DEFAULT_CARE_TIP = "wash it cool and fix small damage early"


@dataclass(frozen=True)
class TipContext:
    """What a rule can look at for one item."""

    item: DetectedItem
    saved_kg: float
    material_factor: float
    carbon: CarbonService
    rewards: RewardsService

    def saved_if(self, **changes: str) -> float:
        """kg saved if the same item had, e.g., condition="second-hand"."""
        return self.carbon.score_item(self.item.model_copy(update=changes)).saved_kg


@dataclass(frozen=True)
class TipRule:
    name: str
    applies: Callable[[TipContext], bool]
    tip: Callable[[TipContext], str]


def _kg(value: float) -> str:
    """3.5 -> "3.5 kg", 8.0 -> "8 kg", 0.04 -> "under 0.1 kg"."""
    if value < 0.05:
        return "under 0.1 kg"
    return f"{round(value, 1):g} kg"


def _care_tip(material: str) -> str:
    return next((tip for word, tip in CARE_TIPS.items() if word in material), DEFAULT_CARE_TIP)


def _would_save_second_hand_tip(ctx: TipContext) -> str:
    # A photo can't show that an item was second-hand, so lead with what marking it would save.
    saved = ctx.saved_if(condition="second-hand")
    tip = f"Bought second-hand, this would save {_kg(saved)} CO2 (+{ctx.rewards.points_for(saved)} pts)."
    if ctx.material_factor > 1:
        return tip + (
            f" {ctx.item.material.capitalize()} has a higher footprint, so make it last: "
            f"{_care_tip(ctx.item.material)}."
        )
    alternative = next((alt for word, alt in MATERIAL_ALTERNATIVES if word in ctx.item.material), None)
    if alternative:
        tip += f" {alternative.capitalize()} would save about {_kg(ctx.saved_if(material=alternative))}."
    return tip


TIP_RULES: list[TipRule] = [
    TipRule(
        name="second-hand",
        applies=lambda ctx: ctx.item.condition == "second-hand",
        tip=lambda ctx: f"Great choice! Buying it second-hand saved about {_kg(ctx.saved_kg)} of CO2.",
    ),
    TipRule(
        name="low-impact material",
        applies=lambda ctx: ctx.material_factor < 1,
        tip=lambda ctx: (
            f"Nice pick! {ctx.item.material.capitalize()} saved about {_kg(ctx.saved_kg)} of CO2 "
            "compared with a conventional material."
        ),
    ),
    # Last, and always applies: new, with nothing saved. Adds care advice for a
    # high-impact material, or a lower-impact alternative for a conventional one.
    TipRule(name="would save second-hand", applies=lambda ctx: True, tip=_would_save_second_hand_tip),
]


class EcoTipService:
    def __init__(
        self,
        carbon: CarbonService,
        factors: CarbonFactorRepository,
        rewards: RewardsService,
        rules: list[TipRule] = TIP_RULES,
    ) -> None:
        self._carbon = carbon
        self._factors = factors
        self._rewards = rewards
        self._rules = rules

    def tip_for(self, result: CarbonBreakdown) -> str:
        ctx = TipContext(
            item=result.item,
            saved_kg=result.saved_kg,
            material_factor=self._factors.material_factor(result.item.material),
            carbon=self._carbon,
            rewards=self._rewards,
        )
        rule = next(rule for rule in self._rules if rule.applies(ctx))
        return rule.tip(ctx)
