import pytest
from pydantic import ValidationError

from app.schemas import LABEL_MAX_LENGTH, DetectedItem, ScoreRequest


def test_item_is_normalised():
    item = DetectedItem(category="  T-Shirt ", material=" Organic Cotton ")

    assert item.category == "t-shirt"
    assert item.material == "organic cotton"


def test_defaults_are_applied():
    item = DetectedItem(category="jeans")

    assert item.material == "unknown"
    assert item.condition == "new"
    assert item.confidence == 1.0
    assert item.label is None


def test_label_is_trimmed_and_keeps_its_case():
    assert DetectedItem(category="dress", label="  Red floral midi dress ").label == "Red floral midi dress"


def test_blank_label_becomes_none():
    assert DetectedItem(category="dress", label="   ").label is None


def test_long_label_is_cut_short_instead_of_rejected():
    item = DetectedItem(category="dress", label="x" * 500)

    assert item.label == "x" * LABEL_MAX_LENGTH


@pytest.mark.parametrize("word", ["used", "Thrifted", "second hand", "pre-owned"])
def test_second_hand_aliases(word):
    assert DetectedItem(category="jacket", condition=word).condition == "second-hand"


def test_empty_category_is_rejected():
    with pytest.raises(ValidationError):
        DetectedItem(category="   ")


def test_unknown_condition_is_rejected():
    with pytest.raises(ValidationError):
        DetectedItem(category="jeans", condition="broken")


def test_confidence_must_be_between_0_and_1():
    with pytest.raises(ValidationError):
        DetectedItem(category="jeans", confidence=1.5)


def test_score_request_needs_at_least_one_item():
    with pytest.raises(ValidationError):
        ScoreRequest(items=[])