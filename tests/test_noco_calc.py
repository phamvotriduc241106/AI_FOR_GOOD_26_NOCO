from __future__ import annotations

import pytest

from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions, BuildingFacts, CalcInputs, Prices
from features.noco_scout.fixtures import (
    NOCO_EXAMPLE_EXPECTED,
    NOCO_EXAMPLE_INPUTS,
    SAMPLE_BUILDINGS,
)


def make_inputs(**overrides: object) -> CalcInputs:
    values: dict[str, object] = NOCO_EXAMPLE_INPUTS.model_dump()
    values.update(overrides)
    return CalcInputs(**values)


def test_noco_golden_example_matches_within_point_one_percent() -> None:
    result = estimate_insulation(NOCO_EXAMPLE_INPUTS)

    for field, expected_value in NOCO_EXAMPLE_EXPECTED.items():
        actual = getattr(result, field)
        if expected_value is None:
            assert actual is None, field
        else:
            assert actual == pytest.approx(expected_value, rel=0.001), field
    assert "HDD=6075 [assumed]" in result.assumptions
    assert "CDD=650 [assumed]" in result.assumptions


def test_unknown_project_cost_never_invents_payback() -> None:
    result = estimate_insulation(make_inputs(cost_per_sqft=None))

    assert result.project_cost is None
    assert result.net_investment is None
    assert result.simple_payback_years is None
    assert any("cost is unknown" in flag.lower() for flag in result.flags)


def test_known_project_cost_calculates_net_investment_and_payback() -> None:
    result = estimate_insulation(make_inputs(cost_per_sqft=8.0))

    assert result.project_cost == pytest.approx(31_200.0)
    assert result.net_investment == pytest.approx(15_600.0)
    assert result.simple_payback_years == pytest.approx(15_600.0 / result.annual_cost_savings)


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


def test_overridden_degree_days_are_labeled_user_input() -> None:
    result = estimate_insulation(make_inputs(hdd=5000.0))

    assert "HDD=5000 [user]" in result.assumptions


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


def test_assumed_source_on_present_floor_count_is_flagged() -> None:
    inputs = inputs_from_facts(SAMPLE_BUILDINGS[3], Assumptions())
    result = estimate_insulation(inputs)

    assert any("floor count is assumed" in flag.lower() for flag in result.flags)
    assert "Floors=1 [assumed]" in result.assumptions
    assert set(inputs.model_dump()) == set(CalcInputs.model_fields)
