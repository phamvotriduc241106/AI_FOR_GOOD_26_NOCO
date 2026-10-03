"""Safe, source-labelled building data for the Buffalo 3D map."""

from __future__ import annotations

import html
import math

from .contract import OSM_ATTRIBUTION, BuildingFacts, Prospect

FT_TO_M = 0.3048
TOOLTIP_TEMPLATE = "<strong>{tooltip_0}</strong>" + "".join(
    f"<br/>{{tooltip_{index}}}" for index in range(1, 6)
)


def _source(facts: BuildingFacts, field: str) -> str:
    source = facts.sources.get(field)
    if source is None:
        return "source not recorded"
    return html.escape(source.source)


def _money(value: float | None, missing: str) -> str:
    return f"${value:,.0f}" if value is not None else missing


def _tooltip_lines(p: Prospect) -> list[str]:
    """Escape dynamic text before it enters the fixed HTML tooltip template."""
    f = p.facts
    r = p.result
    floors = str(f.floors) if f.floors is not None else "unknown"
    sample = (
        "SYNTHETIC SAMPLE · "
        if any("synthetic" in source.note.lower() for source in f.sources.values())
        else ""
    )
    return [
        html.escape(f.address),
        f"Use: {html.escape(f.use_class or 'unknown')} [{_source(f, 'use_class')}]",
        f"Floors: {floors} [{_source(f, 'floors')}]",
        f"Savings/year: {_money(r.annual_cost_savings, 'unavailable')} [NOCO calc]",
        f"Incentive: {_money(r.incentive, 'unavailable')} [NOCO calc]",
        f"{sample}{OSM_ATTRIBUTION}",
    ]


def prospect_tooltip_html(p: Prospect) -> str:
    """Render the fixed tooltip order with escaped public data and explicit sources."""
    lines = _tooltip_lines(p)
    return f"<strong>{lines[0]}</strong><br/>" + "<br/>".join(lines[1:])


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
        tooltip_lines = _tooltip_lines(prospect)
        row = {
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
        row.update({f"tooltip_{line_index}": line for line_index, line in enumerate(tooltip_lines)})
        rows.append(row)
    return rows
