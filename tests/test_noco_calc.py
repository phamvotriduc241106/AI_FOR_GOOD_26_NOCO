from __future__ import annotations

import pytest

from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions, BuildingFacts, CalcInputs, FieldSource, Prices
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


def test_confirmed_raw_hdd_and_realization_still_match_golden() -> None:
    facts = SAMPLE_BUILDINGS[0].model_copy(
        update={"perimeter_ft": 500.0, "floors": 1, "floor_height_ft": 12.0}
    )
    inputs = inputs_from_facts(facts, Assumptions())
    result = estimate_insulation(inputs)

    assert inputs.hdd == 6750.0
    assert inputs.heating_realization_factor == 0.9
    for field, expected in NOCO_EXAMPLE_EXPECTED.items():
        assert getattr(result, field) == (
            None if expected is None else pytest.approx(expected, rel=0.001)
        )
    assert "HDD=6750 [noco_sheet]" in result.assumptions
    assert "CDD=650 [noco_sheet]" in result.assumptions
    assert any("Heating system is assumed electric resistance" in flag for flag in result.flags)


@pytest.mark.parametrize(
    ("fuel", "delta_r", "rate"),
    [
        ("electric", 3.99, 0.0),
        ("electric", 4.0, 2.0),
        ("electric", 10.0, 2.0),
        ("electric", 10.99, 2.0),
        ("electric", 11.0, 3.0),
        ("electric", 20.0, 3.0),
        ("electric", 20.99, 3.0),
        ("electric", 21.0, 4.0),
        ("electric", 61.0, 4.0),
        ("natural_gas", 3.99, 0.0),
        ("natural_gas", 4.0, 0.15),
        ("natural_gas", 10.0, 0.15),
        ("natural_gas", 10.99, 0.15),
        ("natural_gas", 11.0, 1.5),
        ("natural_gas", 20.0, 1.5),
        ("natural_gas", 20.99, 1.5),
        ("natural_gas", 21.0, 1.75),
        ("natural_gas", 30.0, 1.75),
        ("natural_gas", 30.99, 1.75),
        ("natural_gas", 31.0, 1.9),
        ("natural_gas", 40.0, 1.9),
        ("natural_gas", 40.99, 1.9),
        ("natural_gas", 41.0, 2.0),
        ("natural_gas", 60.0, 2.0),
        ("natural_gas", 60.01, 0.0),
    ],
)
@pytest.mark.parametrize("dac", [False, True])
def test_fuel_delta_r_and_dac_incentive_tiers(
    fuel: str, delta_r: float, rate: float, dac: bool
) -> None:
    result = estimate_insulation(
        make_inputs(heating_fuel=fuel, proposed_r=11.0 + delta_r, is_dac=dac)
    )

    expected_rate = rate + (1.0 if dac and rate > 0 else 0.0)
    assert result.incentive == pytest.approx(3900.0 * expected_rate)


def test_gas_reference_incentive_is_7410_dollars() -> None:
    result = estimate_insulation(make_inputs(heating_fuel="natural_gas", heating_efficiency=0.8))
    assert result.incentive == pytest.approx(7410.0)


@pytest.mark.parametrize(("fuel", "cap"), [("electric", 150_000.0), ("natural_gas", 250_000.0)])
def test_incentive_caps_update_net_investment_and_payback(fuel: str, cap: float) -> None:
    result = estimate_insulation(
        make_inputs(perimeter_ft=100_000.0, heating_fuel=fuel, is_dac=True, cost_per_sqft=8.0)
    )

    assert result.incentive == cap
    assert result.net_investment == result.project_cost - cap
    assert result.simple_payback_years == pytest.approx(
        result.net_investment / result.annual_cost_savings
    )
    assert any("capped" in flag for flag in result.flags)


def test_unknown_dac_receives_no_bonus_and_user_rate_is_explicit() -> None:
    unknown = estimate_insulation(make_inputs(is_dac=None))
    assert unknown.incentive == 15_600.0
    assert any("DAC status is unknown" in flag for flag in unknown.flags)
    custom = estimate_insulation(make_inputs(use_incentive_schedule=False, incentive_per_sqft=2.5))
    assert custom.incentive == 9750.0
    assert any("user override" in note for note in custom.assumptions)


def test_warehouse_cooling_uses_separate_realization_not_lf_squared() -> None:
    result = estimate_insulation(make_inputs(operating_load_factor=0.65))
    expected = (1 / 11 - 1 / 49) * 3900 * 650 * 24 * 0.65 * 0.75
    assert result.cooling_load_btu == pytest.approx(expected)
    assert not any("squared" in note for note in result.assumptions)


@pytest.mark.parametrize(
    ("use_class", "profile", "lf", "height", "windows"),
    [
        ("APARTMENT", "residential", 1.0, 10.0, 0.25),
        ("OFFICE BUILDING", "office", 0.75, 12.0, 0.35),
        ("RESTAURANTS", "retail", 0.85, 14.0, 0.30),
        ("OTHER STORAGE & WAREHOUSE FACILITIES", "warehouse", 0.65, 20.0, 0.08),
        ("AUTO BODY AND TIRE SHOPS", "warehouse", 0.65, 20.0, 0.08),
        ("SEASONAL", "intermittent", 0.5, 12.0, 0.20),
        (None, "office", 0.75, 12.0, 0.35),
    ],
)
def test_use_profiles_fill_unknown_height_and_operating_values(
    use_class: str | None, profile: str, lf: float, height: float, windows: float
) -> None:
    facts = SAMPLE_BUILDINGS[0].model_copy(update={"floor_height_ft": None, "use_class": use_class})
    inputs = inputs_from_facts(facts, Assumptions())

    assert inputs.operating_profile == profile
    assert inputs.operating_load_factor == lf
    assert inputs.floor_height_ft == height
    assert inputs.window_door_pct == windows
    assert any("noco_sheet" in note for note in estimate_insulation(inputs).assumptions)


def test_profiles_preserve_assessor_height_and_explicit_user_overrides() -> None:
    facts = SAMPLE_BUILDINGS[0].model_copy(deep=True)
    facts.use_class = "WAREHOUSE"
    facts.floor_height_ft = 16.0
    facts.sources["floor_height_ft"] = FieldSource(source="assessor", confidence=0.7)
    assumptions = Assumptions(operating_load_factor=0.75, window_door_pct=0.35, hdd=5000.0)
    inputs = inputs_from_facts(facts, assumptions)
    assert inputs.floor_height_ft == 16.0
    assert inputs.operating_load_factor == 0.75
    assert inputs.window_door_pct == 0.35
    assert inputs.hdd == 5000.0

    facts.sources["floor_height_ft"] = FieldSource(source="assumed", confidence=0.3)
    profiled = inputs_from_facts(facts, Assumptions())
    assert profiled.floor_height_ft == 20.0


@pytest.mark.parametrize(
    ("aspect", "shape", "expected"), [(1.0, 1.0, 400.0), (4.0, 1.0, 500.0), (4.0, 1.15, 575.0)]
)
def test_perimeter_fallback_uses_footprint_and_shape(
    aspect: float, shape: float, expected: float
) -> None:
    facts = SAMPLE_BUILDINGS[0].model_copy(
        update={"perimeter_ft": None, "footprint_sqft": 10_000.0}
    )
    inputs = inputs_from_facts(
        facts, Assumptions(perimeter_aspect_ratio=aspect, perimeter_shape_factor=shape)
    )
    assert inputs.perimeter_ft == pytest.approx(expected)
    assert any("assumed shape" in flag for flag in estimate_insulation(inputs).flags)


@pytest.mark.parametrize("field", ["heating_realization_factor", "cooling_realization_factor"])
@pytest.mark.parametrize("factor", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_realization_factors_are_rejected(field: str, factor: float) -> None:
    with pytest.raises(ValueError, match=field):
        estimate_insulation(make_inputs(**{field: factor}))


@pytest.mark.parametrize(
    ("use_class", "profile"),
    [
        ("AUTO BODY AND TIRE SHOPS", "warehouse"),  # R1 finding 3 / T17: not retail
        ("AUTO BODY AND TIRE SHOP", "warehouse"),
        ("AREA OR NEIGHBORHOOD SHOPPING CENTERS", "retail"),  # "SHOP" still means retail here
        ("MEDIUM RETAIL", "retail"),
        ("AUTO DEALERS", "retail"),
        ("LARGE RETAIL FOOD STORES", "retail"),
        ("BARS", "retail"),
        ("TIRE SHOP", "warehouse"),
        ("RETIREMENT HOME", "office"),  # "TIRE" inside "RETIREMENT" must not match
    ],
)
def test_operating_profile_auto_body_is_light_industrial(use_class: str, profile: str) -> None:
    facts = SAMPLE_BUILDINGS[0].model_copy(update={"use_class": use_class})
    assert inputs_from_facts(facts, Assumptions()).operating_profile == profile
