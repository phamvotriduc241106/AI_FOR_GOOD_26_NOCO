"""Frozen data contract for the NOCO Address-to-Quote feature (task T1).

Every other noco_scout module (calc, geo, prospect, mapdata, report, app pages) builds on these
types. Names, fields and defaults mirror the "Contract" section of docs/TASKS.md; do not change
them without the human integrator's approval.

Data rules baked in here:
- Models forbid unknown fields, so assessment-roll owner/mailing fields can never ride along.
- Every assumption constant carries a source label (`noco_sheet` or `assumed`).
- Unknown money stays `None`: no invented project cost, payback or NOCO profit.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Source = Literal["geocoder", "osm", "assessor", "user", "assumed", "noco_sheet"]
HeatingFuel = Literal["electric", "natural_gas"]

OSM_ATTRIBUTION = "© OpenStreetMap contributors"
NOT_IN_PUBLIC_DATA = "Not in public data: ask the customer"
UTILITY = "National Grid"
INCENTIVE_PROGRAM = "National Grid - Commercial Weatherization"


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FieldSource(_Model):
    """Where one building fact came from and how much we trust it."""

    source: Source
    confidence: float = Field(ge=0.0, le=1.0)
    note: str = ""


class BuildingFacts(_Model):
    """Public facts about one Buffalo building. Never holds owner or mailing data."""

    address: str
    lat: float
    lon: float
    osm_id: int | None = None
    neighborhood: str | None = None
    footprint_geojson: dict | None = Field(
        default=None, description="GeoJSON Polygon, coordinates in [lon, lat] order."
    )
    footprint_sqft: float | None = None
    perimeter_ft: float | None = None
    floors: int | None = None
    floor_height_ft: float | None = None
    use_class: str | None = Field(
        default=None, description='Assessment-roll class, e.g. "OFFICE BUILDING".'
    )
    sources: dict[str, FieldSource] = Field(
        default_factory=dict,
        description='Keyed by the field names above, plus "join" for the OSM <-> roll match.',
    )

    @field_validator("sources")
    @classmethod
    def _known_source_keys(cls, value: dict[str, FieldSource]) -> dict[str, FieldSource]:
        unknown = set(value) - FACT_SOURCE_KEYS
        if unknown:
            raise ValueError(f"Unknown source keys: {sorted(unknown)}")
        return value


FACT_SOURCE_KEYS = frozenset(BuildingFacts.model_fields) - {"sources"} | {"join"}


class Prices(_Model):
    """Energy prices from NOCO's Buffalo example sheet."""

    electricity_per_kwh: float = 0.16
    gas_per_therm: float = 1.20
    propane_per_gal: float = 2.80
    oil_per_gal: float = 3.40
    district_per_mmbtu: float = 18.0


class Assumptions(_Model):
    """Calculator defaults. Sources per field are in ASSUMPTION_SOURCES."""

    floor_height_ft: float = 12.0
    window_door_pct: float = 0.35
    exposed_wall_pct: float = 1.0
    existing_r: float = 11.0
    proposed_r: float = 49.0
    hdd: float = 6075.0
    cdd: float = 650.0
    operating_load_factor: float = 0.75
    heating_fuel: HeatingFuel = "electric"
    heating_efficiency: float = 1.0
    cooling_cop: float = 3.0
    prices: Prices = Field(default_factory=Prices)
    incentive_per_sqft: float = 4.0
    cost_per_sqft: float | None = None
    margin_pct: float | None = None
    heating_realization_factor: float | None = Field(
        default=0.9, description="NOCO v5 heating realization; None uses effective HDD directly."
    )
    cooling_realization_factor: float | None = Field(
        default=0.75,
        description="NOCO v5 cooling realization, separate from operating load factor.",
    )
    is_dac: bool | None = Field(
        default=None, description="Confirmed DAC designation; unknown gets no DAC incentive bonus."
    )
    use_incentive_schedule: bool = Field(
        default=True,
        description="Apply NOCO fuel/Delta-R/DAC tiers and caps; False uses a user rate.",
    )
    operating_profile: (
        Literal["auto", "office", "residential", "retail", "warehouse", "intermittent", "custom"]
        | None
    ) = Field(
        default="auto",
        description="NOCO profile; auto maps public use class, None keeps legacy inputs.",
    )
    perimeter_aspect_ratio: float | None = Field(
        default=1.5, description="Assumed length/width ratio when GIS perimeter is missing."
    )
    perimeter_shape_factor: float | None = Field(
        default=1.0, description="NOCO shape multiplier for perimeter fallback; rectangle is 1."
    )


# HDD 6,075 and CDD 650 are back-solved from NOCO's example, not printed legibly on the sheet,
# so they stay `assumed` until NOCO confirms them. Cost and margin have no default value at all.
ASSUMPTION_SOURCES: dict[str, Source] = {
    "floor_height_ft": "noco_sheet",
    "window_door_pct": "noco_sheet",
    "exposed_wall_pct": "noco_sheet",
    "existing_r": "noco_sheet",
    "proposed_r": "noco_sheet",
    "hdd": "assumed",
    "cdd": "assumed",
    "operating_load_factor": "noco_sheet",
    "heating_fuel": "noco_sheet",
    "heating_efficiency": "noco_sheet",
    "cooling_cop": "noco_sheet",
    "prices": "noco_sheet",
    "incentive_per_sqft": "noco_sheet",
    "cost_per_sqft": "user",
    "margin_pct": "user",
}


class CalcInputs(_Model):
    """Everything the insulation calculator needs. No range checks: calc.py flags bad values."""

    perimeter_ft: float
    floors: int
    floor_height_ft: float
    exposed_wall_pct: float
    window_door_pct: float
    existing_r: float
    proposed_r: float
    hdd: float
    cdd: float
    operating_load_factor: float
    heating_fuel: HeatingFuel
    heating_efficiency: float
    cooling_cop: float
    prices: Prices
    incentive_per_sqft: float
    cost_per_sqft: float | None = None
    heating_realization_factor: float | None = Field(
        default=None, description="None preserves legacy effective-HDD inputs; raw HDD uses 0.9."
    )
    cooling_realization_factor: float | None = Field(
        default=0.75, description="Separate NOCO cooling realization, multiplied by operating LF."
    )
    is_dac: bool | None = Field(
        default=None, description="Confirmed DAC designation; unknown receives the non-DAC rate."
    )
    use_incentive_schedule: bool = Field(
        default=True,
        description="Apply NOCO fuel/Delta-R/DAC tiers and caps; False uses a user rate.",
    )
    operating_profile: str | None = Field(
        default=None,
        description="Resolved NOCO profile for source attribution; numeric inputs win.",
    )


class CalcResult(_Model):
    """Calculator output. Payback-related fields are None when the project cost is unknown."""

    insulated_wall_area_sqft: float
    delta_u: float
    heating_load_btu: float
    cooling_load_btu: float
    heating_kwh: float
    heating_therms: float
    cooling_kwh: float
    total_kwh: float
    site_mmbtu: float
    annual_cost_savings: float
    incentive: float
    project_cost: float | None = None
    net_investment: float | None = None
    simple_payback_years: float | None = None
    ten_year_energy_value: float
    flags: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class Opportunity(_Model):
    """What a prospect could mean for NOCO. Money is ILLUSTRATIVE until NOCO gives real margins."""

    utility: str = UTILITY
    incentive_program: str | None = None
    current_supplier: str = NOT_IN_PUBLIC_DATA
    project_revenue: float | None = None
    estimated_profit: float | None = None
    margin_pct: float | None = None
    illustrative: bool = True
    notes: list[str] = Field(default_factory=list)


class Prospect(_Model):
    """One ranked building on the prospect map."""

    facts: BuildingFacts
    inputs: CalcInputs
    result: CalcResult
    opportunity: Opportunity
    score: float
    rank: int
