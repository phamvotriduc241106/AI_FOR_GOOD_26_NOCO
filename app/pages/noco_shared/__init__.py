"""Shared presentation helpers for the two Buffalo NOCO pages."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from types import ModuleType
from urllib.parse import quote

import pydeck as pdk
import streamlit as st

from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import (
    INCENTIVE_PROGRAM,
    OSM_ATTRIBUTION,
    Assumptions,
    BuildingFacts,
    Opportunity,
    Prospect,
)
from features.noco_scout.fixtures import SAMPLE_BUILDINGS
from features.noco_scout.mapdata import TOOLTIP_TEMPLATE, prospects_to_deck_rows

REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_DATA = REPO_ROOT / "data/public/demo_buildings.json"
LAYER_ID = "noco-buildings"
BLANK_MAP_STYLE = "data:application/json," + quote(
    json.dumps({"version": 8, "sources": {}, "layers": []})
)


def offline_mode() -> bool:
    """Honor the demo's explicit no-network setting."""
    return os.environ.get("NOCO_OFFLINE") == "1"


def _optional_module(name: str) -> ModuleType | None:
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name == name:
            return None
        raise


def load_buildings() -> tuple[list[BuildingFacts], bool]:
    """Use T7's saved public data when present, else T1's five synthetic samples."""
    if DEMO_DATA.is_file():
        geo = _optional_module("features.noco_scout.geo")
        if geo is not None:
            return geo.load_demo_buildings(), False
        records = json.loads(DEMO_DATA.read_text(encoding="utf-8"))
        return [BuildingFacts.model_validate(record) for record in records], False
    return list(SAMPLE_BUILDINGS), True


def find_building(address: str, available: list[BuildingFacts]) -> BuildingFacts | None:
    """Look up a typed address; the house number must match exactly (no substring matches).

    First the buildings already on the page (T3's address normalisation), then T3's lookup:
    offline it reads the saved demo set and the cache only and returns None when the address
    is not there; online it may call the public services (ValueError reaches the page).
    """
    if not address.strip():
        return None
    geo = _optional_module("features.noco_scout.geo")
    if geo is None:
        query = address.strip().casefold()
        return next((f for f in available if f.address.casefold() == query), None)
    found = geo.match_address(address, available)
    if found is not None:
        return found
    if offline_mode():
        try:
            return geo.build_facts(address, offline=True)
        except ValueError:
            return None
    return geo.build_facts(address)


def make_prospect(facts: BuildingFacts, assumptions: Assumptions, rank: int = 1) -> Prospect:
    """Calculate a map record; T5 supplies the opportunity model when available."""
    inputs = inputs_from_facts(facts, assumptions)
    result = estimate_insulation(inputs)
    prospect_module = _optional_module("features.noco_scout.prospect")
    opportunity = (
        prospect_module.build_opportunity(facts, result, assumptions)
        if prospect_module is not None
        else Opportunity(
            incentive_program=INCENTIVE_PROGRAM,
            project_revenue=result.project_cost,
            estimated_profit=(
                result.project_cost * assumptions.margin_pct
                if result.project_cost is not None and assumptions.margin_pct is not None
                else None
            ),
            margin_pct=assumptions.margin_pct,
            notes=["ILLUSTRATIVE: project cost and margin are user-entered assumptions."],
        )
    )
    return Prospect(
        facts=facts,
        inputs=inputs,
        result=result,
        opportunity=opportunity,
        score=result.annual_cost_savings,
        rank=rank,
    )


def rank_buildings(buildings: list[BuildingFacts], assumptions: Assumptions) -> list[Prospect]:
    """Use T5 ranking when merged; keep a deterministic sample preview meanwhile."""
    prospect_module = _optional_module("features.noco_scout.prospect")
    if prospect_module is not None:
        return prospect_module.rank_prospects(buildings, assumptions, top=len(buildings))
    prospects = [make_prospect(facts, assumptions) for facts in buildings]
    prospects.sort(
        key=lambda prospect: (
            -prospect.score,
            prospect.result.simple_payback_years
            if prospect.result.simple_payback_years is not None
            else float("inf"),
            prospect.facts.address,
        )
    )
    for rank, prospect in enumerate(prospects, 1):
        prospect.rank = rank
    return prospects


def render_map(
    prospects: list[Prospect],
    *,
    key: str,
    center: tuple[float, float] | None = None,
    ranked: bool = True,
    height: int = 550,
) -> Prospect | None:
    """Draw 3D footprints and return the clicked prospect, if any."""
    rows = prospects_to_deck_rows(prospects)
    if not rows:
        st.info("No building footprint is available for the map.")
        return None
    if not ranked:
        for row in rows:
            row["color"] = [70, 133, 168, 185]

    if center is None:
        lat = sum(p.facts.lat for p in prospects) / len(prospects)
        lon = sum(p.facts.lon for p in prospects) / len(prospects)
        zoom = 16.3 if len(prospects) == 1 else 15.0 if len(prospects) <= 10 else 12.6
    else:
        lat, lon = center
        zoom = 16.5
    layer = pdk.Layer(
        "PolygonLayer",
        data=rows,
        id=LAYER_ID,
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color=[25, 48, 67, 230],
        get_line_width=1,
        get_elevation="elevation",
        elevation_scale=1,
        extruded=True,
        pickable=True,
        auto_highlight=True,
        stroked=True,
    )
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=zoom,
            pitch=50,
            bearing=-15,
        ),
        map_provider="maplibre" if offline_mode() else "carto",
        map_style=BLANK_MAP_STYLE if offline_mode() else "light",
        tooltip={
            "html": TOOLTIP_TEMPLATE,
            "style": {"backgroundColor": "#0c2436", "color": "#fff", "fontSize": "12px"},
        },
    )
    event = st.pydeck_chart(
        deck,
        key=key,
        on_select="rerun",
        selection_mode="single-object",
        height=height,
    )
    selected = event.selection.objects.get(LAYER_ID, [])
    if not selected:
        return None
    row = selected[0]
    index = row.get("prospect_index")
    if not isinstance(index, int) or not 0 <= index < len(prospects):
        return None
    prospect = prospects[index]
    return prospect if row.get("address") == prospect.facts.address else None


def fact_rows(facts: BuildingFacts) -> list[dict[str, str]]:
    """Keep each visible fact beside its own source and confidence."""
    fields = (
        ("address", "Address", facts.address),
        ("use_class", "Building use", facts.use_class or "unknown"),
        (
            "footprint_sqft",
            "Footprint",
            f"{facts.footprint_sqft:,.0f} sq ft" if facts.footprint_sqft is not None else "unknown",
        ),
        (
            "perimeter_ft",
            "Perimeter",
            f"{facts.perimeter_ft:,.0f} ft" if facts.perimeter_ft is not None else "unknown",
        ),
        ("floors", "Floors", str(facts.floors) if facts.floors is not None else "unknown"),
        (
            "floor_height_ft",
            "Floor height",
            f"{facts.floor_height_ft:g} ft" if facts.floor_height_ft is not None else "unknown",
        ),
    )
    rows: list[dict[str, str]] = []
    for field, label, value in fields:
        source = facts.sources.get(field)
        rows.append(
            {
                "Fact": label,
                "Value": value,
                "Source": source.source if source else "not recorded",
                "Confidence": f"{source.confidence:.2f}" if source else "not recorded",
                "Note": source.note if source else "",
            }
        )
    return rows


def show_fact_panel(facts: BuildingFacts) -> None:
    st.dataframe(fact_rows(facts), hide_index=True, width="stretch")
    st.caption(OSM_ATTRIBUTION)


def show_estimate(prospect: Prospect) -> None:
    result = prospect.result
    first, second, third = st.columns(3)
    first.metric("Annual savings · NOCO model + GIS", f"${result.annual_cost_savings:,.0f}")
    second.metric("Incentive · NOCO sheet", f"${result.incentive:,.0f}")
    third.metric(
        "Payback · ILLUSTRATIVE cost",
        f"{result.simple_payback_years:.1f} years"
        if result.simple_payback_years is not None
        else "Needs installed cost",
    )
    st.caption("Reference model reproduces NOCO's example; inferred HDD/CDD remain unconfirmed.")
    for flag in result.flags:
        st.warning(flag)
    with st.expander("Calculation sources and assumptions"):
        for assumption in result.assumptions:
            st.write(assumption)


def customer_report_button(prospect: Prospect) -> None:
    report = _optional_module("features.noco_scout.report")
    if report is None:
        st.button("Generate customer report", disabled=True, help="Available when T10 merges.")
        return
    document = report.render_customer_report(
        prospect.facts, prospect.inputs, prospect.result, prospect.opportunity
    )
    st.download_button(
        "Generate customer report",
        data=document,
        file_name="noco-customer-report.html",
        mime="text/html",
    )
