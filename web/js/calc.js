// Deterministic insulation calculator (port of src/features/noco_scout/calc.py, NOCO v5).
// Operations keep Python's order so every float matches the reference bit for bit.

import { ASSUMPTION_SOURCES, DEFAULT_ASSUMPTIONS } from "./contract.js";
import { comma0, g } from "./pyfmt.js";

export const BTU_PER_KWH = 3412.0;
export const BTU_PER_THERM = 100_000.0;
export const BTU_PER_MMBTU = 1_000_000.0;
export const DEFAULT_PERIMETER_FT = 400.0;
export const DEFAULT_FLOORS = 1;
export const BUFFALO_HDD = 6750.0;
export const HEATING_REALIZATION = 0.9;
export const COOLING_REALIZATION = 0.75;
// [operating load factor, floor height ft, window/door fraction] from NOCO v5 Assumptions.
export const OPERATING_PROFILES = Object.freeze({
  residential: [1.0, 10.0, 0.25],
  office: [0.75, 12.0, 0.35],
  retail: [0.85, 14.0, 0.3],
  warehouse: [0.65, 20.0, 0.08],
  intermittent: [0.5, 12.0, 0.2],
  custom: [1.0, 12.0, 0.2],
});

const CALC_INPUT_DEFAULTS = {
  cost_per_sqft: null,
  heating_realization_factor: null,
  cooling_realization_factor: 0.75,
  is_dac: null,
  use_incentive_schedule: true,
  operating_profile: null,
};

/** CalcInputs(**fields) with the model's defaults; provenance rides along non-enumerably. */
export function makeCalcInputs(fields, sourceFlags = [], sourceAssumptions = []) {
  const inputs = { ...CALC_INPUT_DEFAULTS, ...fields };
  Object.defineProperty(inputs, "sourceFlags", { value: [...sourceFlags] });
  Object.defineProperty(inputs, "sourceAssumptions", { value: [...sourceAssumptions] });
  return inputs;
}

function requireFinite(name, value) {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
}

function validateInputs(i) {
  const numeric = {
    perimeter_ft: i.perimeter_ft,
    floors: i.floors,
    floor_height_ft: i.floor_height_ft,
    exposed_wall_pct: i.exposed_wall_pct,
    window_door_pct: i.window_door_pct,
    existing_r: i.existing_r,
    proposed_r: i.proposed_r,
    hdd: i.hdd,
    cdd: i.cdd,
    operating_load_factor: i.operating_load_factor,
    heating_efficiency: i.heating_efficiency,
    cooling_cop: i.cooling_cop,
    electricity_per_kwh: i.prices.electricity_per_kwh,
    gas_per_therm: i.prices.gas_per_therm,
    incentive_per_sqft: i.incentive_per_sqft,
  };
  if (i.cost_per_sqft !== null) numeric.cost_per_sqft = i.cost_per_sqft;
  for (const field of ["heating_realization_factor", "cooling_realization_factor"]) {
    const factor = i[field];
    if (factor !== null) {
      numeric[field] = factor;
      if (!(factor >= 0 && factor <= 1)) throw new Error(`${field} must be between 0 and 1`);
    }
  }
  for (const [name, value] of Object.entries(numeric)) requireFinite(name, value);

  if (i.perimeter_ft < 0 || i.floors < 1 || i.floor_height_ft < 0) {
    throw new Error("perimeter, floors, and floor height must be non-negative");
  }
  if (!(i.exposed_wall_pct >= 0 && i.exposed_wall_pct <= 1) ||
      !(i.window_door_pct >= 0 && i.window_door_pct <= 1)) {
    throw new Error("wall exposure and window/door percentages must be between 0 and 1");
  }
  if (i.existing_r <= 0 || i.proposed_r <= i.existing_r) {
    throw new Error("proposed_r must be greater than a positive existing_r");
  }
  if (i.hdd < 0 || i.cdd < 0 || i.operating_load_factor < 0) {
    throw new Error("degree days and operating load factor must be non-negative");
  }
  if (i.heating_efficiency <= 0 || i.cooling_cop <= 0) {
    throw new Error("heating efficiency and cooling COP must be positive");
  }
  if ([i.prices.electricity_per_kwh, i.prices.gas_per_therm, i.incentive_per_sqft].some((v) => v < 0) ||
      (i.cost_per_sqft !== null && i.cost_per_sqft < 0)) {
    throw new Error("prices, incentive, and project cost must be non-negative");
  }
}

/** NOCO v5 National Grid Commercial Weatherization tiers, including gas exclusions. */
export function incentiveRateAndCap(i) {
  if (!i.use_incentive_schedule) return [i.incentive_per_sqft, null];
  const deltaR = i.proposed_r - i.existing_r;
  const cap = i.heating_fuel === "electric" ? 150_000.0 : 250_000.0;
  if (deltaR < 4 || (i.heating_fuel === "natural_gas" && deltaR > 60)) return [0.0, cap];
  let rate;
  if (i.heating_fuel === "electric") {
    rate = deltaR < 11 ? 2.0 : deltaR < 21 ? 3.0 : 4.0;
  } else {
    rate = deltaR < 11 ? 0.15 : deltaR < 21 ? 1.5 : deltaR < 31 ? 1.75 : deltaR < 41 ? 1.9 : 2.0;
  }
  return [rate + (i.is_dac === true ? 1.0 : 0.0), cap];
}

/** Calculate NOCO v5 savings; legacy effective-HDD inputs retain the Golden result. */
export function estimateInsulation(i) {
  validateInputs(i);

  const wallArea =
    i.perimeter_ft * i.floor_height_ft * i.floors * i.exposed_wall_pct * (1.0 - i.window_door_pct);
  const deltaU = 1.0 / i.existing_r - 1.0 / i.proposed_r;
  const heatingFactor = i.heating_realization_factor;
  const heatingLoad =
    deltaU * wallArea * i.hdd * 24.0 * i.operating_load_factor *
    (heatingFactor !== null ? heatingFactor : 1.0);
  const coolingFactor =
    i.cooling_realization_factor !== null ? i.cooling_realization_factor : COOLING_REALIZATION;
  const coolingLoad = deltaU * wallArea * i.cdd * 24.0 * i.operating_load_factor * coolingFactor;
  const coolingKwh = coolingLoad / BTU_PER_KWH / i.cooling_cop;

  let heatingKwh, heatingTherms, heatingCostSavings;
  if (i.heating_fuel === "electric") {
    heatingKwh = heatingLoad / BTU_PER_KWH / i.heating_efficiency;
    heatingTherms = 0.0;
    heatingCostSavings = heatingKwh * i.prices.electricity_per_kwh;
  } else if (i.heating_fuel === "natural_gas") {
    heatingKwh = 0.0;
    heatingTherms = heatingLoad / BTU_PER_THERM / i.heating_efficiency;
    heatingCostSavings = heatingTherms * i.prices.gas_per_therm;
  } else {
    throw new Error(`unsupported heating fuel: ${i.heating_fuel}`);
  }

  const totalKwh = heatingKwh + coolingKwh;
  const siteMmbtu = (totalKwh * BTU_PER_KWH + heatingTherms * BTU_PER_THERM) / BTU_PER_MMBTU;
  const annualCostSavings = heatingCostSavings + coolingKwh * i.prices.electricity_per_kwh;
  const [incentiveRate, incentiveCap] = incentiveRateAndCap(i);
  const uncappedIncentive = wallArea * incentiveRate;
  const incentive =
    incentiveCap !== null ? Math.min(uncappedIncentive, incentiveCap) : uncappedIncentive;
  const projectCost = i.cost_per_sqft === null ? null : wallArea * i.cost_per_sqft;
  const netInvestment = projectCost === null ? null : projectCost - incentive;

  const flags = [...(i.sourceFlags || [])];
  if (i.use_incentive_schedule && i.is_dac === null) {
    flags.push("DAC status is unknown; no DAC bonus assumed.");
  }
  if (incentiveCap !== null && uncappedIncentive > incentiveCap) {
    flags.push(`Incentive capped at $${comma0(incentiveCap)} [noco_sheet].`);
  }
  if (projectCost === null) flags.push("Project cost is unknown; payback is unavailable.");
  if (annualCostSavings <= 0) flags.push("Annual cost savings are zero; payback is unavailable.");

  let simplePayback = null;
  if (netInvestment !== null && annualCostSavings > 0) {
    simplePayback = netInvestment / annualCostSavings;
  }

  const label = (field, value) => {
    if (heatingFactor !== null &&
        ((field === "hdd" && value === BUFFALO_HDD) || (field === "cdd" && value === 650.0))) {
      return "noco_sheet";
    }
    if (i.operating_profile in OPERATING_PROFILES) {
      const profileValues = OPERATING_PROFILES[i.operating_profile];
      if ((field === "operating_load_factor" && value === profileValues[0]) ||
          (field === "window_door_pct" && value === profileValues[2])) {
        return "noco_sheet";
      }
    }
    return value === DEFAULT_ASSUMPTIONS[field] ? ASSUMPTION_SOURCES[field] : "user";
  };

  const incentiveSource = i.use_incentive_schedule
    ? "noco_sheet; National Grid fuel/Delta-R/DAC schedule"
    : "user override";
  const assumptions = [
    `HDD=${g(i.hdd)} [${label("hdd", i.hdd)}]`,
    `CDD=${g(i.cdd)} [${label("cdd", i.cdd)}]`,
    `Operating load factor=${g(i.operating_load_factor)} ` +
      `[${label("operating_load_factor", i.operating_load_factor)}]`,
    heatingFactor !== null
      ? `Heating realization factor=${g(heatingFactor)} ` +
        `[${heatingFactor === HEATING_REALIZATION ? "noco_sheet" : "user"}]`
      : "Heating realization factor=1 [assumed; legacy HDD is already effective]",
    `Cooling realization factor=${g(coolingFactor)} ` +
      `[${coolingFactor === COOLING_REALIZATION ? "noco_sheet" : "user"}]; ` +
      "cooling load = operating LF × cooling realization factor",
    `Window and door fraction=${g(i.window_door_pct)} ` +
      `[${label("window_door_pct", i.window_door_pct)}]`,
    `Incentive=$${g(incentiveRate)}/sq ft [${incentiveSource}]`,
    `Heating fuel=${i.heating_fuel}; efficiency/COP=${g(i.heating_efficiency)} ` +
      "[assumed scenario unless confirmed by the customer]",
    ...(i.sourceAssumptions || []),
  ];
  if (incentiveCap !== null) {
    assumptions.push(`Incentive cap=$${g(incentiveCap)} [noco_sheet]`);
    assumptions.push(
      i.is_dac === null
        ? "DAC status=unknown; non-DAC rate [assumed]"
        : `DAC status=${i.is_dac ? "True" : "False"} [user; designation requires confirmation]`,
    );
  }

  return {
    insulated_wall_area_sqft: wallArea,
    delta_u: deltaU,
    heating_load_btu: heatingLoad,
    cooling_load_btu: coolingLoad,
    heating_kwh: heatingKwh,
    heating_therms: heatingTherms,
    cooling_kwh: coolingKwh,
    total_kwh: totalKwh,
    site_mmbtu: siteMmbtu,
    annual_cost_savings: annualCostSavings,
    incentive,
    project_cost: projectCost,
    net_investment: netInvestment,
    simple_payback_years: simplePayback,
    ten_year_energy_value: annualCostSavings * 10.0,
    flags,
    assumptions,
  };
}

/** Conservative mapping of public building use to NOCO's operating profiles. */
export function operatingProfile(useClass) {
  const use = (useClass || "").toUpperCase();
  // Auto body / tire shops are service bays (Warehouse / Light Industrial), checked before
  // the retail words, which include "SHOP". "TIRE SHOP", not "TIRE": "RETIREMENT" must not match.
  const lightIndustrial = ["WAREHOUSE", "STORAGE", "INDUSTRIAL", "MANUFACTUR", "AUTO BODY", "TIRE SHOP"];
  if (lightIndustrial.some((w) => use.includes(w))) return "warehouse";
  if (["APARTMENT", "RESIDENTIAL", "HOTEL", "MOTEL", "HOSPITAL", "LODG"].some((w) => use.includes(w))) {
    return "residential";
  }
  const retail = ["RETAIL", "RESTAURANT", "STORE", "SHOP", "DINER", "FAST FOOD", "BAR", "AUTO DEALER"];
  if (retail.some((w) => use.includes(w))) return "retail";
  if (["SEASONAL", "INTERMITTENT"].some((w) => use.includes(w))) return "intermittent";
  return "office";
}

const sourceOf = (facts, field) => (facts.sources || {})[field] || null;

/** Build calculator inputs, using explicit assumptions for unavailable GIS facts. */
export function inputsFromFacts(f, a) {
  const flags = [];
  const sourceAssumptions = [];
  const set = a.fieldsSet;
  const profile = a.operating_profile === "auto" ? operatingProfile(f.use_class) : a.operating_profile;
  const profileValues =
    profile !== null && profile in OPERATING_PROFILES
      ? OPERATING_PROFILES[profile]
      : [a.operating_load_factor, a.floor_height_ft, a.window_door_pct];
  let [loadFactor, profileHeight, windowPct] = profileValues;
  if (profile !== null) {
    const profileSource =
      a.operating_profile === "auto" ? "assumed use-class mapping" : "user selection";
    sourceAssumptions.push(
      `Operating profile=${profile} [${profileSource}; NOCO v5 values noco_sheet]`,
    );
  }
  if (set.has("operating_load_factor")) {
    loadFactor = a.operating_load_factor;
  } else if (profile !== null) {
    sourceAssumptions.push(`Profile operating LF=${g(loadFactor)} [noco_sheet; assumed profile]`);
  }
  if (set.has("window_door_pct")) {
    windowPct = a.window_door_pct;
  } else if (profile !== null) {
    sourceAssumptions.push(
      `Profile window/door fraction=${g(windowPct)} [noco_sheet; assumed profile]`,
    );
  }

  let perimeter = f.perimeter_ft;
  if (perimeter === null || perimeter === undefined || perimeter <= 0) {
    perimeter = DEFAULT_PERIMETER_FT;
    const area = f.footprint_sqft;
    const aspect = a.perimeter_aspect_ratio !== null ? a.perimeter_aspect_ratio : 1.5;
    const shape = a.perimeter_shape_factor !== null ? a.perimeter_shape_factor : 1.0;
    if (!Number.isFinite(aspect) || aspect <= 0 || !Number.isFinite(shape) || shape <= 0) {
      throw new Error("perimeter aspect ratio and shape factor must be finite and positive");
    }
    if (area !== null && area !== undefined && Number.isFinite(area) && area > 0) {
      perimeter = 2 * (Math.sqrt(area * aspect) + Math.sqrt(area / aspect)) * shape;
      sourceAssumptions.push(
        `Perimeter=${g(perimeter)} ft [assumed; NOCO v5 footprint/shape formula]; ` +
          `aspect ratio=${g(aspect)}, shape factor=${g(shape)} [assumed]`,
      );
      flags.push("Perimeter is unavailable; using assumed shape with the sourced footprint.");
    } else {
      flags.push("Perimeter is unavailable; using an assumed 400 ft perimeter.");
      sourceAssumptions.push("Perimeter=400 ft [assumed; footprint unavailable]");
    }
  } else if (sourceOf(f, "perimeter_ft")?.source === "assumed") {
    flags.push("Perimeter is assumed in building facts.");
    sourceAssumptions.push(`Perimeter=${g(perimeter)} ft [assumed]`);
  }

  let floors = f.floors;
  if (floors === null || floors === undefined || floors < 1) {
    floors = DEFAULT_FLOORS;
    flags.push("Floor count is unavailable; using 1 assumed floor.");
    sourceAssumptions.push("Floors=1 [assumed]");
  } else if (sourceOf(f, "floors")?.source === "assumed") {
    flags.push("Floor count is assumed in building facts.");
    sourceAssumptions.push(`Floors=${floors} [assumed]`);
  }

  let floorHeight = f.floor_height_ft;
  const heightSource = sourceOf(f, "floor_height_ft");
  if (floorHeight === null || floorHeight === undefined || floorHeight <= 0 ||
      (heightSource && heightSource.source === "assumed")) {
    floorHeight = set.has("floor_height_ft") ? a.floor_height_ft : profileHeight;
    flags.push("Floor height is unavailable; using the configured assumption.");
    const defaultSource = set.has("floor_height_ft") ? "user" : "noco_sheet";
    sourceAssumptions.push(`Floor height=${g(floorHeight)} ft [assumed; ${defaultSource} default]`);
  }
  const heatingFactor = a.heating_realization_factor;
  let hdd = a.hdd;
  if (!set.has("hdd") && heatingFactor !== null) {
    // Preserve the frozen effective-HDD default while the live GIS flow uses raw sheet HDD.
    hdd = BUFFALO_HDD;
  }
  if (!set.has("heating_fuel")) {
    flags.push(
      a.heating_fuel === "electric" && a.heating_efficiency === 1.0
        ? "Heating system is assumed electric resistance (COP 1) [assumed]; confirm with the customer."
        : `Heating fuel=${a.heating_fuel} is assumed; confirm with the customer [assumed].`,
    );
  }
  return makeCalcInputs(
    {
      perimeter_ft: perimeter,
      floors,
      floor_height_ft: floorHeight,
      exposed_wall_pct: a.exposed_wall_pct,
      window_door_pct: windowPct,
      existing_r: a.existing_r,
      proposed_r: a.proposed_r,
      hdd,
      cdd: a.cdd,
      operating_load_factor: loadFactor,
      heating_fuel: a.heating_fuel,
      heating_efficiency: a.heating_efficiency,
      cooling_cop: a.cooling_cop,
      prices: a.prices,
      incentive_per_sqft: a.incentive_per_sqft,
      cost_per_sqft: a.cost_per_sqft,
      heating_realization_factor: heatingFactor,
      cooling_realization_factor: a.cooling_realization_factor,
      is_dac: a.is_dac,
      use_incentive_schedule: a.use_incentive_schedule && !set.has("incentive_per_sqft"),
      operating_profile: profile,
    },
    flags,
    sourceAssumptions,
  );
}
