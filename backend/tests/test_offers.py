from app.data.offers import InMemoryOffers
from app.schemas import Offer
from app.services.offers import OffersService

offers = [
    Offer(id="cheap", title="Cheap", partner="P", description="d", points_required=50),
    Offer(id="mid", title="Mid", partner="P", description="d", points_required=100),
    Offer(id="top", title="Top", partner="P", description="d", points_required=300),
]
service = OffersService(InMemoryOffers(offers))


def ids(items):
    return [o.id for o in items]


def test_zero_points_unlocks_nothing():
    result = service.offers_for(0)
    assert result.eligible == []
    assert ids(result.locked) == ["cheap", "mid", "top"]


def test_exactly_enough_points_unlocks_the_offer():
    result = service.offers_for(100)
    assert ids(result.eligible) == ["cheap", "mid"]
    assert ids(result.locked) == ["top"]


def test_one_point_short_stays_locked_with_points_needed():
    result = service.offers_for(99)
    assert ids(result.eligible) == ["cheap"]
    assert result.locked[0].id == "mid"
    assert result.locked[0].points_needed == 1


def test_lots_of_points_unlocks_everything():
    result = service.offers_for(10_000)
    assert ids(result.eligible) == ["cheap", "mid", "top"]
    assert result.locked == []


def test_negative_points_are_treated_as_zero():
    result = service.offers_for(-5)
    assert result.points == 0
    assert result.eligible == []


def test_default_catalogue_is_sorted_by_cost():
    result = OffersService(InMemoryOffers()).offers_for(0)
    costs = [o.points_required for o in result.locked]
    assert costs == sorted(costs)
    assert len(costs) > 0