"""Public GIS data -> BuildingFacts for one Buffalo address (task T3).

Sources: US Census geocoder (address -> point), OpenStreetMap via Overpass (footprint, levels),
City of Buffalo assessment roll on Socrata (use class, story height). Every live call goes through
`_http_get_json`, which caches to `data/public/cache/` and spaces Overpass calls >= 1 s apart.

Data rules:
- Only OSM **ways** tagged `building` are queried; relations (multipolygons) are skipped.
- The geocoder snaps addresses to the street centreline, so the footprint search is anchored on
  the assessment parcel point matched by house number + street (falling back to the geocoded
  point). The way that contains the anchor gets confidence 0.9; if none contains it, the way
  with the nearest edge is used with confidence 0.6.
- Join confidence (OSM <-> roll, `sources["join"]`): address match with the parcel point inside
  the footprint 0.9, address match only 0.7; location-only match inside the footprint 0.6,
  within 25 m 0.5, farther 0.3.
- Floors come from `building:levels` (0.9). Without it, they may be estimated from the `height`
  tag at 12 ft per floor with low confidence (0.4); otherwise they stay None.
- The assessment roll query selects ONLY class, story height and coordinates. Owner and mailing
  columns (`owner1`, `mail3`, ...) are never requested, stored or returned.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from collections.abc import Callable
from contextvars import ContextVar
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from hackkit.cache import DiskCache

from .contract import BuildingFacts, FieldSource

_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = _ROOT / "data" / "public" / "cache"
DEMO_BUILDINGS_PATH = _ROOT / "data" / "public" / "demo_buildings.json"

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
ASSESSMENT_URL = "https://data.buffalony.gov/resource/4t8s-9yih.json"
USER_AGENT = "noco-scout/0.1 (AI for Good hackathon; Buffalo insulation prospecting)"

# City of Buffalo bounding box (south, west, north, east). 14218 "Buffalo" addresses in
# Lackawanna fall south of it.
BUFFALO_BBOX = (42.826, -78.920, 42.967, -78.795)
_OVERPASS_MIN_INTERVAL_S = 1.0
_PROPERTY_RADIUS_M = 60
_FT_PER_M = 3.28084
_ASSUMED_FLOOR_HEIGHT_FT = 12.0

_offline: ContextVar[bool] = ContextVar("noco_offline", default=False)
_transport: httpx.BaseTransport | None = None  # tests inject httpx.MockTransport here
_last_overpass_call = 0.0


class CacheMiss(LookupError):
    """Offline mode is on and the request has no cached response."""


def _is_offline() -> bool:
    return _offline.get() or os.environ.get("NOCO_OFFLINE") == "1"


def _http_get_json(url: str, params: dict[str, Any], *, offline: bool = False) -> Any:
    """The ONLY function that touches the network. Disk-cached; offline => cache only."""
    global _last_overpass_call
    cache = DiskCache(CACHE_DIR)
    key = DiskCache.make_key(url, json.dumps(params, sort_keys=True))
    if (cached := cache.get(key)) is not None:
        return json.loads(cached)
    if offline or _is_offline():
        raise CacheMiss(f"No cached response for {urlparse(url).netloc} (offline mode)")

    is_overpass = urlparse(url).netloc == urlparse(OVERPASS_URL).netloc
    last_error: Exception | None = None
    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, timeout=30.0, transport=_transport
    ) as client:
        for attempt in range(3):
            if is_overpass:
                wait = _last_overpass_call + _OVERPASS_MIN_INTERVAL_S - time.monotonic()
                if wait > 0:
                    time.sleep(wait)
                _last_overpass_call = time.monotonic()
            try:
                response = client.get(url, params=params)
                if response.status_code == 429 or response.status_code >= 500:
                    last_error = RuntimeError(f"HTTP {response.status_code} from {url}")
                    time.sleep(1.0 * 2**attempt)
                    continue
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                break
            cache.set(key, json.dumps(data))
            return data
    raise RuntimeError(f"GET {url} failed: {last_error}") from last_error


# --- geometry (pure Python, local flat projection; fine at building scale) ---


def _ft_per_degree(lat: float) -> tuple[float, float]:
    phi = math.radians(lat)
    m_lat = 111_132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
    m_lon = 111_412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
    return m_lat * _FT_PER_M, m_lon * _FT_PER_M


def _ring_area_perimeter_ft(ring: list[list[float]]) -> tuple[float, float]:
    """Area (sq ft) and perimeter (ft) of a closed [lon, lat] ring."""
    lat0 = sum(p[1] for p in ring) / len(ring)
    fy, fx = _ft_per_degree(lat0)
    pts = [(p[0] * fx, p[1] * fy) for p in ring]
    area = 0.0
    perimeter = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:], strict=False):
        area += x1 * y2 - x2 * y1
        perimeter += math.hypot(x2 - x1, y2 - y1)
    return abs(area) / 2, perimeter


def _contains(ring: list[list[float]], lat: float, lon: float) -> bool:
    """Ray-casting point-in-polygon on a [lon, lat] ring."""
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:], strict=False):
        if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    fy, fx = _ft_per_degree((lat1 + lat2) / 2)
    return math.hypot((lat2 - lat1) * fy, (lon2 - lon1) * fx) / _FT_PER_M


def _distance_to_ring_m(ring: list[list[float]], lat: float, lon: float) -> float:
    """Shortest distance (m) from the point to the ring's edges; 0 if inside."""
    if _contains(ring, lat, lon):
        return 0.0
    fy, fx = _ft_per_degree(lat)
    px, py = lon * fx, lat * fy
    best = math.inf
    for (x1, y1), (x2, y2) in zip(ring, ring[1:], strict=False):
        ax, ay, bx, by = x1 * fx, y1 * fy, x2 * fx, y2 * fy
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1.0)))
        best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return best / _FT_PER_M


def in_buffalo(lat: float, lon: float) -> bool:
    south, west, north, east = BUFFALO_BBOX
    return south <= lat <= north and west <= lon <= east


# --- public data lookups ---


def geocode(address: str) -> tuple[float, float, str] | None:
    """US Census geocoder: (lat, lon, matched address), preferring a match inside Buffalo."""
    data = _http_get_json(
        CENSUS_URL, {"address": address, "benchmark": "Public_AR_Current", "format": "json"}
    )
    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        return None
    found = [(m["coordinates"]["y"], m["coordinates"]["x"], m["matchedAddress"]) for m in matches]
    for lat, lon, matched in found:
        if _is_buffalo_match(matched, lat, lon):
            return lat, lon, matched
    return found[0]


def _is_buffalo_match(matched: str, lat: float, lon: float) -> bool:
    return "BUFFALO, NY" in matched.upper() and in_buffalo(lat, lon)


def _parse_floors(tags: dict[str, str]) -> tuple[int | None, str | None]:
    levels = re.match(r"\s*(\d+(?:\.\d+)?)", tags.get("building:levels", ""))
    if levels:
        return max(1, round(float(levels.group(1)))), "building:levels"
    height = re.match(r"\s*(\d+(?:\.\d+)?)\s*(m|ft|')?", tags.get("height", ""))
    if height:
        unit = height.group(2) or "m"
        feet = float(height.group(1)) * (1 if unit in ("ft", "'") else _FT_PER_M)
        return max(1, round(feet / _ASSUMED_FLOOR_HEIGHT_FT)), "height"
    return None, None


def fetch_footprint(lat: float, lon: float, radius_m: int = 25) -> dict | None:
    """OSM building way at the point (or the nearest within `radius_m`).

    Returns osm_id, geojson, footprint_sqft, perimeter_ft, floors (or None), building_type,
    plus `contains_point` (bool) and `floors_from` ("building:levels" | "height" | None).
    """
    query = f'[out:json][timeout:25];way(around:{radius_m},{lat},{lon})["building"];out geom tags;'
    data = _http_get_json(OVERPASS_URL, {"data": query})
    best: tuple[float, dict, list[list[float]], bool] | None = None
    for element in data.get("elements", []):
        if element.get("type") != "way" or len(element.get("geometry", [])) < 3:
            continue
        ring = [[p["lon"], p["lat"]] for p in element["geometry"]]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        distance = _distance_to_ring_m(ring, lat, lon)
        if best is None or distance < best[0]:
            best = (distance, element, ring, distance == 0.0)
    if best is None:
        return None
    _, element, ring, contains = best
    tags = element.get("tags", {})
    area, perimeter = _ring_area_perimeter_ft(ring)
    floors, floors_from = _parse_floors(tags)
    return {
        "osm_id": element["id"],
        "geojson": {"type": "Polygon", "coordinates": [ring]},
        "footprint_sqft": round(area, 1),
        "perimeter_ft": round(perimeter, 1),
        "floors": floors,
        "building_type": tags.get("building:use") or tags.get("building"),
        "contains_point": contains,
        "floors_from": floors_from,
    }


# Owner and mailing columns are never selected, so they never reach this process.
_ROLL_SELECT = "prop_class_description,story_height,latitude,longitude"
_STREET_SUFFIXES = {"ST", "AVE", "SQ", "BLVD", "RD", "DR", "PL", "PKWY", "TER", "CT", "LN", "WAY"}


def _roll_rows(where: str) -> list[tuple[dict, float, float]]:
    """(record, lat, lon) per roll row; record holds ONLY use_class and story_height_ft."""
    data = _http_get_json(ASSESSMENT_URL, {"$select": _ROLL_SELECT, "$where": where, "$limit": 50})
    rows = []
    for row in data:
        try:
            plat, plon = float(row["latitude"]), float(row["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        record = {
            "use_class": row.get("prop_class_description") or None,
            "story_height_ft": float(row.get("story_height") or 0) or None,
        }
        rows.append((record, plat, plon))
    return rows


def _property_by_address(matched: str) -> tuple[dict, float, float] | None:
    """Roll record whose house number and street match the geocoded address, with its point."""
    words = _normalize_address(matched).split()
    if len(words) < 2 or not words[0].isdigit():
        return None
    street = words[1:-1] if len(words) > 2 and words[-1] in _STREET_SUFFIXES else words[1:]
    where = f"house_number='{words[0]}' AND upper(street) like '{' '.join(street)}%'"
    rows = _roll_rows(where)
    rows.sort(key=lambda r: r[0]["story_height_ft"] is None)  # parcels with a building first
    return rows[0] if rows else None


def _nearest_property(
    lat: float, lon: float, ring: list[list[float]] | None = None
) -> tuple[dict, float, bool] | None:
    """Nearest roll parcel by location: (record, distance m, parcel point inside footprint)."""
    rows = _roll_rows(f"within_circle(geocoded_column, {lat}, {lon}, {_PROPERTY_RADIUS_M})")
    best: tuple[tuple[bool, bool, float], dict, bool] | None = None
    for record, plat, plon in rows:
        inside = ring is not None and _contains(ring, plat, plon)
        # Rank: inside the footprint, then parcels with a building (skips parking lots and
        # parks), then distance.
        rank = (not inside, record["story_height_ft"] is None, _distance_m(lat, lon, plat, plon))
        if best is None or rank < best[0]:
            best = (rank, record, inside)
    if best is None:
        return None
    (_, _, distance), record, inside = best
    return record, distance, inside


def fetch_property(lat: float, lon: float) -> dict | None:
    """Buffalo assessment roll near the point: ONLY {use_class, story_height_ft}."""
    found = _nearest_property(lat, lon)
    return dict(found[0]) if found else None


# --- assembling the facts ---


def _normalize_address(address: str) -> str:
    """'110 Franklin Street, Buffalo NY' -> '110 FRANKLIN ST' (street part only)."""
    words = re.sub(r"[^A-Z0-9 ]", " ", address.upper().split(",")[0]).split()
    return " ".join(_ABBREVIATIONS.get(w, w) for w in words)


def _street_key(address: str) -> str:
    """_normalize_address without a trailing street suffix: '110 FRANKLIN ST' -> '110 FRANKLIN'."""
    words = _normalize_address(address).split()
    return " ".join(words[:-1] if len(words) > 2 and words[-1] in _STREET_SUFFIXES else words)


_ABBREVIATIONS = {
    "STREET": "ST",
    "AVENUE": "AVE",
    "SQUARE": "SQ",
    "BOULEVARD": "BLVD",
    "ROAD": "RD",
    "DRIVE": "DR",
    "PLACE": "PL",
    "PARKWAY": "PKWY",
    "TERRACE": "TER",
    "COURT": "CT",
    "LANE": "LN",
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
}


def load_demo_buildings() -> list[BuildingFacts]:
    """Pre-fetched Buffalo buildings (T7) from data/public/demo_buildings.json; [] if absent.

    File format: a JSON list of BuildingFacts objects (a {"buildings": [...]} wrapper is also read).
    """
    if not DEMO_BUILDINGS_PATH.exists():
        return []
    data = json.loads(DEMO_BUILDINGS_PATH.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("buildings", [])
    return [BuildingFacts.model_validate(item) for item in data]


def build_facts(address: str, *, offline: bool = False) -> BuildingFacts:
    """Address -> BuildingFacts with a source and confidence for every field.

    offline=True (or NOCO_OFFLINE=1): first look the address up in load_demo_buildings() by
    normalized street address, then use cached responses only; never calls the network.

    Raises ValueError (catch it in the UI and show the message) when:
    - the address is not found (or, offline, is neither a demo building nor cached), or
    - it is outside the city of Buffalo: the matched address lacks "BUFFALO, NY" OR the point
      is outside BUFFALO_BBOX.
    A missing footprint or assessment record does NOT raise: those fields stay None with a note.
    """
    offline = offline or _is_offline()
    if offline:
        demo = load_demo_buildings()
        # Exact street match first, then ignoring the suffix: the assessment roll writes
        # "110 FRANKLIN" where people type "110 Franklin St".
        for normalize in (_normalize_address, _street_key):
            key = normalize(address)
            for building in demo:
                if normalize(building.address) == key:
                    return building.model_copy(deep=True)

    token = _offline.set(offline)
    try:
        return _build_facts_live(address)
    finally:
        _offline.reset(token)


def _build_facts_live(address: str) -> BuildingFacts:
    try:
        located = geocode(address)
    except CacheMiss as exc:
        raise ValueError(f"'{address}' is not in the offline demo data.") from exc
    except RuntimeError as exc:
        raise ValueError(f"The address service is unavailable: {exc}") from exc
    if located is None:
        raise ValueError(f"Address not found: '{address}'.")
    lat, lon, matched = located
    if not _is_buffalo_match(matched, lat, lon):
        raise ValueError(f"'{matched}' is outside the City of Buffalo; only Buffalo is covered.")

    geocoder_note = "Census geocoder, interpolated along the street segment"
    sources: dict[str, FieldSource] = {
        "address": FieldSource(source="geocoder", confidence=0.95, note=f"input: {address}"),
        "lat": FieldSource(source="geocoder", confidence=0.8, note=geocoder_note),
        "lon": FieldSource(source="geocoder", confidence=0.8, note=geocoder_note),
    }
    facts: dict[str, Any] = {"address": matched, "lat": lat, "lon": lon}

    # The geocoder puts the point on the street centreline, so anchor the footprint search on the
    # assessment parcel point (matched by house number + street) when there is one.
    by_address = _quietly(_property_by_address, matched)
    anchor = (by_address[1], by_address[2]) if by_address else (lat, lon)
    anchor_name = "the assessment parcel point" if by_address else "the address point"

    footprint = _quietly(fetch_footprint, *anchor)
    ring = None
    if footprint:
        ring = footprint["geojson"]["coordinates"][0]
        match = f"contains {anchor_name}" if footprint["contains_point"] else "nearest way"
        osm = FieldSource(
            source="osm",
            confidence=0.9 if footprint["contains_point"] else 0.6,
            note=f"OSM way {footprint['osm_id']} ({match})",
        )
        facts.update(
            osm_id=footprint["osm_id"],
            footprint_geojson=footprint["geojson"],
            footprint_sqft=footprint["footprint_sqft"],
            perimeter_ft=footprint["perimeter_ft"],
        )
        sources.update(footprint_geojson=osm, footprint_sqft=osm, perimeter_ft=osm)
        if footprint["floors"] is not None:
            from_levels = footprint["floors_from"] == "building:levels"
            facts["floors"] = footprint["floors"]
            sources["floors"] = FieldSource(
                source="osm",
                confidence=0.9 if from_levels else 0.4,
                note=f"OSM {footprint['floors_from']} tag"
                + ("" if from_levels else f", estimated at {_ASSUMED_FLOOR_HEIGHT_FT:g} ft/floor"),
            )

    parcel: tuple[dict, float, str] | None = None  # (record, join confidence, join note)
    if by_address:
        inside = ring is not None and _contains(ring, by_address[1], by_address[2])
        parcel = (
            by_address[0],
            0.9 if inside else 0.7,
            "Assessment record matched by house number and street"
            + (", its parcel point inside the OSM footprint" if inside else ""),
        )
    elif nearby := _quietly(_nearest_property, lat, lon, ring):
        record, distance, inside = nearby
        where = "inside the OSM footprint" if inside else f"{distance:.0f} m from the address"
        confidence = 0.6 if inside else 0.5 if distance <= 25 else 0.3
        parcel = (record, confidence, f"Nearest assessment parcel by location, {where}")

    if parcel:
        record, join_confidence, join_note = parcel
        roll = FieldSource(source="assessor", confidence=0.7, note="Buffalo assessment roll")
        if record["use_class"]:
            facts["use_class"] = record["use_class"]
            sources["use_class"] = roll
        if record["story_height_ft"]:
            facts["floor_height_ft"] = record["story_height_ft"]
            sources["floor_height_ft"] = roll
        sources["join"] = FieldSource(source="assessor", confidence=join_confidence, note=join_note)
    elif footprint and footprint["building_type"] not in (None, "yes"):
        facts["use_class"] = str(footprint["building_type"]).upper()
        sources["use_class"] = FieldSource(
            source="osm", confidence=0.5, note="OSM building tag (no assessment record)"
        )

    return BuildingFacts(**facts, sources=sources)


def _quietly(fn: Callable[..., Any], *args: Any) -> Any:
    """Run a lookup; a failed or uncached call means 'no data', not a crash."""
    try:
        return fn(*args)
    except (CacheMiss, RuntimeError):
        return None
