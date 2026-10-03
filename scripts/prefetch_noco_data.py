"""Pre-fetch the offline Buffalo demo set into data/public/demo_buildings.json (task T7).

Bulk, not per address: one assessment-roll query for commercial parcels (class 4xx with a
building) in the Downtown / Allentown / Elmwood box, OSM building ways in a 5x5 tile grid
(Downtown tiles first), a local point-in-polygon join, then a neighbourhood-capped selection.
The file is rewritten after every tile, so a partial run is still usable. Every request goes
through geo._http_get_json (disk cache, >= 1 s between Overpass calls), so re-running only
fetches what is missing; --offline uses the cache alone.

Run:  python scripts/prefetch_noco_data.py [--target 300] [--geocode 30] [--offline]
      [--osm-floors-only]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

from features.noco_scout import geo
from features.noco_scout.contract import BuildingFacts, FieldSource

BOX = (42.870, -78.900, 42.905, -78.850)  # south, west, north, east (spec: Downtown-Elmwood)
DOWNTOWN = (42.886, -78.877)
GRID = 5
MIN_BUILDINGS = 40
MIN_FOOTPRINT_SQFT = 1000.0
NEIGHBORHOOD_CAP = 0.4  # no neighbourhood takes more than 40% of the set
EXCLUDED_CLASSES = {"PARKING GARAGE"}  # unheated: wall insulation saves nothing
COMMON_WALL = "COMMON WALL"
COMMON_WALL_WEIGHT = 0.5  # shared walls are not exposed: rank these lower
# Most buildings outside Downtown have no building:levels in OSM. Assuming one floor
# understates wall area (never inflates savings); these rank after buildings with known floors.
ASSUMED_FLOORS = 1
FLOOR_SOURCES = {
    "building:levels": FieldSource(source="osm", confidence=0.9, note="OSM building:levels tag"),
    "height": FieldSource(
        source="osm", confidence=0.4, note="OSM height tag, estimated at 12 ft per floor"
    ),
    "roll class": FieldSource(
        source="assessor", confidence=0.7, note="Buffalo assessment roll class: one story"
    ),
    "assumed": FieldSource(
        source="assumed",
        confidence=0.3,
        note="No OSM building:levels or height; assumed 1 floor (conservative)",
    ),
}
OUT = geo.DEMO_BUILDINGS_PATH

# Only the building's own facts and location. Owner and mailing columns are never requested.
ROLL_COLUMNS = (
    "prop_class_description",
    "story_height",
    "latitude",
    "longitude",
    "address",
    "zip_code_5_digit",
    "neighborhood",
)
assert not any("owner" in c or "mail" in c for c in ROLL_COLUMNS), "owner/mail column requested"


def fetch_parcels() -> list[dict]:
    s, w, n, e = BOX
    rows = geo._http_get_json(
        geo.ASSESSMENT_URL,
        {
            "$select": ",".join(ROLL_COLUMNS),
            "$where": (
                f"latitude between {s} and {n} AND longitude between {w} and {e} "
                "AND starts_with(property_class_code, '4') AND story_height > 0"
            ),
            "$order": "address",
            "$limit": 5000,
        },
    )
    parcels = []
    for row in rows:
        assert set(row) <= set(ROLL_COLUMNS), f"unexpected roll columns: {sorted(row)}"
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        use_class = (row.get("prop_class_description") or "").strip()
        if not use_class or use_class in EXCLUDED_CLASSES or not row.get("address"):
            continue
        parcels.append(
            {
                "lat": lat,
                "lon": lon,
                "use_class": use_class,
                "story_height_ft": float(row.get("story_height") or 0) or None,
                "address": " ".join(row["address"].upper().split()),
                "zip": (row.get("zip_code_5_digit") or "").strip(),
                "neighborhood": (row.get("neighborhood") or "").strip() or None,
            }
        )
    return parcels


def tiles() -> list[tuple[float, float, float, float]]:
    s, w, n, e = BOX
    dlat, dlon = (n - s) / GRID, (e - w) / GRID
    out = [
        (
            round(s + i * dlat, 5),
            round(w + j * dlon, 5),
            round(s + (i + 1) * dlat, 5),
            round(w + (j + 1) * dlon, 5),
        )
        for i in range(GRID)
        for j in range(GRID)
    ]
    centre = lambda t: ((t[0] + t[2]) / 2, (t[1] + t[3]) / 2)  # noqa: E731
    return sorted(out, key=lambda t: geo._distance_m(*DOWNTOWN, *centre(t)))


def fetch_tile(tile: tuple[float, float, float, float]) -> list[dict]:
    s, w, n, e = tile
    query = f'[out:json][timeout:60];way["building"]({s},{w},{n},{e});out geom tags;'
    data = geo._http_get_json(geo.OVERPASS_URL, {"data": query})
    ways = []
    for element in data.get("elements", []):
        if element.get("type") != "way" or len(element.get("geometry", [])) < 3:
            continue
        ring = [[p["lon"], p["lat"]] for p in element["geometry"]]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        lons, lats = [p[0] for p in ring], [p[1] for p in ring]
        ways.append(
            {
                "id": element["id"],
                "tags": element.get("tags", {}),
                "ring": ring,
                "bbox": (min(lats), min(lons), max(lats), max(lons)),
            }
        )
    return ways


def _osm_street_line(parcel: dict, tags: dict) -> str | None:
    """'110 FRANKLIN ST' when OSM has the same house number and street, else None."""
    number, *street = parcel["address"].split()
    osm_street = geo._normalize_address(
        f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}"
    )
    if tags.get("addr:housenumber", "").upper() != number or not street:
        return None
    return osm_street if osm_street.split()[1:2] == street[:1] else None


def _floors(tags: dict, use_class: str, assume: bool) -> tuple[int | None, str | None]:
    """Floors and where they came from: OSM tags, the roll class, or a conservative 1."""
    floors, origin = geo._parse_floors(tags)
    if floors is None and use_class.startswith("ONE STORY"):
        return 1, "roll class"
    if floors is None and assume:
        return ASSUMED_FLOORS, "assumed"
    return floors, origin


def join(parcels: list[dict], ways: dict[int, dict], assume_floors: bool = True) -> list[dict]:
    """One candidate per OSM way that contains at least one commercial parcel point."""
    cell = 0.002  # ~200 m grid index so each parcel only tests nearby ways
    index: dict[tuple[int, int], list[dict]] = {}
    for way in ways.values():
        s, w, n, e = way["bbox"]
        for i in range(int(s / cell), int(n / cell) + 1):
            for j in range(int(w / cell) - 1, int(e / cell) + 1):
                index.setdefault((i, j), []).append(way)
    inside: dict[int, list[dict]] = {}
    for parcel in parcels:
        key = (int(parcel["lat"] / cell), int(parcel["lon"] / cell))
        for way in index.get(key, []):
            s, w, n, e = way["bbox"]
            in_bbox = s <= parcel["lat"] <= n and w <= parcel["lon"] <= e
            if in_bbox and geo._contains(way["ring"], parcel["lat"], parcel["lon"]):
                inside.setdefault(way["id"], []).append(parcel)
                break
    candidates = []
    for way_id, found in inside.items():
        way = ways[way_id]
        area, perimeter = geo._ring_area_perimeter_ft(way["ring"])
        parcel = max(found, key=lambda p: p["story_height_ft"] or 0)
        floors, floors_from = _floors(way["tags"], parcel["use_class"], assume_floors)
        if floors is None or area < MIN_FOOTPRINT_SQFT:
            continue
        street_line = _osm_street_line(parcel, way["tags"])
        if len(found) > 1:
            join_conf, join_note = 0.6, f"{len(found)} assessment parcels inside this footprint"
        elif street_line:
            join_conf, join_note = (
                0.9,
                "parcel point inside the footprint; OSM house number matches",
            )
        else:
            join_conf, join_note = 0.8, "parcel point inside the OSM footprint"
        common_wall = COMMON_WALL in parcel["use_class"]
        candidates.append(
            {
                "way": way,
                "parcel": parcel,
                "area": round(area, 1),
                "perimeter": round(perimeter, 1),
                "floors": floors,
                "floors_from": floors_from,
                "street_line": street_line,
                "join": (join_conf, join_note),
                "common_wall": common_wall,
                "score": perimeter * floors * (COMMON_WALL_WEIGHT if common_wall else 1.0),
            }
        )
    return candidates


def select(candidates: list[dict], target: int) -> list[dict]:
    """Known floors before assumed ones, then highest wall-area score, with no neighbourhood
    above NEIGHBORHOOD_CAP of the target."""
    cap = max(1, math.ceil(target * NEIGHBORHOOD_CAP))
    ranked = sorted(
        candidates,
        key=lambda c: (c["floors_from"] == "assumed", -c["score"], c["way"]["id"]),
    )
    chosen, overflow, per_hood = [], [], Counter()
    for c in ranked:
        hood = c["parcel"]["neighborhood"] or "Unknown"
        if per_hood[hood] < cap:
            chosen.append(c)
            per_hood[hood] += 1
        else:
            overflow.append(c)
        if len(chosen) >= target:
            break
    # Too few neighbourhoods to fill the target: top up from the capped ones.
    chosen += overflow[: max(0, target - len(chosen))]
    return chosen


def to_facts(c: dict, geocoded: tuple[float, float, str] | None) -> BuildingFacts:
    parcel, way = c["parcel"], c["way"]
    roll = "Buffalo assessment roll"
    wall_note = (
        "; row building with common walls: part of this perimeter is shared, not exposed"
        if c["common_wall"]
        else ""
    )
    osm = FieldSource(
        source="osm",
        confidence=0.9,
        note=f"OSM way {way['id']} (contains the assessment parcel point)",
    )
    if geocoded:
        lat, lon, address = geocoded
        address_src = FieldSource(source="geocoder", confidence=0.95, note="Census geocoder")
        point_src = FieldSource(
            source="geocoder", confidence=0.8, note="Census geocoder, street segment"
        )
    else:
        lat, lon = parcel["lat"], parcel["lon"]
        line = c["street_line"] or parcel["address"]
        address = f"{line}, BUFFALO, NY, {parcel['zip']}".replace(", , ", ", ").rstrip(", ")
        note = f"{roll} property address" + (" + OSM street name" if c["street_line"] else "")
        address_src = FieldSource(source="assessor", confidence=0.8, note=note)
        point_src = FieldSource(source="assessor", confidence=0.8, note=f"{roll} parcel point")
    sources = {
        "address": address_src,
        "lat": point_src,
        "lon": point_src,
        "footprint_geojson": osm,
        "footprint_sqft": osm,
        "perimeter_ft": osm.model_copy(update={"note": osm.note + wall_note}),
        "floors": FLOOR_SOURCES[c["floors_from"]],
        "use_class": FieldSource(source="assessor", confidence=0.7, note=roll + wall_note),
        "join": FieldSource(source="assessor", confidence=c["join"][0], note=c["join"][1]),
    }
    if parcel["neighborhood"]:
        sources["neighborhood"] = FieldSource(source="assessor", confidence=0.9, note=roll)
    if parcel["story_height_ft"]:
        sources["floor_height_ft"] = FieldSource(source="assessor", confidence=0.7, note=roll)
    return BuildingFacts(
        address=address,
        lat=lat,
        lon=lon,
        osm_id=way["id"],
        neighborhood=parcel["neighborhood"],
        footprint_geojson={"type": "Polygon", "coordinates": [way["ring"]]},
        footprint_sqft=c["area"],
        perimeter_ft=c["perimeter"],
        floors=c["floors"],
        floor_height_ft=parcel["story_height_ft"],
        use_class=parcel["use_class"],
        sources=sources,
    )


def geocode_standout(c: dict) -> tuple[float, float, str] | None:
    parcel = c["parcel"]
    try:
        found = geo.geocode(f"{parcel['address']}, Buffalo, NY {parcel['zip']}")
    except (geo.CacheMiss, RuntimeError) as exc:
        print(f"  geocode skipped for {parcel['address']}: {exc}")
        return None
    if found and geo._is_buffalo_match(found[2], found[0], found[1]):
        return found
    return None


def build(candidates: list[dict], target: int, n_geocode: int) -> list[BuildingFacts]:
    chosen = select(candidates, target)
    facts = [
        to_facts(c, geocode_standout(c) if i < n_geocode else None) for i, c in enumerate(chosen)
    ]
    # One entry per address (two footprints can share a roll address).
    unique = {geo._normalize_address(f.address): f for f in reversed(facts)}
    return sorted(unique.values(), key=lambda f: f.address)


def write(buildings: list[BuildingFacts], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [b.model_dump(mode="json") for b in buildings]
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


def summary(buildings: list[BuildingFacts]) -> str:
    hoods = Counter(b.neighborhood or "Unknown" for b in buildings)
    joins = Counter(b.sources["join"].confidence for b in buildings)
    floors = Counter(b.sources["floors"].source for b in buildings)
    return (
        f"{len(buildings)} buildings | neighbourhoods {dict(hoods.most_common())} | "
        f"join {dict(sorted(joins.items()))} | floors by source {dict(floors)}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", type=int, default=300, help="max buildings (SHOULD 150-300)")
    parser.add_argument("--geocode", type=int, default=30, help="standout buildings to geocode")
    parser.add_argument(
        "--tiles", type=int, default=GRID * GRID, help="tiles to fetch, Downtown first"
    )
    parser.add_argument("--offline", action="store_true", help="cached responses only")
    parser.add_argument(
        "--osm-floors-only",
        action="store_true",
        help="skip buildings without OSM floors instead of assuming 1 floor",
    )
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if args.offline:
        geo._offline.set(True)

    parcels = fetch_parcels()
    print(f"{len(parcels)} commercial parcels with a building in the box")
    ways: dict[int, dict] = {}
    buildings: list[BuildingFacts] = []
    failed = 0
    for k, tile in enumerate(tiles()[: args.tiles], start=1):
        try:
            for way in fetch_tile(tile):
                ways[way["id"]] = way
        except (geo.CacheMiss, RuntimeError) as exc:
            failed += 1
            print(f"tile {k}/{args.tiles} {tile}: skipped ({exc}); re-run to fill it")
            continue
        candidates = join(parcels, ways, assume_floors=not args.osm_floors_only)
        buildings = build(candidates, args.target, args.geocode)
        write(buildings, args.out)
        print(f"tile {k}/{args.tiles}: {len(ways)} ways -> {summary(buildings)}")

    print(f"wrote {args.out} ({failed} tile(s) missing)")
    if len(buildings) < MIN_BUILDINGS:
        print(f"ERROR: only {len(buildings)} buildings; the demo needs >= {MIN_BUILDINGS}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
