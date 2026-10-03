"""T10 report tests: pure functions on fixtures and the committed demo set. No network."""

from __future__ import annotations

import csv
import io
import re

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
        assert assumption.replace("&", "&amp;") in html or assumption in html


def test_customer_report_uses_inputs_not_hard_coded_values(prospects):
    p = prospects[0]
    inputs = p.inputs.model_copy(update={"existing_r": 13.0, "proposed_r": 30.0})
    shown = ["Heating system=natural gas boiler [assumed]", "Incentive=$2.50/sq ft [user]"]
    result = p.result.model_copy(update={"incentive": 12_345.0, "assumptions": shown})
    html = visible(report.render_customer_report(p.facts, inputs, result, p.opportunity))
    assert "R-13 → R-30" in html
    assert "$12,345" in html
    assert all(text in html for text in shown)  # assumptions come from result.assumptions
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


# Placeholders kept so the Prospect Map page (which calls them) keeps working until part 2.


def test_manager_report_and_csv_do_not_break_the_map_page(prospects):
    html = report.render_manager_report(prospects, Assumptions())
    assert html.startswith("<!DOCTYPE html>") and prospects[0].facts.address in html
    rows = list(csv.DictReader(io.StringIO(report.prospects_to_csv(prospects))))
    assert len(rows) == len(prospects)


def test_csv_neutralises_formulas(prospects):
    p = prospects[0].model_copy(deep=True)
    p.facts.address = '=HYPERLINK("http://evil")'
    row = next(csv.DictReader(io.StringIO(report.prospects_to_csv([p]))))
    assert row["address"].startswith("'=")


def test_opportunity_default_is_customer_safe():
    assert Opportunity().illustrative is True
