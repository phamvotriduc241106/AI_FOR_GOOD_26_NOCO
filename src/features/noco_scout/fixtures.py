"""Reference data for tests and for building the UI before the real data lands (task T1).

- NOCO_EXAMPLE_INPUTS / NOCO_EXAMPLE_EXPECTED: NOCO's own Buffalo spreadsheet example, the
  "Golden" case in docs/TASKS.md (compare with a 0.1% tolerance).
- SAMPLE_BUILDINGS: five SYNTHETIC Buffalo buildings (made-up addresses and shapes inside the
  Downtown / Allentown / Elmwood box) with footprints and floors, so map and report work can
  start on fixtures. They are not real buildings; never show them as real data.
"""

from __future__ import annotations

import math

from .contract import BuildingFacts, CalcInputs, FieldSource, Prices

NOCO_EXAMPLE_INPUTS = CalcInputs(
    perimeter_ft=500.0,
    floors=1,
    floor_height_ft=12.0,
    exposed_wall_pct=1.0,
    window_door_pct=0.35,
    existing_r=11.0,
    proposed_r=49.0,
    hdd=6075.0,
    cdd=650.0,
    operating_load_factor=0.75,
    heating_fuel="electric",
    heating_efficiency=1.0,
    cooling_cop=3.0,
    prices=Prices(),
    incentive_per_sqft=4.0,
    cost_per_sqft=None,
)

# Keys are CalcResult field names. The sheet prints no project cost, so payback stays None.
# site_mmbtu: the sheet shows 30.9 (rounded); 9,047.6 kWh x 3,412 Btu/kWh = 30.87 MMBtu.
NOCO_EXAMPLE_EXPECTED: dict[str, float | None] = {
    "insulated_wall_area_sqft": 3900.0,
    "delta_u": 0.0705,
    "heating_load_btu": 30_066_178.0,
    "cooling_load_btu": 2_412_718.0,
    "heating_kwh": 8811.9,
    "heating_therms": 0.0,
    "cooling_kwh": 235.7,
    "total_kwh": 9047.6,
    "site_mmbtu": 30.87,
    "annual_cost_savings": 1447.6,
    "incentive": 15600.0,
    "ten_year_energy_value": 14476.0,
    "project_cost": None,
    "net_investment": None,
    "simple_payback_years": None,
}

_FT_PER_DEG_LAT = 364_000.0
_SYNTHETIC = "synthetic sample building"


def _rectangle(
    lat: float, lon: float, width_ft: float, depth_ft: float
) -> tuple[dict, float, float]:
    """Axis-aligned rectangle centred on (lat, lon): (GeoJSON Polygon, area sq ft, perimeter ft)."""
    dlat = depth_ft / 2 / _FT_PER_DEG_LAT
    dlon = width_ft / 2 / (_FT_PER_DEG_LAT * math.cos(math.radians(lat)))
    ring = [
        [round(lon - dlon, 7), round(lat - dlat, 7)],
        [round(lon + dlon, 7), round(lat - dlat, 7)],
        [round(lon + dlon, 7), round(lat + dlat, 7)],
        [round(lon - dlon, 7), round(lat + dlat, 7)],
        [round(lon - dlon, 7), round(lat - dlat, 7)],
    ]
    return (
        {"type": "Polygon", "coordinates": [ring]},
        width_ft * depth_ft,
        2 * (width_ft + depth_ft),
    )


def _sample(
    address: str,
    neighborhood: str,
    lat: float,
    lon: float,
    width_ft: float,
    depth_ft: float,
    floors: int,
    floor_height_ft: float,
    use_class: str,
    *,
    floors_source: FieldSource,
    join_confidence: float,
) -> BuildingFacts:
    geojson, area, perimeter = _rectangle(lat, lon, width_ft, depth_ft)
    osm = FieldSource(source="osm", confidence=0.9, note=_SYNTHETIC)
    return BuildingFacts(
        address=address,
        lat=lat,
        lon=lon,
        osm_id=None,
        neighborhood=neighborhood,
        footprint_geojson=geojson,
        footprint_sqft=area,
        perimeter_ft=perimeter,
        floors=floors,
        floor_height_ft=floor_height_ft,
        use_class=use_class,
        sources={
            "address": FieldSource(source="user", confidence=1.0, note=_SYNTHETIC),
            "lat": FieldSource(source="geocoder", confidence=0.95, note=_SYNTHETIC),
            "lon": FieldSource(source="geocoder", confidence=0.95, note=_SYNTHETIC),
            "neighborhood": FieldSource(source="assumed", confidence=0.8, note=_SYNTHETIC),
            "footprint_geojson": osm,
            "footprint_sqft": osm,
            "perimeter_ft": osm,
            "floors": floors_source,
            "floor_height_ft": FieldSource(source="assessor", confidence=0.7, note=_SYNTHETIC),
            "use_class": FieldSource(source="assessor", confidence=0.7, note=_SYNTHETIC),
            "join": FieldSource(
                source="assessor",
                confidence=join_confidence,
                note=f"{_SYNTHETIC}; OSM footprint <-> assessment roll matched by location",
            ),
        },
    )


_OSM_LEVELS = FieldSource(source="osm", confidence=0.9, note=f"building:levels; {_SYNTHETIC}")
_ASSUMED_FLOORS = FieldSource(
    source="assumed", confidence=0.4, note=f"no building:levels in OSM; {_SYNTHETIC}"
)

SAMPLE_BUILDINGS: list[BuildingFacts] = [
    _sample(
        "101 Example Main St, Buffalo, NY 14202",
        "Downtown",
        42.8875,
        -78.8740,
        120.0,
        90.0,
        6,
        12.0,
        "OFFICE BUILDING",
        floors_source=_OSM_LEVELS,
        join_confidence=0.9,
    ),
    _sample(
        "202 Example Franklin St, Buffalo, NY 14202",
        "Downtown",
        42.8890,
        -78.8770,
        80.0,
        60.0,
        3,
        11.0,
        "DOWNTOWN ROW TYPE",
        floors_source=_OSM_LEVELS,
        join_confidence=0.8,
    ),
    _sample(
        "303 Example Allen St, Buffalo, NY 14201",
        "Allentown",
        42.8990,
        -78.8760,
        50.0,
        100.0,
        2,
        12.0,
        "DETACHED ROW BUILDING",
        floors_source=_OSM_LEVELS,
        join_confidence=0.7,
    ),
    _sample(
        "404 Example Elmwood Ave, Buffalo, NY 14222",
        "Elmwood",
        42.9030,
        -78.8770,
        150.0,
        110.0,
        1,
        14.0,
        "SUPERMARKET",
        floors_source=_ASSUMED_FLOORS,
        join_confidence=0.6,
    ),
    _sample(
        "505 Example Delaware Ave, Buffalo, NY 14202",
        "Downtown",
        42.8960,
        -78.8710,
        200.0,
        50.0,
        4,
        12.0,
        "OFFICE BUILDING",
        floors_source=_OSM_LEVELS,
        join_confidence=0.85,
    ),
]
