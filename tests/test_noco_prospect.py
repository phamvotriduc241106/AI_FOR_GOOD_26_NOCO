from __future__ import annotations

from pathlib import Path

import pytest

from features.noco_scout import prospect
from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import (
    INCENTIVE_PROGRAM,
    NOT_IN_PUBLIC_DATA,
    UTILITY,
    Assumptions,
    BuildingFacts,
    CalcInputs,
    CalcResult,
    Prospect,
)
from features.noco_scout.fixtures import SAMPLE_BUILDINGS


@pytest.mark.parametrize(
    ("cost", "margin", "expected_revenue", "expected_profit"),
    [
        (None, None, None, None),
        (None, 0.2, None, None),
        (8.0, None, 31_200.0, None),
        (8.0, 0.2, 31_200.0, 6_240.0),
        (8.0, 0.0, 31_200.0, 0.0),
        (0.0, 0.2, 0.0, 0.0),
        (8.0, 1.0, 31_200.0, 31_200.0),
    ],
)
def test_opportunity_money_requires_explicit_cost_and_margin(
    cost: float | None,
    margin: float | None,
    expected_revenue: float | None,
    expected_profit: float | None,
) -> None:
    facts = SAMPLE_BUILDINGS[0].model_copy(update={"perimeter_ft": 500.0, "floors": 1})
    assumptions = Assumptions(cost_per_sqft=cost, margin_pct=margin)
    result = estimate_insulation(inputs_from_facts(facts, assumptions))

    opportunity = prospect.build_opportunity(facts, result, assumptions)

    assert opportunity.project_revenue == expected_revenue
    assert opportunity.estimated_profit == expected_profit
    assert opportunity.margin_pct == margin
    assert opportunity.illustrative is True
    assert opportunity.utility == UTILITY == "National Grid"
    assert opportunity.incentive_program == INCENTIVE_PROGRAM
    assert opportunity.current_supplier == NOT_IN_PUBLIC_DATA
    notes = " ".join(opportunity.notes)
    assert "ILLUSTRATIVE" in notes
    assert "National Grid [noco_sheet]" in notes
    if cost is None:
        assert "needs NOCO cost" in notes
        assert result.simple_payback_years is None
    if margin is None:
        assert "needs NOCO margin" in notes
    else:
        assert f"margin fraction={margin:g} [user]" in notes


def test_unknown_cost_does_not_reuse_a_stale_calculator_cost() -> None:
    facts = SAMPLE_BUILDINGS[0]
    result = estimate_insulation(inputs_from_facts(facts, Assumptions(cost_per_sqft=8.0)))

    opportunity = prospect.build_opportunity(facts, result, Assumptions(margin_pct=0.2))

    assert opportunity.project_revenue is None
    assert opportunity.estimated_profit is None


@pytest.mark.parametrize("margin", [-0.01, 1.01, float("nan"), float("inf")])
def test_invalid_margin_cannot_produce_illustrative_profit(margin: float) -> None:
    facts = SAMPLE_BUILDINGS[0]
    assumptions = Assumptions(cost_per_sqft=8.0, margin_pct=margin)
    result = estimate_insulation(inputs_from_facts(facts, assumptions))

    with pytest.raises(ValueError, match="margin_pct"):
        prospect.build_opportunity(facts, result, assumptions)


def test_ranking_uses_calculator_outputs_and_preserves_inputs() -> None:
    items = [facts.model_copy(deep=True) for facts in reversed(SAMPLE_BUILDINGS)]
    assumptions = Assumptions(cost_per_sqft=8.0, margin_pct=0.2)
    before = [facts.model_dump() for facts in items], assumptions.model_dump()

    ranked = prospect.rank_prospects(items, assumptions, top=len(items))

    assert [item.rank for item in ranked] == list(range(1, len(items) + 1))
    assert [item.score for item in ranked] == sorted([item.score for item in ranked], reverse=True)
    assert {item.facts.address for item in ranked} == {facts.address for facts in items}
    for item in ranked:
        expected_inputs = inputs_from_facts(item.facts, assumptions)
        assert item.inputs == expected_inputs
        assert item.result == estimate_insulation(expected_inputs)
        assert item.score == item.result.annual_cost_savings
        assert item.opportunity.project_revenue == item.result.project_cost
        assert item.opportunity.estimated_profit == pytest.approx(item.result.project_cost * 0.2)
    assert ([facts.model_dump() for facts in items], assumptions.model_dump()) == before
    assert ranked == prospect.rank_prospects(list(reversed(items)), assumptions, top=len(items))


def test_equal_savings_sort_by_known_payback_then_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scenarios = [
        ("Z high savings", 500.0, None),
        ("Z short payback", 100.0, 2.0),
        ("A short payback", 100.0, 2.0),
        ("A long payback", 100.0, 5.0),
        ("A unknown payback", 100.0, None),
        ("A low savings", 50.0, 0.0),
    ]
    items = [
        SAMPLE_BUILDINGS[0].model_copy(update={"address": address, "perimeter_ft": index + 100})
        for index, (address, _, _) in enumerate(scenarios)
    ]
    base = estimate_insulation(inputs_from_facts(SAMPLE_BUILDINGS[0], Assumptions()))

    def calculate(inputs: CalcInputs) -> CalcResult:
        _, savings, payback = scenarios[int(inputs.perimeter_ft) - 100]
        return base.model_copy(
            update={"annual_cost_savings": savings, "simple_payback_years": payback}
        )

    monkeypatch.setattr(prospect, "estimate_insulation", calculate)

    ranked = prospect.rank_prospects(items, Assumptions(), top=len(items))

    assert [item.facts.address for item in ranked] == [
        "Z high savings",
        "A short payback",
        "Z short payback",
        "A long payback",
        "A unknown payback",
        "A low savings",
    ]


@pytest.mark.parametrize(("top", "count"), [(0, 0), (-1, 0), (3, 3), (40, 40), (50, 40)])
def test_requested_top_count_is_respected_without_a_hidden_default_cap(
    top: int, count: int
) -> None:
    items = [
        SAMPLE_BUILDINGS[0].model_copy(update={"address": f"{index:03d} Example St, Buffalo, NY"})
        for index in reversed(range(40))
    ]

    ranked = prospect.rank_prospects(items, Assumptions(), top=top)

    assert len(ranked) == count
    assert [item.rank for item in ranked] == list(range(1, count + 1))
    assert [item.facts.address for item in ranked] == sorted(f.address for f in items)[:count]
    assert len(prospect.rank_prospects(items, Assumptions())) == 25


def test_empty_input_and_missing_geometry_keep_contract_behavior() -> None:
    assert prospect.rank_prospects([], Assumptions()) == []
    missing = BuildingFacts(address="Synthetic Buffalo building", lat=42.88, lon=-78.87)

    ranked = prospect.rank_prospects([missing], Assumptions(), top=1)

    assert len(ranked) == 1
    assert ranked[0].rank == 1
    assert any("assumed" in flag for flag in ranked[0].result.flags)
    assert ranked[0].result.simple_payback_years is None
    assert ranked[0].opportunity.project_revenue is None
    assert ranked[0].opportunity.estimated_profit is None


def test_existing_pages_delegate_to_t5_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "app"))
    monkeypatch.setenv("NOCO_OFFLINE", "1")
    from pages import noco_shared

    from features.noco_scout import geo

    monkeypatch.setattr(
        geo, "_http_get_json", lambda *_args, **_kwargs: pytest.fail("unexpected network call")
    )
    calls: list[int] = []
    rank = prospect.rank_prospects

    def record_rank(items: list[BuildingFacts], a: Assumptions, top: int = 25) -> list[Prospect]:
        calls.append(top)
        return rank(items, a, top=top)

    monkeypatch.setattr(prospect, "rank_prospects", record_rank)
    assumptions = Assumptions(cost_per_sqft=8.0, margin_pct=0.2)

    ranked = noco_shared.rank_buildings(SAMPLE_BUILDINGS, assumptions)
    single = noco_shared.make_prospect(SAMPLE_BUILDINGS[0], assumptions)

    assert calls == [len(SAMPLE_BUILDINGS)]
    assert len(ranked) == len(SAMPLE_BUILDINGS)
    assert single.opportunity == prospect.build_opportunity(
        single.facts, single.result, assumptions
    )
    assert any("noco_sheet" in note for note in single.opportunity.notes)
