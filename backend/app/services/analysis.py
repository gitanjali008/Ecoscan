"""One scan, end to end: image -> items -> carbon and points -> offers.

The /analyze route only reads the upload and calls this, so the whole flow can
be tested without HTTP.
"""

from app.errors import NoClothingDetectedError
from app.schemas import AnalysisResponse
from app.services.image_validation import validate_image
from app.services.offers import OffersService
from app.services.scoring import ScoringService
from app.services.vision import VisionProvider


class AnalysisService:
    def __init__(
        self,
        vision: VisionProvider,
        scoring: ScoringService,
        offers: OffersService,
        max_image_bytes: int,
    ) -> None:
        self._vision = vision
        self._scoring = scoring
        self._offers = offers
        self._max_image_bytes = max_image_bytes

    def analyze(self, image: bytes, content_type: str | None) -> AnalysisResponse:
        # The real type from the file's bytes, not the one the client claimed.
        image_type = validate_image(image, content_type, self._max_image_bytes)

        items = self._vision.detect_items(image, image_type)
        if not items:
            raise NoClothingDetectedError()

        score = self._scoring.score(items)
        offers = self._offers.offers_for(score.total_points)
        return AnalysisResponse(**score.model_dump(), offers=offers)
