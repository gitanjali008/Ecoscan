"""Pydantic models: the single source of truth for data shapes.

Every layer (routes, services, tests, frontend via /docs) agrees on these
contracts, and FastAPI uses them to validate input and return 422 on bad data.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Condition = Literal["new", "second-hand"]

# Words a vision model (or a user) might use for a pre-owned item.
_SECOND_HAND_ALIASES = {"second-hand", "second hand", "secondhand", "used", "pre-owned", "preowned", "thrifted", "vintage"}


LABEL_MAX_LENGTH = 80


class DetectedItem(BaseModel):
    """One clothing item as recognised in the image (or sent by the client)."""

    category: str = Field(..., examples=["t-shirt"])
    material: str = Field("unknown", examples=["organic cotton"])
    condition: Condition = "new"
    confidence: float = Field(1.0, ge=0, le=1)
    label: str | None = Field(None, examples=["red floral midi dress"], description="Short human description")

    @field_validator("category")
    @classmethod
    def _clean_category(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("category must not be empty")
        return value

    @field_validator("material")
    @classmethod
    def _clean_material(cls, value: str) -> str:
        return value.strip().lower() or "unknown"

    @field_validator("label")
    @classmethod
    def _clean_label(cls, value: str | None) -> str | None:
        # Optional and only for display: a blank one is dropped, a long one cut short.
        if value is None:
            return None
        return value.strip()[:LABEL_MAX_LENGTH] or None

    @field_validator("condition", mode="before")
    @classmethod
    def _normalise_condition(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().lower()
            return "second-hand" if value in _SECOND_HAND_ALIASES else value
        return value


class ScoredItem(DetectedItem):
    """A detected item plus its carbon numbers and reward points."""

    baseline_kg: float = Field(..., ge=0, description="Footprint of the same item bought new, conventional material")
    actual_kg: float = Field(..., ge=0, description="Footprint after material and condition adjustments")
    saved_kg: float = Field(..., ge=0, description="baseline_kg - actual_kg")
    points: int = Field(..., ge=0)
    tip: str = Field(..., examples=["Great choice! Buying it second-hand saved about 8 kg of CO2."])


class ScoreRequest(BaseModel):
    """Body for POST /api/score, e.g. after the user edits detected items."""

    items: list[DetectedItem] = Field(..., min_length=1)


class ScoreResponse(BaseModel):
    items: list[ScoredItem]
    total_carbon_kg: float
    total_saved_kg: float
    total_points: int


class Offer(BaseModel):
    id: str
    title: str
    partner: str
    description: str
    points_required: int = Field(..., ge=0)


class LockedOffer(Offer):
    points_needed: int = Field(..., gt=0, description="How many more points unlock this offer")


class OffersResponse(BaseModel):
    points: int
    eligible: list[Offer]
    locked: list[LockedOffer]


class AnalysisResponse(ScoreResponse):
    """Everything the UI needs after one scan, in a single response."""

    offers: OffersResponse
    provider: str = Field(
        ..., examples=["gemini"], description='The vision provider that read the photo; "mock" means sample results'
    )


class CarbonFactorsResponse(BaseModel):
    """The carbon assumptions behind every score: actual_kg = base_kg x material x condition."""

    base_kg: dict[str, float] = Field(..., description="kg CO2e for one new item, by category")
    default_kg: float = Field(..., description="Used for categories not in base_kg")
    material_factor: dict[str, float] = Field(..., description="Multiplier vs a conventional material (1.0)")
    condition_factor: dict[str, float] = Field(..., description="Multiplier for new vs second-hand")