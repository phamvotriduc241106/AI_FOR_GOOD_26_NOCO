"""GIS connector tests. NO network: recorded responses in tests/fixtures/noco/ or MockTransport."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from features.noco_scout import geo
from features.noco_scout.fixtures import SAMPLE_BUILDINGS

FIXTURES = Path(__file__).parent / "fixtures" / "noco"
ADDRESS = "110 Franklin Street, Buffalo NY"


def load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Every test: empty cache in tmp, no demo file, no env offline flag, network blocked."""
    monkeypatch.setattr(geo, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(geo, "DEMO_BUILDINGS_PATH", tmp_path / "demo_buildings.json")
    monkeypatch.delenv("NOCO_OFFLINE", raising=False)

    def no_network(request):
        raise AssertionError(f"test tried to call the network: {request.url}")

    monkeypatch.setattr(geo, "_transport", httpx.MockTransport(no_network))
    monkeypatch.setattr(geo.time, "sleep", lambda _s: None)


def recorded_router(overrides: dict[str, object] | None = None):
    """Fake _http_get_json that answers from the recorded 110 Franklin St responses."""
    overrides = overrides or {}
    calls: list[tuple[str, dict]] = []

    def fake(url, params, **_kwargs):
        calls.append((url, params))
        if url == geo.ASSESSMENT_URL:
            name = "by_address" if "house_number" in params["$where"] else "nearby"
        else:
            name = {geo.CENSUS_URL: "census", geo.OVERPASS_URL: "overpass"}[url]
        answer = overrides.get(
            name,
            {
                "census": "census_110_franklin.json",
                "overpass": "overpass_110_franklin.json",
                "by_address": "assessment_by_address_110_franklin.json",
                "nearby": "assessment_110_franklin.json",
            }[name],
        )
        if isinstance(answer, Exception):
            raise answer
        return load(answer) if isinstance(answer, str) else answer

    fake.calls = calls
    return fake


# --- geometry ---


@pytest.mark.parametrize("building", SAMPLE_BUILDINGS, ids=lambda b: b.address)
def test_area_and_perimeter_match_rectangles(building):
    # fixtures.py draws rectangles with a flat 364,000 ft/degree; geo.py uses the WGS84 degree
    # lengths at that latitude, so the two agree within ~0.7%.
    ring = building.footprint_geojson["coordinates"][0]
    area, perimeter = geo._ring_area_perimeter_ft(ring)
    assert area == pytest.approx(building.footprint_sqft, rel=0.01)
    assert perimeter == pytest.approx(building.perimeter_ft, rel=0.01)


def test_point_in_polygon_and_edge_distance():
    b = SAMPLE_BUILDINGS[0]
    ring = b.footprint_geojson["coordinates"][0]
    assert geo._contains(ring, b.lat, b.lon)
    assert geo._distance_to_ring_m(ring, b.lat, b.lon) == 0.0
    north = b.lat + 0.001  # ~111 m north of the centre; the rectangle is 90 ft deep
    assert not geo._contains(ring, north, b.lon)
    assert geo._distance_to_ring_m(ring, north, b.lon) == pytest.approx(111 - 13.7, abs=1.5)


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        ({"building:levels": "3"}, (3, "building:levels")),
        ({"building:levels": "2.5"}, (2, "building:levels")),
        ({"height": "20 m"}, (5, "height")),
        ({"height": "40'"}, (3, "height")),
        ({"building": "yes"}, (None, None)),
    ],
)
def test_parse_floors(tags, expected):
    assert geo._parse_floors(tags) == expected


def test_normalize_address():
    assert geo._normalize_address("110 Franklin Street, Buffalo NY") == "110 FRANKLIN ST"
    assert geo._normalize_address("110 FRANKLIN ST, BUFFALO, NY, 14202") == "110 FRANKLIN ST"


# --- lookups on recorded responses ---


def test_geocode_prefers_the_buffalo_match(monkeypatch):
    data = load("census_110_franklin.json")
    data["result"]["addressMatches"].reverse()  # Lackawanna (14218) first
    monkeypatch.setattr(geo, "_http_get_json", recorded_router({"census": data}))
    lat, lon, matched = geo.geocode(ADDRESS)
    assert matched == "110 FRANKLIN ST, BUFFALO, NY, 14202"
    assert geo.in_buffalo(lat, lon)


def test_fetch_footprint_picks_the_nearest_edge_from_the_street_point(monkeypatch):
    monkeypatch.setattr(geo, "_http_get_json", recorded_router())
    lat, lon, _ = geo.geocode(ADDRESS)
    footprint = geo.fetch_footprint(lat, lon)
    assert footprint["contains_point"] is False  # the geocoder snaps to the street
    assert footprint["geojson"]["type"] == "Polygon"
    ring = footprint["geojson"]["coordinates"][0]
    assert ring[0] == ring[-1]


def test_fetch_property_returns_only_two_keys(monkeypatch):
    monkeypatch.setattr(geo, "_http_get_json", recorded_router())
    record = geo.fetch_property(42.884996, -78.877039)
    assert set(record) == {"use_class", "story_height_ft"}
    assert record["story_height_ft"] > 0  # parking lots and parks are skipped


def test_recorded_roll_responses_hold_no_owner_or_mail_fields():
    for name in ("assessment_110_franklin.json", "assessment_by_address_110_franklin.json"):
        for row in load(name):
            assert set(row) <= set(geo._ROLL_SELECT.split(","))


def test_roll_query_never_selects_owner_columns(monkeypatch):
    router = recorded_router()
    monkeypatch.setattr(geo, "_http_get_json", router)
    geo.build_facts(ADDRESS)
    for url, params in router.calls:
        if url == geo.ASSESSMENT_URL:
            assert params["$select"] == "prop_class_description,story_height,latitude,longitude"


# --- build_facts ---


def test_build_facts_110_franklin(monkeypatch):
    monkeypatch.setattr(geo, "_http_get_json", recorded_router())
    facts = geo.build_facts(ADDRESS)
    assert facts.address == "110 FRANKLIN ST, BUFFALO, NY, 14202"
    assert facts.osm_id == 259799780
    assert facts.floors == 3
    assert facts.use_class == "OFFICE BUILDING"
    assert facts.floor_height_ft == 13.0
    assert facts.footprint_sqft == pytest.approx(5473, rel=0.01)  # spec: 5,473 sq ft
    assert facts.perimeter_ft == pytest.approx(347, rel=0.01)  # spec: 347 ft
    assert facts.sources["footprint_sqft"].confidence == 0.9
    assert facts.sources["floors"].source == "osm"
    assert facts.sources["use_class"].source == "assessor"
    assert facts.sources["join"].confidence == 0.9
    assert "259799780" in facts.sources["perimeter_ft"].note


def test_build_facts_without_address_match_falls_back_to_location(monkeypatch):
    monkeypatch.setattr(geo, "_http_get_json", recorded_router({"by_address": []}))
    facts = geo.build_facts(ADDRESS)
    assert facts.sources["footprint_sqft"].confidence == 0.6
    assert facts.sources["join"].confidence <= 0.6
    assert "by location" in facts.sources["join"].note


def test_build_facts_degrades_when_osm_and_roll_fail(monkeypatch):
    down = RuntimeError("service down")
    router = recorded_router({"overpass": down, "by_address": down, "nearby": down})
    monkeypatch.setattr(geo, "_http_get_json", router)
    facts = geo.build_facts(ADDRESS)
    assert facts.footprint_sqft is None and facts.floors is None and facts.use_class is None
    assert set(facts.sources) == {"address", "lat", "lon"}


def test_outside_buffalo_point_raises(monkeypatch):
    data = load("census_110_franklin.json")
    data["result"]["addressMatches"] = data["result"]["addressMatches"][1:]  # 14218 only
    monkeypatch.setattr(geo, "_http_get_json", recorded_router({"census": data}))
    with pytest.raises(ValueError, match="outside the City of Buffalo"):
        geo.build_facts("110 Franklin St, Buffalo NY 14218")


def test_matched_address_not_in_buffalo_raises(monkeypatch):
    data = load("census_110_franklin.json")
    match = data["result"]["addressMatches"][0]
    match["matchedAddress"] = "110 FRANKLIN ST, AMHERST, NY, 14226"
    data["result"]["addressMatches"] = [match]
    monkeypatch.setattr(geo, "_http_get_json", recorded_router({"census": data}))
    with pytest.raises(ValueError, match="outside the City of Buffalo"):
        geo.build_facts("110 Franklin St, Amherst NY")


def test_unknown_address_raises(monkeypatch):
    empty = {"result": {"addressMatches": []}}
    monkeypatch.setattr(geo, "_http_get_json", recorded_router({"census": empty}))
    with pytest.raises(ValueError, match="not found"):
        geo.build_facts("1 Nowhere Rd, Buffalo NY")


# --- offline mode and demo buildings ---


def write_demo(path: Path) -> None:
    path.write_text(json.dumps([b.model_dump() for b in SAMPLE_BUILDINGS]), encoding="utf-8")


def test_load_demo_buildings_missing_file_is_empty():
    assert geo.load_demo_buildings() == []


def test_offline_looks_up_demo_buildings_first():
    write_demo(geo.DEMO_BUILDINGS_PATH)
    assert len(geo.load_demo_buildings()) == len(SAMPLE_BUILDINGS)
    facts = geo.build_facts("101 Example Main Street, Buffalo NY", offline=True)
    assert facts == SAMPLE_BUILDINGS[0]


def test_offline_unknown_address_raises_without_network():
    write_demo(geo.DEMO_BUILDINGS_PATH)
    with pytest.raises(ValueError, match="offline demo data"):
        geo.build_facts(ADDRESS, offline=True)


def test_env_flag_turns_offline_on(monkeypatch):
    monkeypatch.setenv("NOCO_OFFLINE", "1")
    with pytest.raises(ValueError, match="offline demo data"):
        geo.build_facts(ADDRESS)


def test_offline_uses_cached_responses(monkeypatch):
    """Responses cached by an earlier online run make the offline lookup work."""
    router = recorded_router()

    def serve(request):
        url = str(request.url).split("?")[0]
        params = dict(request.url.params)
        return httpx.Response(200, json=router(url, params))

    monkeypatch.setattr(geo, "_transport", httpx.MockTransport(serve))
    online = geo.build_facts(ADDRESS)

    monkeypatch.setattr(geo, "_transport", httpx.MockTransport(lambda r: pytest.fail("network")))
    assert geo.build_facts(ADDRESS, offline=True) == online


# --- _http_get_json ---


def test_http_get_json_caches_and_sends_user_agent(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(geo, "_transport", httpx.MockTransport(handler))
    assert geo._http_get_json("https://api.example.test/x", {"a": 1}) == {"ok": True}
    assert geo._http_get_json("https://api.example.test/x", {"a": 1}) == {"ok": True}
    assert len(seen) == 1
    assert seen[0].headers["User-Agent"] == geo.USER_AGENT


def test_http_get_json_offline_miss_never_calls_network():
    with pytest.raises(geo.CacheMiss):
        geo._http_get_json("https://api.example.test/x", {}, offline=True)


def test_http_get_json_retries_429(monkeypatch):
    responses = iter([httpx.Response(429), httpx.Response(200, json=[1])])
    monkeypatch.setattr(geo, "_transport", httpx.MockTransport(lambda _r: next(responses)))
    assert geo._http_get_json("https://api.example.test/x", {}) == [1]


def test_http_get_json_client_error_raises(monkeypatch):
    monkeypatch.setattr(geo, "_transport", httpx.MockTransport(lambda _r: httpx.Response(400)))
    with pytest.raises(RuntimeError):
        geo._http_get_json("https://api.example.test/x", {})


def test_overpass_calls_are_spaced(monkeypatch):
    sleeps = []
    monkeypatch.setattr(geo.time, "sleep", sleeps.append)
    monkeypatch.setattr(geo, "_last_overpass_call", 0.0)
    ok = httpx.MockTransport(lambda _r: httpx.Response(200, json={"elements": []}))
    monkeypatch.setattr(geo, "_transport", ok)
    geo._http_get_json(geo.OVERPASS_URL, {"data": "q1"})
    geo._http_get_json(geo.OVERPASS_URL, {"data": "q2"})
    assert sleeps and 0 < sleeps[-1] <= geo._OVERPASS_MIN_INTERVAL_S
