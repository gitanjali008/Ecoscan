from fastapi import APIRouter, Depends, File, UploadFile

from app.config import Settings, get_settings
from app.dependencies import get_analysis_service
from app.schemas import AnalysisResponse
from app.services.analysis import AnalysisService

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


# Sync def: the OpenAI client is sync, so FastAPI runs this in a worker thread.
@router.post("/analyze", response_model=AnalysisResponse)
def analyze(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    analysis: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    # Read one byte past the limit: enough to know a file is too large without loading all of it.
    data = file.file.read(settings.max_image_bytes + 1)
    return analysis.analyze(data, file.content_type)
