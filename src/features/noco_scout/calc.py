"""Deterministic insulation calculations for the NOCO Address-to-Quote flow."""

from __future__ import annotations

import math

from .contract import Assumptions, BuildingFacts, CalcInputs, CalcResult

BTU_PER_KWH = 3412.0
BTU_PER_THERM = 100_000.0
BTU_PER_MMBTU = 1_000_000.0
DEFAULT_PERIMETER_FT = 400.0
DEFAULT_FLOORS = 1


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


def estimate_insulation(i: CalcInputs) -> CalcResult:
    """Calculate savings using the deterministic formula reconstructed from NOCO's sheet."""
    _validate_inputs(i)

    wall_area = (
        i.perimeter_ft
        * i.floor_height_ft
        * i.floors
        * i.exposed_wall_pct
        * (1.0 - i.window_door_pct)
    )
    delta_u = (1.0 / i.existing_r) - (1.0 / i.proposed_r)
    heating_load = delta_u * wall_area * i.hdd * 24.0 * i.operating_load_factor
    cooling_load = delta_u * wall_area * i.cdd * 24.0 * i.operating_load_factor**2
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
    incentive = wall_area * i.incentive_per_sqft
    project_cost = None if i.cost_per_sqft is None else wall_area * i.cost_per_sqft
    net_investment = None if project_cost is None else project_cost - incentive

    flags = list(getattr(i, "_noco_source_flags", ()))
    if project_cost is None:
        flags.append("Project cost is unknown; payback is unavailable.")
    if annual_cost_savings <= 0:
        flags.append("Annual cost savings are zero; payback is unavailable.")

    simple_payback = None
    if net_investment is not None and annual_cost_savings > 0:
        simple_payback = net_investment / annual_cost_savings

    assumptions = [
        f"HDD={i.hdd:g} and CDD={i.cdd:g} [noco_sheet]",
        f"Operating load factor={i.operating_load_factor:g} [noco_sheet]",
        "Cooling load applies the operating load factor squared [assumed]",
        f"Window and door fraction={i.window_door_pct:g} [noco_sheet]",
        f"Incentive=${i.incentive_per_sqft:g}/sq ft [noco_sheet]",
        *getattr(i, "_noco_source_assumptions", ()),
    ]

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


def _attach_source_context(
    inputs: CalcInputs, *, flags: list[str], assumptions: list[str]
) -> CalcInputs:
    """Carry provenance to the result without changing the frozen CalcInputs schema."""
    object.__setattr__(inputs, "_noco_source_flags", tuple(flags))
    object.__setattr__(inputs, "_noco_source_assumptions", tuple(assumptions))
    return inputs


def inputs_from_facts(f: BuildingFacts, a: Assumptions) -> CalcInputs:
    """Build calculator inputs, using explicit assumptions for unavailable GIS facts."""
    flags: list[str] = []
    source_assumptions: list[str] = []

    perimeter = f.perimeter_ft
    if perimeter is None or perimeter <= 0:
        perimeter = DEFAULT_PERIMETER_FT
        flags.append("Perimeter is unavailable; using an assumed 400 ft perimeter.")
        source_assumptions.append("Perimeter=400 ft [assumed]")

    floors = f.floors
    if floors is None or floors < 1:
        floors = DEFAULT_FLOORS
        flags.append("Floor count is unavailable; using 1 assumed floor.")
        source_assumptions.append("Floors=1 [assumed]")

    floor_height = f.floor_height_ft
    if floor_height is None or floor_height <= 0:
        floor_height = a.floor_height_ft
        flags.append("Floor height is unavailable; using the configured assumption.")
        source_assumptions.append(f"Floor height={floor_height:g} ft [assumed]")

    inputs = CalcInputs(
        perimeter_ft=perimeter,
        floors=floors,
        floor_height_ft=floor_height,
        exposed_wall_pct=a.exposed_wall_pct,
        window_door_pct=a.window_door_pct,
        existing_r=a.existing_r,
        proposed_r=a.proposed_r,
        hdd=a.hdd,
        cdd=a.cdd,
        operating_load_factor=a.operating_load_factor,
        heating_fuel=a.heating_fuel,
        heating_efficiency=a.heating_efficiency,
        cooling_cop=a.cooling_cop,
        prices=a.prices,
        incentive_per_sqft=a.incentive_per_sqft,
        cost_per_sqft=a.cost_per_sqft,
    )
    return _attach_source_context(inputs, flags=flags, assumptions=source_assumptions)
