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
from collections import Counter
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
    Prices,
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


def _page(title: str, body: str, extra_css: str = "") -> str:
    return (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(title)}</title><style>{_CSS}{extra_css}</style></head><body>"
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


_MANAGER_CSS = """
@page { size: letter landscape; margin: 0.4in; }
body { max-width: 10.2in; }
.wide th, .wide td { font-size: 11px; padding: 3px 4px; }
.wide td.n { text-align: right; white-space: nowrap; }
th.green, td.green { background: #e7f6ec; }
th.ill, td.ill { background: #fff4e5; }
"""

# NOCO's green output cells (sheet SC, E5:E11), in the sheet's order.
GREEN_COLUMNS = (
    "Heating saved",
    "Cooling kWh",
    "Total electric kWh",
    "Site MMBtu",
    "Energy $ / yr",
    "Incentive",
    "10-yr energy value",
)


def _heating_saved(r: CalcResult) -> str:
    if r.heating_therms:
        return _num(r.heating_therms, " therms")
    return _num(r.heating_kwh, " kWh")


def _manager_row(p: Prospect) -> str:
    f, r, o = p.facts, p.result, p.opportunity
    join = f.sources.get("join")
    payback = "needs cost" if r.simple_payback_years is None else f"{r.simple_payback_years:.1f} yr"
    green = (
        _heating_saved(r),
        _num(r.cooling_kwh),
        _num(r.total_kwh),
        _num(r.site_mmbtu, digits=1),
        _money(r.annual_cost_savings),
        _money(r.incentive),
        _money(r.ten_year_energy_value),
    )
    illustrative = (
        _money(o.project_revenue) if o.project_revenue is not None else "needs cost",
        _money(o.estimated_profit) if o.estimated_profit is not None else "needs margin",
    )
    return (
        f"<tr><td class='n'>{p.rank}</td><td>{escape(f.address)}</td>"
        f"<td>{escape(f.neighborhood or '—')}</td><td>{escape(f.use_class or '—')}</td>"
        f"<td class='n'>{_num(f.floors) if f.floors else '—'}</td>"
        f"<td class='n'>{f'{join.confidence:g}' if join else '—'}</td>"
        + "".join(f"<td class='n green'>{v}</td>" for v in green)
        + f"<td class='n'>{payback}</td>"
        + "".join(f"<td class='n ill'>{v}</td>" for v in illustrative)
        + "</tr>"
    )


def _assumption_rows(prospects: list[Prospect], a: Assumptions) -> str:
    """The calculator's own assumption lines (result.assumptions), so labels always match
    what was computed: lines every prospect shares first, then lines that vary by building
    with how many prospects they apply to. Then the cost, margin and price inputs."""
    total = len(prospects)
    counts = Counter(line for p in prospects for line in dict.fromkeys(p.result.assumptions))
    shared = [
        line
        for line in (prospects[0].result.assumptions if prospects else [])
        if counts[line] == total
    ]
    varying = sorted(
        (line for line in counts if counts[line] < total), key=lambda s: (-counts[s], s)
    )
    rows = [(line, f"all {total}") for line in dict.fromkeys(shared)]
    rows += [(line, f"{counts[line]} of {total}") for line in varying]

    prices_src = "noco_sheet" if a.prices == Prices() else "user"
    cost = "not set" if a.cost_per_sqft is None else f"${a.cost_per_sqft:g}/sq ft"
    margin = "not set" if a.margin_pct is None else f"{a.margin_pct:.0%}"
    rows += [
        (f"Installed cost={cost} [user; ILLUSTRATIVE]", "revenue, payback"),
        (f"NOCO margin={margin} [user; ILLUSTRATIVE]", "profit"),
        (
            f"Electricity=${a.prices.electricity_per_kwh:g}/kWh, gas=${a.prices.gas_per_therm:g}"
            f"/therm [{prices_src}]",
            "energy $ / yr",
        ),
    ]
    return "".join(
        f"<tr><td>{escape(line)}</td><td class='src'>{escape(scope)}</td></tr>"
        for line, scope in rows
    )


def render_manager_report(prospects: list[Prospect], a: Assumptions) -> str:
    """Printable ranked prospect list for NOCO managers.

    Columns: identity + join confidence, NOCO's green output cells, payback, then NOCO
    revenue and profit, which are ILLUSTRATIVE until NOCO provides installed costs.
    """
    revenue = [p.opportunity.project_revenue for p in prospects]
    profit = [p.opportunity.estimated_profit for p in prospects]
    known_revenue = [v for v in revenue if v is not None]
    known_profit = [v for v in profit if v is not None]
    cards = (
        _card(f"{len(prospects):,}", "Prospects in this list")
        + _card(_money(sum(p.result.annual_cost_savings for p in prospects)), "Energy $ saved / yr")
        + _card(_money(sum(p.result.incentive for p in prospects)), "Incentives available")
        + _card(
            _money(sum(known_profit)) if known_profit else "needs cost + margin",
            "NOCO profit (ILLUSTRATIVE)",
        )
    )
    header = (
        "<tr><th>#</th><th>Address</th><th>Neighborhood</th><th>Building type</th>"
        "<th>Floors</th><th>Match</th>"
        + "".join(f"<th class='green'>{c}</th>" for c in GREEN_COLUMNS)
        + "<th>Payback</th><th class='ill'>Project revenue ILLUSTRATIVE</th>"
        "<th class='ill'>NOCO profit ILLUSTRATIVE</th></tr>"
    )
    revenue_note = (
        f"{len(known_revenue)} of {len(prospects)} prospects have an illustrative revenue"
        if known_revenue
        else "No installed cost is set, so revenue and profit show 'needs cost'"
    )
    body = f"""
<h1>NOCO prospect list: wall insulation, Buffalo</h1>
<div class="muted">Ranked by energy cost saved per year. Green columns are NOCO's calculator
outputs; orange columns are ILLUSTRATIVE.</div>
<div class="cards">{cards}</div>
<h2>Ranked prospects</h2>
<table class="wide">{header}{"".join(_manager_row(p) for p in prospects)}</table>
<h2>Assumptions</h2>
<div class="muted">As used by the calculator for these prospects; [labels] give each source.</div>
<table><tr><th>Assumption</th><th>Applies to</th></tr>{_assumption_rows(prospects, a)}</table>
<h2>Data limits</h2>
<ul>
<li>NOCO revenue and profit are ILLUSTRATIVE: {escape(revenue_note)}. Margin guidance from
NOCO is 30 to 40%; installed cost per sq ft is not yet provided.</li>
<li>Footprints and floors come from OpenStreetMap; building type and story height from the
City of Buffalo assessment roll. "Match" is the confidence of that OSM ↔ roll join.</li>
<li>The customer's current energy supplier is not public data: ask the customer.</li>
<li>Buffalo HDD and CDD and the heating and cooling realization factors come from NOCO's own
calculator workbook (v5), labelled [noco_sheet]. Building-specific inputs (operating profile,
heating system, DAC status) are [assumed] until confirmed with the customer.</li>
</ul>
<footer>Building data: {escape(OSM_ATTRIBUTION)} (ODbL); City of Buffalo assessment roll;
US Census geocoder. Internal NOCO document.</footer>
"""
    return _page("NOCO prospect list", body, extra_css=_MANAGER_CSS)


CSV_COLUMNS = (
    "rank",
    "address",
    "neighborhood",
    "use_class",
    "floors",
    "footprint_sqft",
    "perimeter_ft",
    "join_confidence",
    "insulated_wall_area_sqft",
    "heating_kwh",
    "heating_therms",
    "cooling_kwh",
    "total_kwh",
    "site_mmbtu",
    "annual_cost_savings_usd",
    "incentive_usd",
    "ten_year_energy_value_usd",
    "project_cost_usd",
    "net_investment_usd",
    "simple_payback_years",
    "project_revenue_usd_illustrative",
    "estimated_profit_usd_illustrative",
    "margin_pct_illustrative",
    "utility",
    "incentive_program",
    "current_supplier",
    "osm_id",
    "flags",
)


def _fmt(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, str):
        return _cell(value)
    return value


def prospects_to_csv(prospects: list[Prospect]) -> str:
    """One row per prospect; empty cells for unknown values; money suffixed _usd.

    Revenue, profit and margin columns end in `_illustrative`.
    """
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for p in prospects:
        f, r, o = p.facts, p.result, p.opportunity
        join = f.sources.get("join")
        values = (
            p.rank,
            f.address,
            f.neighborhood,
            f.use_class,
            f.floors,
            f.footprint_sqft,
            f.perimeter_ft,
            join.confidence if join else None,
            r.insulated_wall_area_sqft,
            r.heating_kwh,
            r.heating_therms,
            r.cooling_kwh,
            r.total_kwh,
            r.site_mmbtu,
            r.annual_cost_savings,
            r.incentive,
            r.ten_year_energy_value,
            r.project_cost,
            r.net_investment,
            r.simple_payback_years,
            o.project_revenue,
            o.estimated_profit,
            o.margin_pct,
            o.utility,
            o.incentive_program,
            o.current_supplier,
            f.osm_id,
            "; ".join(r.flags),
        )
        writer.writerow([_fmt(v) for v in values])
    return out.getvalue()


def _cell(text: str) -> str:
    """Neutralise spreadsheet formulas (CSV injection) in free-text cells."""
    return f"'{text}" if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text
