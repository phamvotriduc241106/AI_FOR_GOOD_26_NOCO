"""Checks on the committed offline demo set data/public/demo_buildings.json (T7). No network."""

from __future__ import annotations

import httpx
import pytest

from features.noco_scout import geo
from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions

TEXT = geo.DEMO_BUILDINGS_PATH.read_text(encoding="utf-8")
BUILDINGS = geo.load_demo_buildings()
REQUIRED_SOURCES = {"address", "lat", "lon", "footprint_sqft", "perimeter_ft", "floors", "join"}


@pytest.fixture(autouse=True)
def no_network(monkeypatch, tmp_path):
    monkeypatch.setattr(geo, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(
        geo, "_transport", httpx.MockTransport(lambda r: pytest.fail(f"network: {r.url}"))
    )


def test_at_least_40_buildings_in_three_neighbourhoods():
    assert len(BUILDINGS) >= 40
    assert len({b.neighborhood for b in BUILDINGS if b.neighborhood}) >= 3


def test_no_owner_or_mailing_data():
    lowered = TEXT.lower()
    assert "owner" not in lowered
    assert "mail" not in lowered


def test_unique_addresses():
    keys = [geo._normalize_address(b.address) for b in BUILDINGS]
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("b", BUILDINGS, ids=lambda b: b.address)
def test_building_is_complete_and_in_buffalo(b):
    assert b.address.strip() and "BUFFALO, NY" in b.address
    assert geo.in_buffalo(b.lat, b.lon)
    assert b.footprint_geojson["type"] == "Polygon"
    ring = b.footprint_geojson["coordinates"][0]
    assert len(ring) >= 4 and ring[0] == ring[-1]
    assert all(geo.in_buffalo(lat, lon) for lon, lat in ring)
    assert b.footprint_sqft > 0 and b.perimeter_ft > 0
    assert b.floors and b.floors >= 1
    assert b.use_class
    assert set(b.sources) >= REQUIRED_SOURCES
    assert b.sources["footprint_sqft"].source == "osm"
    if "COMMON WALL" in b.use_class:
        assert "common walls" in b.sources["perimeter_ft"].note


@pytest.mark.parametrize("b", BUILDINGS, ids=lambda b: b.address)
def test_calculator_runs_on_every_building(b):
    result = estimate_insulation(inputs_from_facts(b, Assumptions()))
    assert result.annual_cost_savings > 0
    assert result.simple_payback_years is None  # no project cost => no invented payback


def test_offline_lookup_returns_demo_buildings():
    for b in BUILDINGS[:: max(1, len(BUILDINGS) // 10)]:
        assert geo.build_facts(b.address, offline=True) == b
