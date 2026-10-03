"""Safe, source-labelled building data for the Buffalo 3D map."""

from __future__ import annotations

import html
import math

from .contract import OSM_ATTRIBUTION, BuildingFacts, Prospect

FT_TO_M = 0.3048


def _source(facts: BuildingFacts, field: str) -> str:
    source = facts.sources.get(field)
    if source is None:
        return "source not recorded"
    return f"{source.source} ({source.confidence:.2f})"


def _money(value: float | None, missing: str) -> str:
    return f"${value:,.0f}" if value is not None else missing


def _source_summary(facts: BuildingFacts) -> str:
    parts: list[str] = []
    for field in ("address", "footprint_geojson", "floors", "use_class", "join"):
        source = facts.sources.get(field)
        if source is None:
            continue
        label = source.source
        if label == "osm" and facts.osm_id is not None:
            label = f"OSM way {facts.osm_id}"
        entry = f"{label} ({source.confidence:.2f})"
        if entry not in parts:
            parts.append(entry)
    if any("synthetic" in source.note.lower() for source in facts.sources.values()):
        parts.insert(0, "SYNTHETIC SAMPLE")
    parts.append(OSM_ATTRIBUTION)
    return " · ".join(parts)


def prospect_tooltip_html(p: Prospect) -> str:
    """Render the fixed tooltip order with escaped public data and explicit sources."""
    f = p.facts
    r = p.result
    opportunity = p.opportunity
    footprint = (
        f"{f.footprint_sqft:,.0f} sq ft" if f.footprint_sqft is not None else "not available"
    )
    floors = str(f.floors) if f.floors is not None else "unknown"
    payback = (
        f"{r.simple_payback_years:,.1f} years"
        if r.simple_payback_years is not None
        else "needs installed cost"
    )
    revenue = _money(opportunity.project_revenue, "needs NOCO cost")
    profit = _money(opportunity.estimated_profit, "needs NOCO margin")
    rows = [
        f"<strong>{html.escape(f.address)}</strong>",
        f"Use: {html.escape(f.use_class or 'unknown')} [{_source(f, 'use_class')}]",
        f"Floors: {floors} [{_source(f, 'floors')}]",
        f"Footprint: {footprint} [{_source(f, 'footprint_sqft')}]",
        f"Savings/year: {_money(r.annual_cost_savings, 'unavailable')} "
        "[deterministic NOCO calculation]",
        f"Incentive: {_money(r.incentive, 'unavailable')} [noco_sheet calculation]",
        f"Payback: {payback} [calculated from stated cost]",
        f"NOCO opportunity (ILLUSTRATIVE): revenue {revenue}; profit {profit}",
        f"Utility: {html.escape(opportunity.utility)} [noco_sheet]",
        f"Incentive program: {html.escape(opportunity.incentive_program or 'not confirmed')} "
        "[noco_sheet reference]",
        f"Current supplier: {html.escape(opportunity.current_supplier)}",
        f"Sources: {html.escape(_source_summary(f))}",
    ]
    return "<br/>".join(rows)


def _polygon(facts: BuildingFacts) -> list[list[float]] | None:
    geojson = facts.footprint_geojson
    if not isinstance(geojson, dict) or geojson.get("type") != "Polygon":
        return None
    coordinates = geojson.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates:
        return None
    ring = coordinates[0]
    if not isinstance(ring, list) or len(ring) < 3:
        return None
    polygon: list[list[float]] = []
    for pair in ring:
        if not isinstance(pair, (list, tuple)) or len(pair) < 2:
            return None
        try:
            lon, lat = float(pair[0]), float(pair[1])
        except (TypeError, ValueError):
            return None
        if not math.isfinite(lon) or not math.isfinite(lat):
            return None
        polygon.append([lon, lat])
    return polygon


def prospects_to_deck_rows(prospects: list[Prospect]) -> list[dict]:
    """Convert ranked prospects to PolygonLayer rows; omit missing footprints."""
    maximum = max(
        (p.score for p in prospects if math.isfinite(p.score) and p.score > 0),
        default=0.0,
    )
    rows: list[dict] = []
    for index, prospect in enumerate(prospects):
        polygon = _polygon(prospect.facts)
        if polygon is None:
            continue
        facts = prospect.facts
        strength = 0.0
        if maximum and math.isfinite(prospect.score):
            strength = max(0.0, prospect.score) / maximum
        floors = facts.floors if facts.floors is not None and facts.floors > 0 else 1
        floor_height = (
            facts.floor_height_ft
            if facts.floor_height_ft is not None and facts.floor_height_ft > 0
            else 12.0
        )
        rows.append(
            {
                "polygon": polygon,
                "elevation": floors * floor_height * FT_TO_M,
                "color": [
                    round(48 + 207 * strength),
                    round(146 - 26 * strength),
                    round(208 - 154 * strength),
                    210,
                ],
                "tooltip_html": prospect_tooltip_html(prospect),
                "address": facts.address,
                "prospect_index": index,
            }
        )
    return rows
