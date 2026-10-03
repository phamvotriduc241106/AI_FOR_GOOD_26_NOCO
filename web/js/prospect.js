// Prospect ranking and illustrative NOCO opportunities (port of prospect.py).

import { estimateInsulation, inputsFromFacts } from "./calc.js";
import { INCENTIVE_PROGRAM, NOT_IN_PUBLIC_DATA, UTILITY, makeOpportunity } from "./contract.js";
import { cmpStr, g } from "./pyfmt.js";

/** Use calculator cost and explicit margin; unknown money remains unavailable. */
export function buildOpportunity(f, r, a) {
  const margin = a.margin_pct;
  if (margin !== null && (!Number.isFinite(margin) || margin < 0 || margin > 1)) {
    throw new Error("margin_pct must be a finite fraction between 0 and 1");
  }
  const revenue = a.cost_per_sqft !== null ? r.project_cost : null;
  const profit = revenue !== null && margin !== null ? revenue * margin : null;
  const notes = [
    "ILLUSTRATIVE: revenue and profit are scenarios, not validated NOCO quotes.",
    `Utility: ${UTILITY} [noco_sheet]. Program: ${INCENTIVE_PROGRAM} ` +
      "[noco_sheet reference]; eligibility needs confirmation.",
    NOT_IN_PUBLIC_DATA,
  ];
  if (revenue === null) {
    notes.push("Project revenue and profit unavailable: needs NOCO cost [user].");
  } else {
    notes.push(
      "ILLUSTRATIVE project revenue = calculator project cost: insulated wall area " +
        "[deterministic NOCO calculation + GIS/assumptions] × cost per sq ft [user].",
    );
  }
  if (margin === null) {
    notes.push("Estimated profit unavailable: needs NOCO margin [user].");
  } else {
    notes.push(`ILLUSTRATIVE margin fraction=${g(margin)} [user].`);
  }
  if (profit !== null) {
    notes.push("ILLUSTRATIVE estimated profit = project revenue × margin fraction [user].");
  }
  return makeOpportunity({
    utility: UTILITY,
    incentive_program: INCENTIVE_PROGRAM,
    current_supplier: NOT_IN_PUBLIC_DATA,
    project_revenue: revenue,
    estimated_profit: profit,
    margin_pct: margin,
    illustrative: true,
    notes,
  });
}

/** One prospect for a building (the pages' make_prospect). */
export function makeProspect(facts, a, rank = 1) {
  const inputs = inputsFromFacts(facts, a);
  const result = estimateInsulation(inputs);
  return {
    facts,
    inputs,
    result,
    opportunity: buildOpportunity(facts, result, a),
    score: result.annual_cost_savings,
    rank,
  };
}

/** Rank by annual savings, shorter known payback, then address; ranks start at 1. */
export function rankProspects(items, a, top = 25) {
  const prospects = items.map((facts) => makeProspect(facts, a, 0));
  const payback = (p) =>
    p.result.simple_payback_years !== null ? p.result.simple_payback_years : Infinity;
  prospects.sort(
    (x, y) =>
      y.score - x.score || payback(x) - payback(y) || cmpStr(x.facts.address, y.facts.address),
  );
  const selected = prospects.slice(0, Math.max(0, top));
  selected.forEach((p, index) => {
    p.rank = index + 1;
  });
  return selected;
}
