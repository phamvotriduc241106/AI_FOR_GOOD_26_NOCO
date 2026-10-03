"""Deterministic insulation calculations for the NOCO Address-to-Quote flow."""

from __future__ import annotations

import math

from pydantic import PrivateAttr

from .contract import ASSUMPTION_SOURCES, Assumptions, BuildingFacts, CalcInputs, CalcResult

BTU_PER_KWH = 3412.0
BTU_PER_THERM = 100_000.0
BTU_PER_MMBTU = 1_000_000.0
DEFAULT_PERIMETER_FT = 400.0
DEFAULT_FLOORS = 1
BUFFALO_HDD = 6750.0
HEATING_REALIZATION = 0.9
COOLING_REALIZATION = 0.75
# (operating load factor, floor height ft, window/door fraction), NOCO v5 Assumptions.
OPERATING_PROFILES = {
    "residential": (1.0, 10.0, 0.25),
    "office": (0.75, 12.0, 0.35),
    "retail": (0.85, 14.0, 0.30),
    "warehouse": (0.65, 20.0, 0.08),
    "intermittent": (0.5, 12.0, 0.20),
    "custom": (1.0, 12.0, 0.20),
}


class _SourcedCalcInputs(CalcInputs):
    """Carry fallback provenance without adding fields to the frozen input contract."""

    _noco_source_flags: tuple[str, ...] = PrivateAttr(default=())
    _noco_source_assumptions: tuple[str, ...] = PrivateAttr(default=())


def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _validate_inputs(i: CalcInputs) -> None:
    numeric: dict[str, float] = {
        "perimeter_ft": i.perimeter_ft,
        "floors": float(i.floors),
        "floor_height_ft": i.floor_height_ft,
        "exposed_wall_pct": i.exposed_wall_pct,
        "window_door_pct": i.window_door_pct,
        "existing_r": i.existing_r,
        "proposed_r": i.proposed_r,
        "hdd": i.hdd,
        "cdd": i.cdd,
        "operating_load_factor": i.operating_load_factor,
        "heating_efficiency": i.heating_efficiency,
        "cooling_cop": i.cooling_cop,
        "electricity_per_kwh": i.prices.electricity_per_kwh,
        "gas_per_therm": i.prices.gas_per_therm,
        "incentive_per_sqft": i.incentive_per_sqft,
    }
    if i.cost_per_sqft is not None:
        numeric["cost_per_sqft"] = i.cost_per_sqft
    for field in ("heating_realization_factor", "cooling_realization_factor"):
        factor = getattr(i, field)
        if factor is not None:
            numeric[field] = factor
            if not 0 <= factor <= 1:
                raise ValueError(f"{field} must be between 0 and 1")
    for name, value in numeric.items():
        _require_finite(name, value)

    if i.perimeter_ft < 0 or i.floors < 1 or i.floor_height_ft < 0:
        raise ValueError("perimeter, floors, and floor height must be non-negative")
    if not 0 <= i.exposed_wall_pct <= 1 or not 0 <= i.window_door_pct <= 1:
        raise ValueError("wall exposure and window/door percentages must be between 0 and 1")
    if i.existing_r <= 0 or i.proposed_r <= i.existing_r:
        raise ValueError("proposed_r must be greater than a positive existing_r")
    if i.hdd < 0 or i.cdd < 0 or i.operating_load_factor < 0:
        raise ValueError("degree days and operating load factor must be non-negative")
    if i.heating_efficiency <= 0 or i.cooling_cop <= 0:
        raise ValueError("heating efficiency and cooling COP must be positive")
    if any(
        value < 0
        for value in (
            i.prices.electricity_per_kwh,
            i.prices.gas_per_therm,
            i.incentive_per_sqft,
        )
    ) or (i.cost_per_sqft is not None and i.cost_per_sqft < 0):
        raise ValueError("prices, incentive, and project cost must be non-negative")


def _incentive_rate_and_cap(i: CalcInputs) -> tuple[float, float | None]:
    """NOCO v5 National Grid Commercial Weatherization tiers, including gas exclusions."""
    if not i.use_incentive_schedule:
        return i.incentive_per_sqft, None
    delta_r = i.proposed_r - i.existing_r
    cap = 150_000.0 if i.heating_fuel == "electric" else 250_000.0
    if delta_r < 4 or (i.heating_fuel == "natural_gas" and delta_r > 60):
        return 0.0, cap
    if i.heating_fuel == "electric":
        rate = 2.0 if delta_r < 11 else 3.0 if delta_r < 21 else 4.0
    else:
        rate = (
            0.15
            if delta_r < 11
            else 1.5
            if delta_r < 21
            else 1.75
            if delta_r < 31
            else 1.9
            if delta_r < 41
            else 2.0
        )
    return rate + (1.0 if i.is_dac else 0.0), cap


def estimate_insulation(i: CalcInputs) -> CalcResult:
    """Calculate NOCO v5 savings; legacy effective-HDD inputs retain the Golden result."""
    _validate_inputs(i)

    wall_area = (
        i.perimeter_ft
        * i.floor_height_ft
        * i.floors
        * i.exposed_wall_pct
        * (1.0 - i.window_door_pct)
    )
    delta_u = (1.0 / i.existing_r) - (1.0 / i.proposed_r)
    heating_factor = i.heating_realization_factor
    heating_load = (
        delta_u
        * wall_area
        * i.hdd
        * 24.0
        * i.operating_load_factor
        * (heating_factor if heating_factor is not None else 1.0)
    )
    cooling_factor = (
        i.cooling_realization_factor
        if i.cooling_realization_factor is not None
        else COOLING_REALIZATION
    )
    cooling_load = delta_u * wall_area * i.cdd * 24.0 * i.operating_load_factor * cooling_factor
    cooling_kwh = cooling_load / BTU_PER_KWH / i.cooling_cop

    if i.heating_fuel == "electric":
        heating_kwh = heating_load / BTU_PER_KWH / i.heating_efficiency
        heating_therms = 0.0
        heating_cost_savings = heating_kwh * i.prices.electricity_per_kwh
    elif i.heating_fuel == "natural_gas":
        heating_kwh = 0.0
        heating_therms = heating_load / BTU_PER_THERM / i.heating_efficiency
        heating_cost_savings = heating_therms * i.prices.gas_per_therm
    else:
        raise ValueError(f"unsupported heating fuel: {i.heating_fuel}")

    total_kwh = heating_kwh + cooling_kwh
    site_mmbtu = (total_kwh * BTU_PER_KWH + heating_therms * BTU_PER_THERM) / BTU_PER_MMBTU
    annual_cost_savings = heating_cost_savings + cooling_kwh * i.prices.electricity_per_kwh
    incentive_rate, incentive_cap = _incentive_rate_and_cap(i)
    uncapped_incentive = wall_area * incentive_rate
    incentive = (
        min(uncapped_incentive, incentive_cap) if incentive_cap is not None else uncapped_incentive
    )
    project_cost = None if i.cost_per_sqft is None else wall_area * i.cost_per_sqft
    net_investment = None if project_cost is None else project_cost - incentive

    flags = list(getattr(i, "_noco_source_flags", ()))
    if i.use_incentive_schedule and i.is_dac is None:
        flags.append("DAC status is unknown; no DAC bonus assumed.")
    if incentive_cap is not None and uncapped_incentive > incentive_cap:
        flags.append(f"Incentive capped at ${incentive_cap:,.0f} [noco_sheet].")
    if project_cost is None:
        flags.append("Project cost is unknown; payback is unavailable.")
    if annual_cost_savings <= 0:
        flags.append("Annual cost savings are zero; payback is unavailable.")

    simple_payback = None
    if net_investment is not None and annual_cost_savings > 0:
        simple_payback = net_investment / annual_cost_savings

    defaults = Assumptions()

    def label(field: str, value: float) -> str:
        if heating_factor is not None and (
            (field == "hdd" and value == BUFFALO_HDD) or (field == "cdd" and value == 650.0)
        ):
            return "noco_sheet"
        if i.operating_profile in OPERATING_PROFILES:
            profile_values = OPERATING_PROFILES[i.operating_profile]
            if (field == "operating_load_factor" and value == profile_values[0]) or (
                field == "window_door_pct" and value == profile_values[2]
            ):
                return "noco_sheet"
        return ASSUMPTION_SOURCES[field] if value == getattr(defaults, field) else "user"

    incentive_source = (
        "noco_sheet; National Grid fuel/Delta-R/DAC schedule"
        if i.use_incentive_schedule
        else "user override"
    )
    assumptions = [
        f"HDD={i.hdd:g} [{label('hdd', i.hdd)}]",
        f"CDD={i.cdd:g} [{label('cdd', i.cdd)}]",
        f"Operating load factor={i.operating_load_factor:g} "
        f"[{label('operating_load_factor', i.operating_load_factor)}]",
        (
            f"Heating realization factor={heating_factor:g} "
            f"[{'noco_sheet' if heating_factor == HEATING_REALIZATION else 'user'}]"
            if heating_factor is not None
            else "Heating realization factor=1 [assumed; legacy HDD is already effective]"
        ),
        f"Cooling realization factor={cooling_factor:g} "
        f"[{'noco_sheet' if cooling_factor == COOLING_REALIZATION else 'user'}]; "
        "cooling load = operating LF × cooling realization factor",
        f"Window and door fraction={i.window_door_pct:g} "
        f"[{label('window_door_pct', i.window_door_pct)}]",
        f"Incentive=${incentive_rate:g}/sq ft [{incentive_source}]",
        f"Heating fuel={i.heating_fuel}; efficiency/COP={i.heating_efficiency:g} "
        "[assumed scenario unless confirmed by the customer]",
        *getattr(i, "_noco_source_assumptions", ()),
    ]
    if incentive_cap is not None:
        assumptions.append(f"Incentive cap=${incentive_cap:g} [noco_sheet]")
        assumptions.append(
            "DAC status=unknown; non-DAC rate [assumed]"
            if i.is_dac is None
            else f"DAC status={i.is_dac} [user; designation requires confirmation]"
        )

    return CalcResult(
        insulated_wall_area_sqft=wall_area,
        delta_u=delta_u,
        heating_load_btu=heating_load,
        cooling_load_btu=cooling_load,
        heating_kwh=heating_kwh,
        heating_therms=heating_therms,
        cooling_kwh=cooling_kwh,
        total_kwh=total_kwh,
        site_mmbtu=site_mmbtu,
        annual_cost_savings=annual_cost_savings,
        incentive=incentive,
        project_cost=project_cost,
        net_investment=net_investment,
        simple_payback_years=simple_payback,
        ten_year_energy_value=annual_cost_savings * 10.0,
        flags=flags,
        assumptions=assumptions,
    )


def _operating_profile(use_class: str | None) -> str:
    """Conservative mapping of public building use to NOCO's operating profiles."""
    use = (use_class or "").upper()
    # Auto body / tire shops are service bays, i.e. Warehouse / Light Industrial, not retail
    # (checked before the retail words, which include "SHOP").
    # "TIRE SHOP", not "TIRE": "RETIREMENT" must not match.
    light_industrial = (
        "WAREHOUSE",
        "STORAGE",
        "INDUSTRIAL",
        "MANUFACTUR",
        "AUTO BODY",
        "TIRE SHOP",
    )
    if any(word in use for word in light_industrial):
        return "warehouse"
    if any(
        word in use for word in ("APARTMENT", "RESIDENTIAL", "HOTEL", "MOTEL", "HOSPITAL", "LODG")
    ):
        return "residential"
    if any(
        word in use
        for word in (
            "RETAIL",
            "RESTAURANT",
            "STORE",
            "SHOP",
            "DINER",
            "FAST FOOD",
            "BAR",
            "AUTO DEALER",
        )
    ):
        return "retail"
    if any(word in use for word in ("SEASONAL", "INTERMITTENT")):
        return "intermittent"
    return "office"


def inputs_from_facts(f: BuildingFacts, a: Assumptions) -> CalcInputs:
    """Build calculator inputs, using explicit assumptions for unavailable GIS facts."""
    flags: list[str] = []
    source_assumptions: list[str] = []
    profile = (
        _operating_profile(f.use_class) if a.operating_profile == "auto" else a.operating_profile
    )
    profile_values = OPERATING_PROFILES.get(
        profile, (a.operating_load_factor, a.floor_height_ft, a.window_door_pct)
    )
    load_factor, profile_height, window_pct = profile_values
    if profile is not None:
        profile_source = (
            "assumed use-class mapping" if a.operating_profile == "auto" else "user selection"
        )
        source_assumptions.append(
            f"Operating profile={profile} [{profile_source}; NOCO v5 values noco_sheet]"
        )
    if "operating_load_factor" in a.model_fields_set:
        load_factor = a.operating_load_factor
    elif profile is not None:
        source_assumptions.append(
            f"Profile operating LF={load_factor:g} [noco_sheet; assumed profile]"
        )
    if "window_door_pct" in a.model_fields_set:
        window_pct = a.window_door_pct
    elif profile is not None:
        source_assumptions.append(
            f"Profile window/door fraction={window_pct:g} [noco_sheet; assumed profile]"
        )

    perimeter = f.perimeter_ft
    if perimeter is None or perimeter <= 0:
        perimeter = DEFAULT_PERIMETER_FT
        area = f.footprint_sqft
        aspect = a.perimeter_aspect_ratio if a.perimeter_aspect_ratio is not None else 1.5
        shape = a.perimeter_shape_factor if a.perimeter_shape_factor is not None else 1.0
        if not math.isfinite(aspect) or aspect <= 0 or not math.isfinite(shape) or shape <= 0:
            raise ValueError("perimeter aspect ratio and shape factor must be finite and positive")
        if area is not None and math.isfinite(area) and area > 0:
            perimeter = 2 * (math.sqrt(area * aspect) + math.sqrt(area / aspect)) * shape
            source_assumptions.append(
                f"Perimeter={perimeter:g} ft [assumed; NOCO v5 footprint/shape formula]; "
                f"aspect ratio={aspect:g}, shape factor={shape:g} [assumed]"
            )
            flags.append(
                "Perimeter is unavailable; using assumed shape with the sourced footprint."
            )
        else:
            flags.append("Perimeter is unavailable; using an assumed 400 ft perimeter.")
            source_assumptions.append("Perimeter=400 ft [assumed; footprint unavailable]")
    elif (source := f.sources.get("perimeter_ft")) and source.source == "assumed":
        flags.append("Perimeter is assumed in building facts.")
        source_assumptions.append(f"Perimeter={perimeter:g} ft [assumed]")

    floors = f.floors
    if floors is None or floors < 1:
        floors = DEFAULT_FLOORS
        flags.append("Floor count is unavailable; using 1 assumed floor.")
        source_assumptions.append("Floors=1 [assumed]")
    elif (source := f.sources.get("floors")) and source.source == "assumed":
        flags.append("Floor count is assumed in building facts.")
        source_assumptions.append(f"Floors={floors} [assumed]")

    floor_height = f.floor_height_ft
    height_source = f.sources.get("floor_height_ft")
    if (
        floor_height is None
        or floor_height <= 0
        or (height_source and height_source.source == "assumed")
    ):
        floor_height = (
            a.floor_height_ft if "floor_height_ft" in a.model_fields_set else profile_height
        )
        flags.append("Floor height is unavailable; using the configured assumption.")
        default_source = "user" if "floor_height_ft" in a.model_fields_set else "noco_sheet"
        source_assumptions.append(
            f"Floor height={floor_height:g} ft [assumed; {default_source} default]"
        )
    heating_factor = a.heating_realization_factor
    hdd = a.hdd
    if "hdd" not in a.model_fields_set and heating_factor is not None:
        # Preserve the frozen effective-HDD default while the live GIS flow uses raw sheet HDD.
        hdd = BUFFALO_HDD
    if "heating_fuel" not in a.model_fields_set:
        flags.append(
            "Heating system is assumed electric resistance (COP 1) [assumed]; "
            "confirm with the customer."
            if a.heating_fuel == "electric" and a.heating_efficiency == 1.0
            else f"Heating fuel={a.heating_fuel} is assumed; confirm with the customer [assumed]."
        )
    inputs = _SourcedCalcInputs(
        perimeter_ft=perimeter,
        floors=floors,
        floor_height_ft=floor_height,
        exposed_wall_pct=a.exposed_wall_pct,
        window_door_pct=window_pct,
        existing_r=a.existing_r,
        proposed_r=a.proposed_r,
        hdd=hdd,
        cdd=a.cdd,
        operating_load_factor=load_factor,
        heating_fuel=a.heating_fuel,
        heating_efficiency=a.heating_efficiency,
        cooling_cop=a.cooling_cop,
        prices=a.prices,
        incentive_per_sqft=a.incentive_per_sqft,
        cost_per_sqft=a.cost_per_sqft,
        heating_realization_factor=heating_factor,
        cooling_realization_factor=a.cooling_realization_factor,
        is_dac=a.is_dac,
        use_incentive_schedule=(
            a.use_incentive_schedule and "incentive_per_sqft" not in a.model_fields_set
        ),
        operating_profile=profile,
    )
    inputs._noco_source_flags = tuple(flags)
    inputs._noco_source_assumptions = tuple(source_assumptions)
    return inputs
