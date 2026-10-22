import pytest

from app.data.carbon_factors import InMemoryCarbonFactors
from app.schemas import DetectedItem
from app.services.carbon import CarbonService
from app.services.tips import TIP_RULES, EcoTipService, TipRule, _kg

factors = InMemoryCarbonFactors()
carbon = CarbonService(factors)
tips = EcoTipService(carbon, factors)


def tip(**item) -> str:
    return tips.tip_for(carbon.score_item(DetectedItem(**item)))


# One test per rule.

def test_second_hand_is_praised_with_the_kg_saved():
    # jeans: 10 kg new, 2 kg second-hand -> 8 kg saved
    assert tip(category="jeans", material="cotton", condition="second-hand") == (
        "Great choice! Buying it second-hand saved about 8 kg of CO2."
    )


def test_second_hand_wins_over_a_high_impact_material():
    assert tip(category="sweater", material="wool", condition="second-hand").startswith("Great choice!")


@pytest.mark.parametrize(
    "material, care",
    [
        ("wool", "air it between wears and wash it cool by hand"),
        ("merino wool", "air it between wears and wash it cool by hand"),
        ("leather", "clean and condition it, and repair it instead of replacing it"),
        ("nylon", "wash it cool and fix small damage early"),  # factor 1.1, no specific care tip
    ],
)
def test_new_high_impact_material_gets_a_care_tip(material, care):
    assert tip(category="jacket", material=material) == (
        f"{material.capitalize()} has a higher footprint, so make it last: {care}."
    )


def test_new_low_impact_material_is_praised_with_the_kg_saved():
    # t-shirt: 5 kg x 0.7 = 3.5 kg -> 1.5 kg saved
    assert tip(category="t-shirt", material="organic cotton") == (
        "Nice pick! Organic cotton saved about 1.5 kg of CO2 compared with a conventional material."
    )


def test_new_cotton_suggests_second_hand_and_organic_cotton_with_the_kg_they_save():
    # jeans: second-hand saves 10 - 2 = 8 kg; organic cotton saves 10 - 7 = 3 kg
    assert tip(category="jeans", material="cotton") == (
        "Next time, try it second-hand to save about 8 kg of CO2. Organic cotton would save about 3 kg."
    )


def test_new_polyester_suggests_recycled_polyester():
    # dress: second-hand saves 9 - 1.8 = 7.2 kg; recycled polyester saves 9 - 5.4 = 3.6 kg
    assert tip(category="dress", material="cotton/polyester blend") == (
        "Next time, try it second-hand to save about 7.2 kg of CO2. Recycled polyester would save about 3.6 kg."
    )


def test_new_unknown_material_only_suggests_second_hand():
    # shoes: 8 kg new -> 6.4 kg saved second-hand
    assert tip(category="shoes", material="unknown") == "Next time, try it second-hand to save about 6.4 kg of CO2."


def test_unknown_category_uses_the_default_footprint():
    # default 7 kg -> 5.6 kg saved second-hand
    assert tip(category="kimono") == "Next time, try it second-hand to save about 5.6 kg of CO2."


@pytest.mark.parametrize("kg, text", [(8.0, "8 kg"), (3.5, "3.5 kg"), (1.26, "1.3 kg"), (0.3, "0.3 kg"), (0.04, "under 0.1 kg")])
def test_kg_is_rounded_and_a_tiny_saving_is_not_shown_as_zero(kg, text):
    assert _kg(kg) == text


def test_rules_are_checked_in_order_and_can_be_replaced():
    custom = EcoTipService(carbon, factors, rules=[
        TipRule("never", lambda ctx: False, lambda ctx: "not this"),
        TipRule("always", lambda ctx: True, lambda ctx: f"{ctx.item.category} tip"),
    ])

    assert custom.tip_for(carbon.score_item(DetectedItem(category="jeans"))) == "jeans tip"


def test_every_item_gets_a_tip_because_the_last_rule_always_applies():
    assert TIP_RULES[-1].name == "new conventional"
    assert TIP_RULES[-1].applies(None)
