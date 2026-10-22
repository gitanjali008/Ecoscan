from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.config import Settings, get_settings
from app.data.carbon_factors import CarbonFactorRepository
from app.dependencies import get_analysis_service, get_carbon_factors, get_offers_service, get_scoring_service
from app.schemas import AnalysisResponse, CarbonFactorsResponse, OffersResponse, ScoreRequest, ScoreResponse
from app.services.analysis import AnalysisService
from app.services.offers import OffersService
from app.services.scoring import ScoringService

router = APIRouter()


@router.get("/health")
def health():
    """Check that the API is running."""
    return {"status": "ok"}


# Sync def: the OpenAI client is sync, so FastAPI runs this in a worker thread.
@router.post("/analyze", response_model=AnalysisResponse, summary="Scan a photo of clothing")
def analyze(
    file: UploadFile = File(..., description="A JPEG, PNG or WebP photo"),
    settings: Settings = Depends(get_settings),
    analysis: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    """Upload a photo and get the clothing items found in it, each item's carbon
    footprint and reward points, the totals, and the offers those points unlock.

    Errors: 400 empty_image, 413 image_too_large, 415 invalid_image,
    422 no_clothing_detected, 502 vision_service_error.
    """
    # Read one byte past the limit: enough to know a file is too large without loading all of it.
    data = file.file.read(settings.max_image_bytes + 1)
    return analysis.analyze(data, file.content_type)


@router.post("/score", response_model=ScoreResponse, summary="Score a list of items")
def score(
    request: ScoreRequest,
    scoring: ScoringService = Depends(get_scoring_service),
) -> ScoreResponse:
    """Recalculate carbon footprint and points for a list of items, without a photo.

    Used after the user corrects what the scan detected (e.g. marks an item as
    second-hand or changes its material).
    """
    return scoring.score(request.items)


@router.get("/offers", response_model=OffersResponse, summary="Offers for a points balance")
def offers(
    points: int = Query(..., ge=0, description="The user's eco-reward points"),
    offers_service: OffersService = Depends(get_offers_service),
) -> OffersResponse:
    """Offers the user can redeem now (eligible) and the rest (locked), each
    locked offer with how many more points it needs.
    """
    return offers_service.offers_for(points)


@router.get("/carbon-factors", response_model=CarbonFactorsResponse, summary="Carbon assumptions")
def carbon_factors(
    factors: CarbonFactorRepository = Depends(get_carbon_factors),
) -> CarbonFactorsResponse:
    """The numbers every score is based on:
    actual_kg = base_kg x material_factor x condition_factor.
    """
    return CarbonFactorsResponse(**factors.all_factors())
