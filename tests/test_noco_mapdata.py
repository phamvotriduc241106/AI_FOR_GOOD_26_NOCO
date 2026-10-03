from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from streamlit.testing.v1 import AppTest

from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions, BuildingFacts, Opportunity, Prospect
from features.noco_scout.fixtures import SAMPLE_BUILDINGS
from features.noco_scout.mapdata import (
    TOOLTIP_TEMPLATE,
    prospect_tooltip_html,
    prospects_to_deck_rows,
)


def _prospect(index: int = 0, rank: int = 1) -> Prospect:
    facts = SAMPLE_BUILDINGS[index].model_copy(deep=True)
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
        "Savings/year:",
        "Incentive:",
    )
    positions = [tooltip.index(label) for label in labels]
    assert positions == sorted(positions)
    assert tooltip.count("<br/>") == 5
    assert "[NOCO calc]" in tooltip
    assert "[osm]" in tooltip
    assert "Payback:" not in tooltip
    assert "NOCO opportunity" not in tooltip
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
    assert rows[0]["tooltip_0"] == prospect.facts.address
    assert "<strong>{tooltip_0}</strong>" in TOOLTIP_TEMPLATE
    assert "{tooltip_html}" not in TOOLTIP_TEMPLATE
    assert "{tooltip_5}" in TOOLTIP_TEMPLATE
    assert "tooltip_6" not in rows[0]
    assert TOOLTIP_TEMPLATE.format(**rows[0]) == rows[0]["tooltip_html"]


def test_deck_rows_skip_missing_geometry_without_losing_selection_index() -> None:
    missing = _prospect(0)
    missing.facts.footprint_geojson = None
    present = _prospect(1, rank=2)

    rows = prospects_to_deck_rows([missing, present])

    assert len(rows) == 1
    assert rows[0]["prospect_index"] == 1


def test_offline_address_search_never_calls_live_gis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "app"))

    from pages.noco_shared import find_building

    from features.noco_scout import geo

    monkeypatch.setenv("NOCO_OFFLINE", "1")
    real_build_facts = geo.build_facts

    def offline_only(address: str, *, offline: bool = False) -> BuildingFacts:
        if not offline:
            pytest.fail("offline search attempted a live lookup")
        return real_build_facts(address, offline=True)

    monkeypatch.setattr(geo, "build_facts", offline_only)
    monkeypatch.setattr(geo, "CACHE_DIR", Path(__file__).parent / "no-such-cache")
    monkeypatch.setattr(
        geo, "_transport", httpx.MockTransport(lambda r: pytest.fail(f"network: {r.url}"))
    )

    assert find_building("not in the saved set", SAMPLE_BUILDINGS) is None
    assert find_building(SAMPLE_BUILDINGS[0].address, SAMPLE_BUILDINGS) == SAMPLE_BUILDINGS[0]


def _offline_find(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """find_building in offline mode with the network and the HTTP cache blocked."""
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "app"))
    from pages.noco_shared import find_building

    from features.noco_scout import geo

    monkeypatch.setenv("NOCO_OFFLINE", "1")
    monkeypatch.setattr(geo, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(
        geo, "_transport", httpx.MockTransport(lambda r: pytest.fail(f"network: {r.url}"))
    )
    return find_building


def _at(address: str) -> BuildingFacts:
    return SAMPLE_BUILDINGS[1].model_copy(update={"address": address})


@pytest.mark.parametrize(
    "typed",
    [
        "110 Franklin St",
        "110 Franklin Street",
        "110 FRANKLIN, BUFFALO",
        "110 franklin st buffalo ny",
        "110 Franklin St., Buffalo, NY 14202",
    ],
)
def test_t14_house_number_and_street_variants_find_the_building(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, typed: str
) -> None:
    find_building = _offline_find(monkeypatch, tmp_path)
    saved = [_at("333 FRANKLIN ST, BUFFALO, NY, 14202"), _at("110 FRANKLIN, BUFFALO, NY, 14202")]
    assert find_building(typed, saved).address == "110 FRANKLIN, BUFFALO, NY, 14202"


def test_t14_33_franklin_never_returns_333(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    find_building = _offline_find(monkeypatch, tmp_path)
    from features.noco_scout import geo

    monkeypatch.setattr(geo, "DEMO_BUILDINGS_PATH", tmp_path / "no_demo.json")
    only_333 = [_at("333 FRANKLIN ST, BUFFALO, NY, 14202")]
    assert find_building("33 Franklin St", only_333) is None
    assert find_building("3 Franklin St", only_333) is None
    assert find_building("333 Franklin Street", only_333).address.startswith("333 ")


def test_t14_on_the_committed_demo_set(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The QA case on the real saved buildings: 33 and 333 Franklin are both in the set."""
    find_building = _offline_find(monkeypatch, tmp_path)
    from features.noco_scout import geo

    saved = geo.load_demo_buildings()
    addresses = {b.address for b in saved}
    if not {"33 FRANKLIN, BUFFALO, NY, 14202", "333 FRANKLIN ST, BUFFALO, NY, 14202"} <= addresses:
        pytest.skip("demo set no longer holds both Franklin buildings")
    assert find_building("33 Franklin St", saved).address == "33 FRANKLIN, BUFFALO, NY, 14202"
    assert find_building("333 Franklin St", saved).address == "333 FRANKLIN ST, BUFFALO, NY, 14202"
    assert find_building("110 Franklin St", saved).address == "110 FRANKLIN, BUFFALO, NY, 14202"
    assert find_building("34 Franklin St", saved) is None


def test_t14_offline_also_reads_the_saved_demo_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Buildings not passed in still come from geo.build_facts(offline=True)'s demo lookup."""
    find_building = _offline_find(monkeypatch, tmp_path)
    assert find_building("110 franklin st buffalo ny", []).address.startswith("110 FRANKLIN")
    assert find_building("33 Franklin St", []).address.startswith("33 FRANKLIN,")


def test_online_address_search_uses_t3_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "app"))

    from pages.noco_shared import find_building

    from features.noco_scout import geo

    monkeypatch.delenv("NOCO_OFFLINE", raising=False)
    calls: list[str] = []

    def lookup(address: str) -> BuildingFacts:
        calls.append(address)
        return SAMPLE_BUILDINGS[0]

    monkeypatch.setattr(geo, "build_facts", lookup)
    assert find_building("110 Franklin St, Buffalo, NY", []) == SAMPLE_BUILDINGS[0]
    assert calls == ["110 Franklin St, Buffalo, NY"]


def test_preview_opportunity_uses_only_illustrative_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "app"))

    from pages import noco_shared

    monkeypatch.setattr(noco_shared, "_optional_module", lambda _name: None)
    assumptions = Assumptions(cost_per_sqft=8.0, margin_pct=0.2)
    prospect = noco_shared.make_prospect(SAMPLE_BUILDINGS[0], assumptions)

    assert prospect.opportunity.illustrative is True
    assert prospect.opportunity.project_revenue == prospect.result.project_cost
    assert prospect.opportunity.estimated_profit == pytest.approx(
        prospect.result.project_cost * 0.2
    )


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
    assert not any("remain unconfirmed" in caption.value for caption in app.caption)

    app.switch_page("pages/2_Prospect_Map.py").run()
    assert not app.exception
    show_button = next(
        button for button in app.button if button.label == "Show potential customers"
    )
    show_button.click().run()
    assert not app.exception
    assert any("Ranked prospects" in heading.value for heading in app.subheader)
    tooltip = json.loads(app.get("deck_gl_json_chart")[0].proto.tooltip)
    assert tooltip["html"].count("<br/>") == 5
    assert tooltip["style"]["position"] == "fixed"
    assert tooltip["style"]["transform"] == "none"
    assert "300px" in tooltip["style"]["maxWidth"]
    assert tooltip["style"]["whiteSpace"] == "normal"
