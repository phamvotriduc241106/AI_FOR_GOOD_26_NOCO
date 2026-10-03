// Data contract (port of src/features/noco_scout/contract.py).
//
// Plain objects replace the Pydantic models. Assumptions remember which fields the caller set
// explicitly (Python's `model_fields_set`), because the calculator treats an explicit value
// differently from a default (for example an explicit HDD is a raw HDD).

export const OSM_ATTRIBUTION = "© OpenStreetMap contributors";
export const NOT_IN_PUBLIC_DATA = "Not in public data: ask the customer";
export const UTILITY = "National Grid";
export const INCENTIVE_PROGRAM = "National Grid - Commercial Weatherization";

export const DEFAULT_PRICES = Object.freeze({
  electricity_per_kwh: 0.16,
  gas_per_therm: 1.2,
  propane_per_gal: 2.8,
  oil_per_gal: 3.4,
  district_per_mmbtu: 18.0,
});

export const DEFAULT_ASSUMPTIONS = Object.freeze({
  floor_height_ft: 12.0,
  window_door_pct: 0.35,
  exposed_wall_pct: 1.0,
  existing_r: 11.0,
  proposed_r: 49.0,
  hdd: 6075.0,
  cdd: 650.0,
  operating_load_factor: 0.75,
  heating_fuel: "electric",
  heating_efficiency: 1.0,
  cooling_cop: 3.0,
  prices: DEFAULT_PRICES,
  incentive_per_sqft: 4.0,
  cost_per_sqft: null,
  margin_pct: null,
  heating_realization_factor: 0.9,
  cooling_realization_factor: 0.75,
  is_dac: null,
  use_incentive_schedule: true,
  operating_profile: "auto",
  perimeter_aspect_ratio: 1.5,
  perimeter_shape_factor: 1.0,
});

export const ASSUMPTION_SOURCES = Object.freeze({
  floor_height_ft: "noco_sheet",
  window_door_pct: "noco_sheet",
  exposed_wall_pct: "noco_sheet",
  existing_r: "noco_sheet",
  proposed_r: "noco_sheet",
  hdd: "assumed",
  cdd: "assumed",
  operating_load_factor: "noco_sheet",
  heating_fuel: "noco_sheet",
  heating_efficiency: "noco_sheet",
  cooling_cop: "noco_sheet",
  prices: "noco_sheet",
  incentive_per_sqft: "noco_sheet",
  cost_per_sqft: "user",
  margin_pct: "user",
});

/**
 * Assumptions(**overrides): defaults plus the overrides, with `fieldsSet` = the keys passed.
 * Unknown keys throw, like the Pydantic model's extra="forbid".
 */
export function makeAssumptions(overrides = {}) {
  for (const key of Object.keys(overrides)) {
    if (!(key in DEFAULT_ASSUMPTIONS)) throw new Error(`Unknown assumption: ${key}`);
  }
  const prices = { ...DEFAULT_PRICES, ...(overrides.prices || {}) };
  return Object.freeze({
    ...DEFAULT_ASSUMPTIONS,
    ...overrides,
    prices: Object.freeze(prices),
    fieldsSet: new Set(Object.keys(overrides)),
  });
}

export function pricesEqualDefault(prices) {
  return Object.keys(DEFAULT_PRICES).every((k) => prices[k] === DEFAULT_PRICES[k]);
}

/** An Opportunity with the model's defaults. */
export function makeOpportunity(fields = {}) {
  return {
    utility: UTILITY,
    incentive_program: null,
    current_supplier: NOT_IN_PUBLIC_DATA,
    project_revenue: null,
    estimated_profit: null,
    margin_pct: null,
    illustrative: true,
    notes: [],
    ...fields,
  };
}
