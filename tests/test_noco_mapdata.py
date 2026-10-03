from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions, Opportunity, Prospect
from features.noco_scout.fixtures import SAMPLE_BUILDINGS
from features.noco_scout.mapdata import prospect_tooltip_html, prospects_to_deck_rows


def _prospect(index: int = 0, rank: int = 1) -> Prospect:
    facts = SAMPLE_BUILDINGS[index]
    inputs = inputs_from_facts(facts, Assumptions())
    result = estimate_insulation(inputs)
    return Prospect(
        facts=facts,
        inputs=inputs,
        result=result,
        opportunity=Opportunity(),
        score=result.annual_cost_savings,
        rank=rank,
    )


def test_tooltip_order_and_provenance() -> None:
    tooltip = prospect_tooltip_html(_prospect())

    labels = (
        "Use:",
        "Floors:",
        "Footprint:",
        "Savings/year:",
        "Incentive:",
        "Payback:",
        "NOCO opportunity",
        "Utility:",
        "Incentive program:",
        "Sources:",
    )
    positions = [tooltip.index(label) for label in labels]
    assert positions == sorted(positions)
    assert "needs installed cost" in tooltip
    assert "ILLUSTRATIVE" in tooltip
    assert "SYNTHETIC SAMPLE" in tooltip
    assert "© OpenStreetMap contributors" in tooltip


def test_tooltip_escapes_untrusted_address_and_class() -> None:
    prospect = _prospect()
    prospect.facts.address = '<img src=x onerror="alert(1)">'
    prospect.facts.use_class = "<script>bad</script>"

    tooltip = prospect_tooltip_html(prospect)

    assert "<img" not in tooltip
    assert "<script>" not in tooltip
    assert "&lt;img" in tooltip
    assert "&lt;script&gt;" in tooltip


def test_deck_rows_use_geojson_lon_lat_and_floor_height() -> None:
    prospect = _prospect()
    rows = prospects_to_deck_rows([prospect])

    assert len(rows) == 1
    assert rows[0]["polygon"] == prospect.facts.footprint_geojson["coordinates"][0]
    assert rows[0]["elevation"] == pytest.approx(
        prospect.facts.floors * prospect.facts.floor_height_ft * 0.3048
    )
    assert len(rows[0]["color"]) == 4
    assert rows[0]["prospect_index"] == 0


def test_deck_rows_skip_missing_geometry_without_losing_selection_index() -> None:
    missing = _prospect(0)
    missing.facts.footprint_geojson = None
    present = _prospect(1, rank=2)

    rows = prospects_to_deck_rows([missing, present])

    assert len(rows) == 1
    assert rows[0]["prospect_index"] == 1


def test_offline_pages_run_lookup_estimate_and_ranking(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOCO_OFFLINE", "1")

    app = AppTest.from_file("../app/streamlit_app.py", default_timeout=30).run()
    app.switch_page("pages/1_Address_to_Quote.py").run()
    assert not app.exception
    next(button for button in app.button if button.label == "Find building").click().run()
    assert not app.exception
    next(
        button for button in app.button if button.label == "Estimate insulation upgrade"
    ).click().run()
    assert not app.exception
    assert any(metric.label.startswith("Annual savings") for metric in app.metric)

    app.switch_page("pages/2_Prospect_Map.py").run()
    assert not app.exception
    show_button = next(
        button for button in app.button if button.label == "Show potential customers"
    )
    show_button.click().run()
    assert not app.exception
    assert any("Ranked prospects" in heading.value for heading in app.subheader)
