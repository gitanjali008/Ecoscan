import json
import re

import pytest

from app.data.carbon_factors import BASE_CARBON_KG, InMemoryCarbonFactors
from app.errors import VisionServiceError
from app.services.vision.prompt import build_system_prompt, parse_items

PROMPT = build_system_prompt(InMemoryCarbonFactors().categories())


def test_lists_every_known_category():
    known = PROMPT.split("Known categories: ")[1]

    assert known.split(", ") == list(BASE_CARBON_KG)


def test_categories_are_not_aliases():
    assert InMemoryCarbonFactors().categories() == list(BASE_CARBON_KG)


def test_example_reply_is_valid_and_parses_into_an_item():
    example = re.search(r"^\{\"items\".*\}$", PROMPT, re.MULTILINE).group(0)

    [item] = parse_items(example)

    assert item.label == "red floral midi dress"
    assert json.loads(example)["items"][0].keys() == {"category", "material", "condition", "confidence", "label"}


def test_asks_for_every_item_and_the_rules():
    assert "EVERY item of clothing, footwear and accessory" in PROMPT
    assert "one of the known categories below when it fits" in PROMPT
    assert '"unknown"' in PROMPT
    assert 'exactly "new" or "second-hand"' in PROMPT
    assert "thrift or vintage listing" in PROMPT
    assert "from 0 to 1" in PROMPT
    assert "label:" in PROMPT
    assert 'reply {"items": []}' in PROMPT
    assert "ONLY a JSON object" in PROMPT


def test_without_categories_the_prompt_still_reads_well():
    assert build_system_prompt([]).endswith("Known categories: (none)")


def test_parse_items_accepts_json_in_a_code_fence():
    assert [i.category for i in parse_items('```json\n{"items": [{"category": "saree"}]}\n```')] == ["saree"]


def test_parse_items_still_rejects_a_broken_fence():
    with pytest.raises(VisionServiceError):
        parse_items('```json\n{"items": [')
