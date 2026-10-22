"""The prompt shared by every real vision provider.

Keeping it in one place means each provider asks the same question and gets
answers in the same shape, which parse_items in each provider then checks.
Giving the model the known categories makes it pick names the carbon table
recognises, instead of falling back to the default footprint.
"""

from collections.abc import Iterable

USER_PROMPT = "List every clothing item, footwear and accessory in this image."

_TEMPLATE = """You identify clothing in photos for a carbon footprint app.
Reply with ONLY a JSON object, no other text, in exactly this shape:
{{"items": [{{"category": "dress", "material": "polyester", "condition": "new", "confidence": 0.9, "label": "red floral midi dress"}}]}}
Rules:
- Detect EVERY item of clothing, footwear and accessory that is visible (e.g. bag, belt, scarf, cap), one entry per item. If two similar items are visible, list both. Ignore people, furniture and everything else.
- category: one of the known categories below when it fits. Otherwise a short generic name in lowercase.
- material: your best guess of the main fabric or material in lowercase, e.g. "cotton", "organic cotton", "polyester", "wool", "leather". Use "unknown" if you cannot tell.
- condition: exactly "new" or "second-hand". Use "second-hand" only if there are visible signs of wear (fading, pilling, stretched or worn areas) or the photo looks like a thrift or vintage listing. Otherwise use "new".
- confidence: a number from 0 to 1 for how sure you are about the item.
- label: a short description a person would recognise, e.g. "red floral midi dress", "white canvas sneakers".
- If there is no clothing, footwear or accessory in the image, reply {{"items": []}}.
Known categories: {categories}"""


def build_system_prompt(categories: Iterable[str]) -> str:
    """The system prompt, listing the categories the carbon table knows."""
    return _TEMPLATE.format(categories=", ".join(categories) or "(none)")
