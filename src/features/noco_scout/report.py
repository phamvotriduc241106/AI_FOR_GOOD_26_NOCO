"""Printable exports for NOCO (task T10): customer report, manager report, prospect CSV.

Self-contained HTML (inline CSS, NOCO logo embedded as base64) that the browser prints to PDF;
no extra libraries. Every number comes from the calculator result or the inputs (nothing about
the incentive rate or R-values is hard-coded), and every building fact shows its source.

The CUSTOMER report never shows NOCO's revenue, profit or margin. Those appear only in the
manager report, labelled ILLUSTRATIVE.
"""

from __future__ import annotations

import base64
import csv
import functools
import io
from datetime import date
from html import escape
from pathlib import Path

from .contract import (
    NOT_IN_PUBLIC_DATA,
    OSM_ATTRIBUTION,
    Assumptions,
    BuildingFacts,
    CalcInputs,
    CalcResult,
    Opportunity,
    Prospect,
)

LOGO_PATH = Path(__file__).resolve().parents[3] / "docs" / "pitch" / "assets" / "noco_logo.png"

SOURCE_LABELS = {
    "geocoder": "US Census geocoder",
    "osm": "OpenStreetMap",
    "assessor": "Buffalo assessment roll",
    "user": "Entered by NOCO",
    "assumed": "Assumed",
    "noco_sheet": "NOCO calculator",
}
HEATING = {"electric": "Electric", "natural_gas": "Natural gas"}
MISSING = "Not found in public data"

_CSS = """
@page { size: letter; margin: 0.5in; }
* { box-sizing: border-box; }
body { font: 13px/1.45 -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: #1d2a33;
  margin: 0 auto; max-width: 8in; padding: 16px; background: #fff; }
header { display: flex; align-items: center; justify-content: space-between; gap: 16px;
  border-bottom: 3px solid #1f7a4d; padding-bottom: 10px; }
header img { height: 56px; }
.brand { font-size: 22px; font-weight: 700; color: #1f7a4d; }
h1 { font-size: 20px; margin: 14px 0 2px; }
h2 { font-size: 14px; text-transform: uppercase; letter-spacing: .04em; color: #1f7a4d;
  margin: 18px 0 6px; }
.muted { color: #5b6b75; font-size: 12px; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 12px; }
.card { border: 1px solid #cfe3d8; border-radius: 6px; padding: 8px 10px; background: #f3faf6; }
.card b { display: block; font-size: 18px; color: #14532d; }
.card span { font-size: 11px; color: #44535c; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid #e3e8eb;
  vertical-align: top; }
th { font-size: 11px; color: #44535c; font-weight: 600; }
td.src { font-size: 11px; color: #5b6b75; }
ul { margin: 4px 0; padding-left: 18px; }
.callout { border-left: 4px solid #d97706; background: #fff7ed; padding: 6px 10px;
  margin-top: 10px; }
footer { margin-top: 16px; border-top: 1px solid #e3e8eb; padding-top: 6px; font-size: 11px;
  color: #5b6b75; }
@media print { body { padding: 0; } .card, table { break-inside: avoid; } }
"""


@functools.cache
def _logo_html() -> str:
    try:
        data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    except OSError:
        return '<div class="brand">NOCO</div>'
    return f'<img src="data:image/png;base64,{data}" alt="NOCO">'


def _money(value: float | None) -> str:
    return "—" if value is None else f"${value:,.0f}"


def _num(value: float | None, unit: str = "", digits: int = 0) -> str:
    return "—" if value is None else f"{value:,.{digits}f}{unit}"


def _card(value: str, label: str) -> str:
    return f"<div class='card'><b>{escape(value)}</b><span>{escape(label)}</span></div>"


def _source(facts: BuildingFacts, field: str) -> str:
    src = facts.sources.get(field)
    if src is None:
        return ""
    label = SOURCE_LABELS.get(src.source, src.source)
    text = f"{label} ({src.confidence:g})"
    repeats = src.note.lower() in label.lower() or label.lower().endswith(src.note.lower())
    return escape(f"{text} · {src.note}" if src.note and not repeats else text)


def _page(title: str, body: str) -> str:
    return (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(title)}</title><style>{_CSS}</style></head><body>"
        f"<header>{_logo_html()}<div class='muted'>Prepared {date.today():%B %d, %Y}</div>"
        f"</header>{body}</body></html>\n"
    )


def _building_rows(facts: BuildingFacts) -> str:
    rows = [
        ("Address", facts.address, "address"),
        ("Building type", facts.use_class, "use_class"),
        ("Neighborhood", facts.neighborhood, "neighborhood"),
        ("Floors", facts.floors, "floors"),
        (
            "Floor height",
            _num(facts.floor_height_ft, " ft", 1) if facts.floor_height_ft else None,
            "floor_height_ft",
        ),
        (
            "Footprint",
            _num(facts.footprint_sqft, " sq ft") if facts.footprint_sqft else None,
            "footprint_sqft",
        ),
        (
            "Perimeter",
            _num(facts.perimeter_ft, " ft") if facts.perimeter_ft else None,
            "perimeter_ft",
        ),
    ]
    html = "".join(
        f"<tr><th>{label}</th><td>{escape(str(value)) if value is not None else MISSING}</td>"
        f"<td class='src'>{_source(facts, key) if value is not None else ''}</td></tr>"
        for label, value, key in rows
    )
    if "join" in facts.sources:
        html += (
            "<tr><th>Map ↔ city records match</th><td></td>"
            f"<td class='src'>{_source(facts, 'join')}</td></tr>"
        )
    return html


def render_customer_report(
    facts: BuildingFacts,
    inputs: CalcInputs,
    result: CalcResult,
    opportunity: Opportunity | None = None,
) -> str:
    """One-page, printable customer report. Never shows NOCO revenue, profit or margin."""
    program = (opportunity.incentive_program if opportunity else None) or "the utility program"
    utility = opportunity.utility if opportunity else None
    supplier = opportunity.current_supplier if opportunity else NOT_IN_PUBLIC_DATA
    heating = HEATING.get(inputs.heating_fuel, inputs.heating_fuel)

    if result.simple_payback_years is not None:
        payback = (
            "<div class='cards'>"
            + _card(_money(result.net_investment), "Net investment after incentive")
            + _card(f"{result.simple_payback_years:,.1f} years", "Simple payback")
            + "</div>"
        )
    else:
        payback = (
            "<div class='callout'><b>Needs an installation quote.</b> Payback depends on the "
            "installed cost, which a NOCO site visit confirms. We do not estimate it without "
            "a real quote.</div>"
        )

    energy = f"{_num(result.total_kwh, ' kWh')} electricity"
    if result.heating_therms:
        energy += f" + {_num(result.heating_therms, ' therms')} gas"
    headline = (
        _card(_money(result.annual_cost_savings), "Energy cost saved per year")
        + _card(_num(result.site_mmbtu, " MMBtu", 1), f"{energy} saved per year")
        + _card(_money(result.incentive), f"Estimated incentive ({program})")
        + _card(_money(result.ten_year_energy_value), "Energy value over 10 years")
    )
    heating_row = f"{heating} (efficiency {inputs.heating_efficiency:g})"

    body = f"""
<h1>Wall insulation upgrade: savings estimate</h1>
<div class="muted">{escape(facts.address)}</div>
<div class="cards">{headline}</div>
{payback}

<h2>Recommended upgrade</h2>
<table>
<tr><th>Wall insulation</th><td>R-{inputs.existing_r:g} → R-{inputs.proposed_r:g}</td></tr>
<tr><th>Insulated wall area</th><td>{_num(result.insulated_wall_area_sqft, " sq ft")}</td></tr>
<tr><th>Heating system</th><td>{escape(heating_row)}</td></tr>
<tr><th>Cooling efficiency</th><td>COP {inputs.cooling_cop:g}</td></tr>
{f"<tr><th>Utility</th><td>{escape(utility)}</td></tr>" if utility else ""}
<tr><th>Current energy supplier</th><td>{escape(supplier)}</td></tr>
</table>

<h2>Your building, from public records</h2>
<table>{_building_rows(facts)}</table>

<h2>Next steps</h2>
<ul>
<li>A NOCO specialist visits to confirm walls, existing insulation and the heating system.</li>
<li>NOCO prepares an installed-cost quote, so the payback above becomes exact.</li>
<li>NOCO checks every program you may qualify for ({escape(program)}, and also NYSERDA and
National Fuel where they apply).</li>
</ul>

<h2>Assumptions and notes</h2>
<ul>{"".join(f"<li>{escape(a)}</li>" for a in result.assumptions)}
{"".join(f"<li>{escape(f)}</li>" for f in result.flags)}</ul>

<footer>This is an estimate from public data and NOCO's reference insulation calculator, not a
quote. Building data: {escape(OSM_ATTRIBUTION)} (ODbL); City of Buffalo assessment roll;
US Census geocoder.</footer>
"""
    return _page(f"Insulation savings estimate: {facts.address}", body)


def render_manager_report(prospects: list[Prospect], a: Assumptions) -> str:
    """Printable ranked prospect list for NOCO managers. Full version: T10 part 2."""
    rows = "".join(
        f"<tr><td>{p.rank}</td><td>{escape(p.facts.address)}</td>"
        f"<td>{_money(p.result.annual_cost_savings)}</td></tr>"
        for p in prospects
    )
    body = (
        "<h1>Prospect list</h1><div class='callout'>Preview: the full manager report "
        "(NOCO output columns, ILLUSTRATIVE revenue and profit) is coming in the next update."
        "</div><table><tr><th>Rank</th><th>Address</th><th>Energy cost saved per year</th></tr>"
        f"{rows}</table><footer>{escape(OSM_ATTRIBUTION)} (ODbL)</footer>"
    )
    return _page("NOCO prospect list", body)


def prospects_to_csv(prospects: list[Prospect]) -> str:
    """Prospect rows as CSV. Full column set: T10 part 2."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["rank", "address", "annual_cost_savings_usd"])
    for p in prospects:
        writer.writerow([p.rank, _cell(p.facts.address), f"{p.result.annual_cost_savings:.2f}"])
    return out.getvalue()


def _cell(text: str) -> str:
    """Neutralise spreadsheet formulas (CSV injection) in free-text cells."""
    return f"'{text}" if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text
