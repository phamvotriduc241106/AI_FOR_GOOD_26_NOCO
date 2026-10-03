from __future__ import annotations

import pytest

from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions, BuildingFacts, CalcInputs, Prices


def make_inputs(**overrides: object) -> CalcInputs:
    values: dict[str, object] = {
        "perimeter_ft": 500.0,
        "floors": 1,
        "floor_height_ft": 12.0,
        "exposed_wall_pct": 1.0,
        "window_door_pct": 0.35,
        "existing_r": 11.0,
        "proposed_r": 49.0,
        "hdd": 6075.0,
        "cdd": 650.0,
        "operating_load_factor": 0.75,
        "heating_fuel": "electric",
        "heating_efficiency": 1.0,
        "cooling_cop": 3.0,
        "prices": Prices(electricity_per_kwh=0.16),
        "incentive_per_sqft": 4.0,
        "cost_per_sqft": None,
    }
    values.update(overrides)
    return CalcInputs(**values)


def test_noco_golden_example_matches_within_point_one_percent() -> None:
    result = estimate_insulation(make_inputs())

    expected = {
        "insulated_wall_area_sqft": 3900.0,
        "heating_load_btu": 30_066_178.0,
        "cooling_load_btu": 2_412_718.0,
        "heating_kwh": 8811.9,
        "cooling_kwh": 235.7,
        "total_kwh": 9047.6,
        "annual_cost_savings": 1447.6,
        "incentive": 15_600.0,
        "ten_year_energy_value": 14_476.0,
    }
    for field, expected_value in expected.items():
        assert getattr(result, field) == pytest.approx(expected_value, rel=0.001)


def test_unknown_project_cost_never_invents_payback() -> None:
    result = estimate_insulation(make_inputs(cost_per_sqft=None))

    assert result.project_cost is None
    assert result.net_investment is None
    assert result.simple_payback_years is None
    assert any("cost is unknown" in flag.lower() for flag in result.flags)


def test_zero_savings_has_no_payback() -> None:
    result = estimate_insulation(make_inputs(hdd=0.0, cdd=0.0, cost_per_sqft=8.0))

    assert result.annual_cost_savings == 0.0
    assert result.simple_payback_years is None
    assert any("savings are zero" in flag.lower() for flag in result.flags)


@pytest.mark.parametrize(
    ("existing_r", "proposed_r"),
    [(0.0, 49.0), (-1.0, 49.0), (11.0, 11.0), (20.0, 11.0)],
)
def test_invalid_r_values_are_rejected(existing_r: float, proposed_r: float) -> None:
    with pytest.raises(ValueError, match="proposed_r"):
        estimate_insulation(make_inputs(existing_r=existing_r, proposed_r=proposed_r))


def test_natural_gas_uses_therms_and_gas_price() -> None:
    result = estimate_insulation(
        make_inputs(
            heating_fuel="natural_gas",
            heating_efficiency=0.8,
            prices=Prices(electricity_per_kwh=0.16, gas_per_therm=1.20),
        )
    )

    expected_therms = result.heating_load_btu / 100_000.0 / 0.8
    assert result.heating_kwh == 0.0
    assert result.heating_therms == pytest.approx(expected_therms)
    assert result.annual_cost_savings == pytest.approx(
        expected_therms * 1.20 + result.cooling_kwh * 0.16
    )


def test_inputs_from_facts_preserves_gis_values() -> None:
    facts = BuildingFacts(
        address="65 Niagara Square, Buffalo, NY",
        lat=42.8864,
        lon=-78.8784,
        osm_id=123,
        neighborhood="Downtown",
        footprint_geojson=None,
        footprint_sqft=10_000.0,
        perimeter_ft=500.0,
        floors=3,
        floor_height_ft=14.0,
        use_class="OFFICE BUILDING",
        sources={},
    )
    inputs = inputs_from_facts(facts, Assumptions())

    assert inputs.perimeter_ft == 500.0
    assert inputs.floors == 3
    assert inputs.floor_height_ft == 14.0


def test_inputs_from_facts_flags_assumed_geometry() -> None:
    facts = BuildingFacts(
        address="Unknown Buffalo building",
        lat=42.8864,
        lon=-78.8784,
        osm_id=None,
        neighborhood=None,
        footprint_geojson=None,
        footprint_sqft=None,
        perimeter_ft=None,
        floors=None,
        floor_height_ft=None,
        use_class=None,
        sources={},
    )
    result = estimate_insulation(inputs_from_facts(facts, Assumptions()))

    assert any("perimeter is unavailable" in flag.lower() for flag in result.flags)
    assert any("floor count is unavailable" in flag.lower() for flag in result.flags)
    assert any("floor height is unavailable" in flag.lower() for flag in result.flags)
    assert any("[assumed]" in item for item in result.assumptions)
