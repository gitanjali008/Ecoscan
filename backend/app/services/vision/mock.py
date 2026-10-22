"""A mock vision provider: no API key, no network, predictable output.

It picks one of a few fixed outfits from a hash of the image bytes, so the same
photo always gives the same items (stable tests) while different photos give
different results (a more realistic demo).
"""

import hashlib

from app.schemas import DetectedItem

# Each scenario shows a different part of the scoring model.
DEFAULT_SCENARIOS: list[list[DetectedItem]] = [
    [  # Conventional new outfit: little or nothing saved.
        DetectedItem(category="t-shirt", material="cotton", condition="new", confidence=0.94),
        DetectedItem(category="jeans", material="cotton", condition="new", confidence=0.91),
    ],
    [  # Better materials.
        DetectedItem(category="t-shirt", material="organic cotton", condition="new", confidence=0.88),
        DetectedItem(category="trousers", material="linen", condition="new", confidence=0.83),
    ],
    [  # Second-hand pieces: the biggest savings.
        DetectedItem(category="jacket", material="recycled polyester", condition="second-hand", confidence=0.86),
        DetectedItem(category="sweater", material="wool", condition="second-hand", confidence=0.79),
        DetectedItem(category="shoes", material="leather", condition="new", confidence=0.72),
    ],
]


class MockVisionProvider:
    """VisionProvider that returns a scenario chosen by the image's content."""

    name = "mock"

    def __init__(self, scenarios: list[list[DetectedItem]] = DEFAULT_SCENARIOS) -> None:
        if not scenarios:
            raise ValueError("MockVisionProvider needs at least one scenario")
        self._scenarios = scenarios

    def detect_items(self, image: bytes, content_type: str) -> list[DetectedItem]:
        digest = hashlib.sha256(image).digest()
        scenario = self._scenarios[int.from_bytes(digest[:4], "big") % len(self._scenarios)]
        # Copies, so a caller changing an item cannot change the scenario itself.
        return [item.model_copy() for item in scenario]
