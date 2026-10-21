"""Eco-reward points: CO2 saved -> points.

Kept separate from carbon scoring so the reward rule (bonuses, tiers, streaks)
can change without touching how carbon is calculated.
"""

import math


class RewardsService:
    def __init__(self, points_per_kg: float = 10) -> None:
        if points_per_kg <= 0:
            raise ValueError("points_per_kg must be positive")
        self._points_per_kg = points_per_kg

    def points_for(self, saved_kg: float) -> int:
        """Points for one item. Rounds half up, so 1.25 kg x 10 = 13 points."""
        if saved_kg <= 0:
            return 0
        return math.floor(saved_kg * self._points_per_kg + 0.5)