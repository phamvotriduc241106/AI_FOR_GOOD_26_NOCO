"""Deterministic prospect ranking and illustrative NOCO opportunities."""

from __future__ import annotations

import math

from .calc import estimate_insulation, inputs_from_facts
from .contract import (
    INCENTIVE_PROGRAM,
    NOT_IN_PUBLIC_DATA,
    UTILITY,
    Assumptions,
    BuildingFacts,
    CalcResult,
    Opportunity,
    Prospect,
)


def build_opportunity(f: BuildingFacts, r: CalcResult, a: Assumptions) -> Opportunity:
    """Use calculator cost and explicit margin; unknown money remains unavailable."""
    margin = a.margin_pct
    if margin is not None and (not math.isfinite(margin) or not 0 <= margin <= 1):
        raise ValueError("margin_pct must be a finite fraction between 0 and 1")

    revenue = r.project_cost if a.cost_per_sqft is not None else None
    profit = revenue * margin if revenue is not None and margin is not None else None
    notes = [
        "ILLUSTRATIVE: revenue and profit are scenarios, not validated NOCO quotes.",
        f"Utility: {UTILITY} [noco_sheet]. Program: {INCENTIVE_PROGRAM} "
        "[noco_sheet reference]; eligibility needs confirmation.",
        NOT_IN_PUBLIC_DATA,
    ]
    if revenue is None:
        notes.append("Project revenue and profit unavailable: needs NOCO cost [user].")
    else:
        notes.append(
            "ILLUSTRATIVE project revenue = calculator project cost: insulated wall area "
            "[deterministic NOCO calculation + GIS/assumptions] × cost per sq ft [user]."
        )
    if margin is None:
        notes.append("Estimated profit unavailable: needs NOCO margin [user].")
    else:
        notes.append(f"ILLUSTRATIVE margin fraction={margin:g} [user].")
    if profit is not None:
        notes.append("ILLUSTRATIVE estimated profit = project revenue × margin fraction [user].")

    return Opportunity(
        utility=UTILITY,
        incentive_program=INCENTIVE_PROGRAM,
        current_supplier=NOT_IN_PUBLIC_DATA,
        project_revenue=revenue,
        estimated_profit=profit,
        margin_pct=margin,
        illustrative=True,
        notes=notes,
    )


def rank_prospects(items: list[BuildingFacts], a: Assumptions, top: int = 25) -> list[Prospect]:
    """Rank by annual savings, shorter known payback, then address; ranks start at 1."""
    prospects: list[Prospect] = []
    for facts in items:
        inputs = inputs_from_facts(facts, a)
        result = estimate_insulation(inputs)
        prospects.append(
            Prospect(
                facts=facts,
                inputs=inputs,
                result=result,
                opportunity=build_opportunity(facts, result, a),
                score=result.annual_cost_savings,
                rank=0,
            )
        )
    prospects.sort(
        key=lambda prospect: (
            -prospect.score,
            prospect.result.simple_payback_years
            if prospect.result.simple_payback_years is not None
            else math.inf,
            prospect.facts.address,
        )
    )
    selected = prospects[: max(0, top)]
    for rank, prospect in enumerate(selected, 1):
        prospect.rank = rank
    return selected
