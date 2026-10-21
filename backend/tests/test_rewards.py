import pytest

from app.data.carbon_factors import InMemoryCarbonFactors
from app.schemas import DetectedItem
from app.services.carbon import CarbonService
from app.services.rewards import RewardsService
from app.services.scoring import ScoringService

rewards = RewardsService(points_per_kg=10)


@pytest.mark.parametrize(
    "saved_kg, points",
    [
        (0, 0),
        (-3, 0),      # never negative
        (8, 80),
        (1.25, 13),   # rounds half up
        (0.04, 0),
    ],
)
def test_points_for(saved_kg, points):
    assert rewards.points_for(saved_kg) == points


def test_points_per_kg_is_configurable():
    assert RewardsService(points_per_kg=2).points_for(8) == 16


def test_points_per_kg_must_be_positive():
    with pytest.raises(ValueError):
        RewardsService(points_per_kg=0)


scoring = ScoringService(CarbonService(InMemoryCarbonFactors()), rewards)


def test_scoring_combines_carbon_and_points():
    response = scoring.score(
        [
            DetectedItem(category="jeans", condition="second-hand"),  # 10 -> 2, saved 8
            DetectedItem(category="t-shirt", material="organic cotton"),  # 5 -> 3.5, saved 1.5
        ]
    )

    assert [i.points for i in response.items] == [80, 15]
    assert response.total_carbon_kg == 5.5
    assert response.total_saved_kg == 9.5
    assert response.total_points == 95


def test_scoring_with_no_savings_gives_zero_points():
    response = scoring.score([DetectedItem(category="sweater", material="wool")])

    assert response.total_points == 0
    assert response.total_saved_kg == 0