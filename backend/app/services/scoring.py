"""Eco-score: combines carbon scoring and rewards into one response.

Routes call this instead of wiring carbon, rewards and tips themselves, so the
"items -> scores + points + tips" flow lives in exactly one place.
"""

from app.schemas import DetectedItem, ScoredItem, ScoreResponse
from app.services.carbon import CarbonService
from app.services.rewards import RewardsService
from app.services.tips import EcoTipService


class ScoringService:
    def __init__(self, carbon: CarbonService, rewards: RewardsService, tips: EcoTipService) -> None:
        self._carbon = carbon
        self._rewards = rewards
        self._tips = tips

    def score(self, items: list[DetectedItem]) -> ScoreResponse:
        scored = [
            ScoredItem(
                **result.item.model_dump(),
                baseline_kg=result.baseline_kg,
                actual_kg=result.actual_kg,
                saved_kg=result.saved_kg,
                points=self._rewards.points_for(result.saved_kg),
                tip=self._tips.tip_for(result),
            )
            for result in self._carbon.score_items(items)
        ]

        return ScoreResponse(
            items=scored,
            total_carbon_kg=round(sum(i.actual_kg for i in scored), 2),
            total_saved_kg=round(sum(i.saved_kg for i in scored), 2),
            # Sum of item points, so the total always matches what the UI lists.
            total_points=sum(i.points for i in scored),
        )