"""Offers: which ones the user can redeem now, and how close they are to the rest."""

from app.data.offers import OfferRepository
from app.schemas import LockedOffer, OffersResponse


class OffersService:
    def __init__(self, offers: OfferRepository) -> None:
        self._offers = offers

    def offers_for(self, points: int) -> OffersResponse:
        points = max(points, 0)
        by_cost = sorted(self._offers.list_all(), key=lambda o: o.points_required)

        eligible = [o for o in by_cost if o.points_required <= points]
        # Locked offers carry how many points are still needed, closest first,
        # so the UI can say "40 more points to unlock".
        locked = [
            LockedOffer(**o.model_dump(), points_needed=o.points_required - points)
            for o in by_cost
            if o.points_required > points
        ]

        return OffersResponse(points=points, eligible=eligible, locked=locked)