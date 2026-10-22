"""FastAPI dependencies: the one place where services are wired together.

Repositories and the vision provider are cached, so they are built once per
process. Services are cheap and built per request. Tests replace any of these
with app.dependency_overrides, e.g. get_vision_provider -> a mock.
"""

from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.data.carbon_factors import CarbonFactorRepository, InMemoryCarbonFactors
from app.data.offers import InMemoryOffers, OfferRepository
from app.services.analysis import AnalysisService
from app.services.carbon import CarbonService
from app.services.offers import OffersService
from app.services.rewards import RewardsService
from app.services.scoring import ScoringService
from app.services.tips import EcoTipService
from app.services.vision import VisionProvider, create_vision_provider


@lru_cache
def get_carbon_factors() -> CarbonFactorRepository:
    return InMemoryCarbonFactors()


@lru_cache
def get_offer_repository() -> OfferRepository:
    return InMemoryOffers()


@lru_cache
def get_vision_provider() -> VisionProvider:
    # Cached so the OpenAI client (and its connection pool) is reused.
    return create_vision_provider(get_settings(), get_carbon_factors().categories())


def get_scoring_service(
    settings: Settings = Depends(get_settings),
    factors: CarbonFactorRepository = Depends(get_carbon_factors),
) -> ScoringService:
    carbon = CarbonService(factors)
    return ScoringService(carbon, RewardsService(settings.points_per_kg), EcoTipService(carbon, factors))


def get_offers_service(offers: OfferRepository = Depends(get_offer_repository)) -> OffersService:
    return OffersService(offers)


def get_analysis_service(
    settings: Settings = Depends(get_settings),
    vision: VisionProvider = Depends(get_vision_provider),
    scoring: ScoringService = Depends(get_scoring_service),
    offers: OffersService = Depends(get_offers_service),
) -> AnalysisService:
    return AnalysisService(vision, scoring, offers, settings.max_image_bytes)
