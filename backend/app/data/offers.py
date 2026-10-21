"""Offers users can unlock with eco-reward points, stored in memory.

Partners are fictional demo names. Read only through OfferRepository so a
database or partner API can replace this list later.
"""

from typing import Protocol

from app.schemas import Offer

OFFERS: list[Offer] = [
    Offer(id="swap-pass", title="Free clothing swap entry", partner="Swap Circle",
          description="One free ticket to a local clothing swap event.", points_required=30),
    Offer(id="thrift-10", title="10% off second-hand fashion", partner="ReLoop Thrift",
          description="10% off your next purchase at a partner thrift store.", points_required=50),
    Offer(id="repair-free", title="Free clothing repair", partner="StitchBack Repairs",
          description="One free basic repair: a zip, a hem or a seam.", points_required=100),
    Offer(id="plant-tree", title="Plant a tree", partner="Green Roots",
          description="We plant a tree in your name.", points_required=150),
    Offer(id="rental-20", title="20% off clothing rental", partner="Wardrobe Share",
          description="20% off your first month of clothing rental.", points_required=250),
    Offer(id="organic-15", title="15% off organic basics", partner="Pure Thread",
          description="15% off organic cotton t-shirts and basics.", points_required=400),
]


class OfferRepository(Protocol):
    def list_all(self) -> list[Offer]: ...


class InMemoryOffers:
    def __init__(self, offers: list[Offer] = OFFERS) -> None:
        self._offers = offers

    def list_all(self) -> list[Offer]:
        return list(self._offers)