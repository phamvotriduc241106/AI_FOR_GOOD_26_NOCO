"""T10 report tests: pure functions on fixtures and the committed demo set. No network."""

from __future__ import annotations

import csv
import io
import re
from html import escape

import pytest

from features.noco_scout import geo, report
from features.noco_scout.contract import Assumptions, Opportunity
from features.noco_scout.fixtures import SAMPLE_BUILDINGS
from features.noco_scout.prospect import rank_prospects


@pytest.fixture
def prospects():
    return rank_prospects(SAMPLE_BUILDINGS, Assumptions())


def customer(p, **opportunity_update):
    opportunity = p.opportunity.model_copy(update=opportunity_update)
    return report.render_customer_report(p.facts, p.inputs, p.result, opportunity)


def visible(html: str) -> str:
    """The page without its <style> block (CSS words like 'margin' are not content)."""
    return re.sub(r"<style>.*?</style>", "", html, flags=re.S)


def test_customer_report_is_self_contained_and_sourced(prospects):
    p = prospects[0]
    html = customer(p)
    assert html.startswith("<!DOCTYPE html>") and html.rstrip().endswith("</html>")
    assert p.facts.address in html
    assert "© OpenStreetMap contributors" in html
    assert "data:image/png;base64," in html  # NOCO logo embedded
    assert "<script" not in html and "http://" not in html.replace("https://", "")
    assert "OpenStreetMap (0.9)" in html  # every fact shows its source and confidence
    for assumption in p.result.assumptions:
        text, _ = report.split_assumption(assumption)
        assert escape(text) in html


def test_customer_report_uses_inputs_not_hard_coded_values(prospects):
    p = prospects[0]
    inputs = p.inputs.model_copy(update={"existing_r": 13.0, "proposed_r": 30.0})
    shown = ["Heating system=natural gas boiler [assumed]", "Incentive=$2.50/sq ft [user]"]
    result = p.result.model_copy(update={"incentive": 12_345.0, "assumptions": shown})
    html = visible(report.render_customer_report(p.facts, inputs, result, p.opportunity))
    assert "R-13 → R-30" in html
    assert "$12,345" in html
    # assumptions come from result.assumptions, shown with a readable Source column
    assert "Heating system = natural gas boiler" in html and "Assumption" in html
    assert "Incentive = $2.50/sq ft" in html and "User input" in html
    assert "[assumed]" not in html and "[user]" not in html
    assert "R-11" not in html and "R-49" not in html and "$4/sq ft" not in html


def test_customer_report_never_shows_noco_revenue_profit_or_margin(prospects):
    html = visible(
        customer(prospects[0], project_revenue=98_765.0, estimated_profit=34_567.0, margin_pct=0.35)
    ).lower()
    for word in ("revenue", "profit", "margin", "illustrative", "98,765", "34,567", "35%"):
        assert word not in html


def test_customer_report_without_cost_asks_for_a_quote(prospects):
    p = prospects[0]
    assert p.result.simple_payback_years is None
    html = customer(p)
    assert "Needs an installation quote" in html
    assert "Simple payback" not in html


def test_customer_report_with_cost_shows_payback(prospects):
    p = prospects[0]
    result = p.result.model_copy(
        update={"project_cost": 50_000.0, "net_investment": 40_000.0, "simple_payback_years": 7.25}
    )
    html = report.render_customer_report(p.facts, p.inputs, result, p.opportunity)
    assert "7.2 years" in html and "$40,000" in html
    assert "Needs an installation quote" not in html


def test_customer_report_escapes_html(prospects):
    p = prospects[0]
    facts = p.facts.model_copy(update={"address": '<script>alert("x")</script> 1 Main St'})
    html = report.render_customer_report(facts, p.inputs, p.result, p.opportunity)
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_customer_report_without_opportunity_and_missing_facts(prospects):
    p = prospects[0]
    facts = p.facts.model_copy(update={"floors": None, "use_class": None, "sources": {}})
    html = report.render_customer_report(facts, p.inputs, p.result)
    assert "Not found in public data" in html
    assert "Not in public data: ask the customer" in html


def test_no_owner_or_mail_text(prospects):
    html = customer(prospects[0]).lower()
    assert "owner" not in html and "mail" not in html


def test_customer_report_runs_on_every_demo_building():
    a = Assumptions()
    for p in rank_prospects(geo.load_demo_buildings(), a, top=1000):
        html = report.render_customer_report(p.facts, p.inputs, p.result, p.opportunity)
        assert p.facts.address.replace("&", "&amp;") in html


# --- manager report and CSV (part 2) ---


def with_illustrative_money(prospects):
    out = []
    for p in prospects:
        o = p.opportunity.model_copy(
            update={
                "project_revenue": 10_000.0 * p.rank,
                "estimated_profit": 3_500.0 * p.rank,
                "margin_pct": 0.35,
            }
        )
        out.append(p.model_copy(update={"opportunity": o}))
    return out


def test_manager_report_has_green_columns_and_every_prospect(prospects):
    html = report.render_manager_report(prospects, Assumptions())
    assert html.startswith("<!DOCTYPE html>") and "data:image/png;base64," in html
    for column in report.GREEN_COLUMNS:
        assert f"<th class='green'>{column}</th>" in html
    for p in prospects:
        assert p.facts.address in html
    assert "© OpenStreetMap contributors" in html
    total = sum(p.result.annual_cost_savings for p in prospects)
    assert f"${total:,.0f}" in html


def test_manager_report_labels_noco_money_illustrative(prospects):
    html = visible(report.render_manager_report(with_illustrative_money(prospects), Assumptions()))
    assert html.count("ILLUSTRATIVE") >= 3
    assert "$10,000" in html and "$3,500" in html
    plain = visible(report.render_manager_report(prospects, Assumptions()))
    assert "needs cost" in plain and "needs margin" in plain


def test_manager_report_assumptions_come_from_the_calculator(prospects):
    """T16: the table shows result.assumptions, so labels match what was computed."""
    html = visible(report.render_manager_report(prospects, Assumptions()))
    for line in prospects[0].result.assumptions:
        assert escape(report.split_assumption(line)[0]) in html
    assert "HDD = 6750" in html and "NOCO calculator (v5)" in html
    assert "Heating realization factor = 0.9" in html
    assert "[noco_sheet]" not in html and "noco_sheet" not in html
    assert "6075" not in html  # the old effective HDD shown as a raw "assumed" value
    assert f"all {len(prospects)}" in html


def test_manager_report_counts_assumptions_that_vary_by_building(prospects):
    custom = [
        p.model_copy(
            update={"result": p.result.model_copy(update={"assumptions": ["Shared [noco_sheet]"]})}
        )
        for p in prospects
    ]
    custom[0] = custom[0].model_copy(
        update={
            "result": custom[0].result.model_copy(
                update={"assumptions": ["Shared [noco_sheet]", "Only here [assumed]"]}
            )
        }
    )
    html = visible(report.render_manager_report(custom, Assumptions()))
    assert "Shared" in html and f"all {len(custom)}" in html
    assert "Only here" in html and f"1 of {len(custom)}" in html


def test_manager_report_shows_cost_margin_and_prices(prospects):
    html = visible(
        report.render_manager_report(prospects, Assumptions(cost_per_sqft=8.0, margin_pct=0.35))
    )
    assert "Installed cost = $8/sq ft" in html and "DEMO value; Illustrative" in html
    assert "NOCO margin = 35%" in html
    assert "Electricity = $0.16/kWh, gas = $1.2/therm" in html
    assert "Installed cost = not set" in visible(report.render_manager_report([], Assumptions()))


def test_manager_report_data_limits_no_longer_call_hdd_unconfirmed(prospects):
    html = visible(report.render_manager_report(prospects, Assumptions()))
    assert "until NOCO confirms" not in html
    assert "NOCO's own\ncalculator workbook (v5)" in html or "calculator workbook (v5)" in html


def test_manager_report_escapes_html(prospects):
    p = prospects[0].model_copy(deep=True)
    p.facts.address = "<b>x</b>"
    assert "<b>x</b>" not in report.render_manager_report([p], Assumptions())


def test_manager_report_works_from_the_map_page_call(prospects):
    """Same call as app/pages/2_Prospect_Map.py, on the full demo set and on an empty filter."""
    a = Assumptions()
    everything = rank_prospects(geo.load_demo_buildings(), a, top=1000)
    assert everything[-1].facts.address.replace("&", "&amp;") in report.render_manager_report(
        everything, a
    )
    assert "Prospects in this list" in report.render_manager_report([], a)


def test_csv_round_trips(prospects):
    rows = list(csv.DictReader(io.StringIO(report.prospects_to_csv(prospects))))
    assert len(rows) == len(prospects)
    assert tuple(rows[0]) == report.CSV_COLUMNS
    first, p = rows[0], prospects[0]
    assert first["address"] == p.facts.address
    assert float(first["annual_cost_savings_usd"]) == pytest.approx(
        p.result.annual_cost_savings, abs=0.01
    )
    assert first["simple_payback_years"] == ""  # None => empty, never 0
    assert first["project_revenue_usd_illustrative"] == ""
    assert first["current_supplier"] == "Not in public data: ask the customer"


def test_csv_illustrative_columns_and_header_has_no_owner():
    header = ",".join(report.CSV_COLUMNS)
    assert "owner" not in header and "mail" not in header
    money = [c for c in report.CSV_COLUMNS if "revenue" in c or "profit" in c or "margin" in c]
    assert money and all(c.endswith("_illustrative") for c in money)


def test_csv_with_money_and_empty_list(prospects):
    rows = list(
        csv.DictReader(io.StringIO(report.prospects_to_csv(with_illustrative_money(prospects))))
    )
    assert float(rows[0]["project_revenue_usd_illustrative"]) == 10_000.0
    assert report.prospects_to_csv([]).strip() == ",".join(report.CSV_COLUMNS)


def test_csv_neutralises_formulas(prospects):
    p = prospects[0].model_copy(deep=True)
    p.facts.address = '=HYPERLINK("http://evil")'
    row = next(csv.DictReader(io.StringIO(report.prospects_to_csv([p]))))
    assert row["address"].startswith("'=")


def test_opportunity_default_is_customer_safe():
    assert Opportunity().illustrative is True


@pytest.mark.parametrize("cost,margin", [(8.0, 0.35), (12.5, 0.22), (0.0, 0.0)])
def test_demo_reports_label_actual_values_and_preserve_customer_privacy(cost, margin):
    assumptions = Assumptions(cost_per_sqft=cost, margin_pct=margin)
    p = rank_prospects(SAMPLE_BUILDINGS, assumptions)[0]
    customer_html = customer(p)
    manager_html = report.render_manager_report([p], assumptions)
    for document in (customer_html, manager_html):
        assert 'class="demo"' in document
        assert "color: #EF4444" in document
        assert "print-color-adjust: exact" in document
        assert "Red values are DEMO values for illustration" in document
        assert f"installed cost ${cost:g}/sq ft" in document
        assert "They are not NOCO quotes" in document
    content = visible(customer_html).lower()
    assert "illustrative estimate" in content
    assert "needs an installation quote" not in content
    for forbidden in ("revenue", "profit", "margin", "30-40%"):
        assert forbidden not in content
    assert f"margin {margin:.0%}" in manager_html
    assert f'<b class="demo">${p.result.project_cost:,.0f}</b>' in customer_html
    assert f"<td class='n ill demo'>${p.opportunity.project_revenue:,.0f}</td>" in manager_html
    assert f"<td class='n ill demo'>${p.opportunity.estimated_profit:,.0f}</td>" in manager_html
    assert f"<td class='n demo'>{p.result.simple_payback_years:.1f} yr</td>" in manager_html
    assert "<td class='demo'>Installed cost = " in manager_html
    assert "<td class='demo'>NOCO margin = " in manager_html
    assert f"<b>${p.result.annual_cost_savings:,.0f}</b>" in customer_html
    assert f"<b>${p.result.incentive:,.0f}</b>" in customer_html


def test_unknown_cost_remains_unknown_without_demo_legend(prospects):
    assert Assumptions().cost_per_sqft is None
    assert Assumptions().margin_pct is None
    for document in (
        customer(prospects[0]),
        report.render_manager_report(prospects, Assumptions()),
    ):
        assert "Red values are DEMO" not in visible(document)
        assert 'class="demo"' not in visible(document)
    assert "Needs an installation quote" in customer(prospects[0])


def test_customer_known_cost_with_zero_savings_does_not_claim_cost_is_unknown():
    p = rank_prospects(SAMPLE_BUILDINGS, Assumptions(cost_per_sqft=8.0))[0]
    p.result.simple_payback_years = None
    p.result.annual_cost_savings = 0.0
    document = customer(p)
    assert "Unavailable" in document
    assert "Needs an installation quote" not in document
    assert "Illustrative estimate" in document


def test_manager_missing_margin_does_not_color_an_invented_profit():
    assumptions = Assumptions(cost_per_sqft=8.0)
    p = rank_prospects(SAMPLE_BUILDINGS, assumptions)[0]
    document = report.render_manager_report([p], assumptions)
    assert "<td class='n ill'>needs margin</td>" in document
    assert "margin 35%" not in document
    assert "<td class='demo'>NOCO margin = not set" not in document


@pytest.mark.parametrize(
    ("line", "text", "source"),
    [
        ("HDD=6750 [noco_sheet]", "HDD = 6750", "NOCO calculator (v5)"),
        ("Incentive cap=$150000 [noco_sheet]", "Incentive cap = $150,000", "NOCO calculator (v5)"),
        (
            "Operating profile=office [assumed use-class mapping; NOCO v5 values noco_sheet]",
            "Operating profile = office",
            "Assumed use-class mapping; Values from NOCO calculator (v5)",
        ),
        (
            "Heating system is assumed electric resistance (COP 1) [assumed]; confirm with the "
            "customer.",
            "Heating system is assumed electric resistance (COP 1); confirm with the customer.",
            "Assumption",
        ),
        (
            "DAC status is unknown; no DAC bonus assumed.",
            "DAC status is unknown; no DAC bonus assumed.",
            "",
        ),
    ],
)
def test_split_assumption_turns_brackets_into_a_readable_source(line, text, source):
    assert report.split_assumption(line) == (text, source)


def test_reports_show_no_raw_source_brackets(prospects):
    a = Assumptions(cost_per_sqft=8.0, margin_pct=0.35)
    p = prospects[0]
    for html in (
        visible(report.render_manager_report(prospects, a)),
        visible(report.render_customer_report(p.facts, p.inputs, p.result, p.opportunity)),
    ):
        assert not re.search(r"\[(noco_sheet|assumed|user)[^\]]*\]", html)
