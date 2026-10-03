// Printable exports (port of report.py): customer report, manager report, prospect CSV.
//
// Same self-contained HTML as the Python version (inline CSS, NOCO logo as a data URL).
// The CUSTOMER report never shows NOCO revenue, profit or margin.

import { NOT_IN_PUBLIC_DATA, OSM_ATTRIBUTION, pricesEqualDefault } from "./contract.js";
import {
  cmpStr, comma0, escapeHtml as escape, fixed, floatRepr, g, longDate, percent0, pyRound,
  uniqueInOrder,
} from "./pyfmt.js";

export const SOURCE_LABELS = {
  geocoder: "US Census geocoder",
  osm: "OpenStreetMap",
  assessor: "Buffalo assessment roll",
  user: "Entered by NOCO",
  assumed: "Assumed",
  noco_sheet: "NOCO calculator",
};
const HEATING = { electric: "Electric", natural_gas: "Natural gas" };
const MISSING = "Not found in public data";

const BRACKET = /\s*\[([^\]]*)\]/g;
const SOURCE_WORDS = {
  noco_sheet: "NOCO calculator (v5)",
  assumed: "Assumption",
  user: "User input",
  ILLUSTRATIVE: "illustrative",
};

/** "HDD=6750 [noco_sheet]" -> ["HDD = 6750", "NOCO calculator (v5)"]. */
export function splitAssumption(line) {
  let text = line.replace(BRACKET, "").trim();
  text = text.replace(/\s*=\s*/g, " = ");
  text = text.replace(/\$(\d{4,})(?![\d.])/g, (_, digits) => `$${comma0(Number(digits))}`);
  const parts = [];
  for (const match of line.matchAll(BRACKET)) {
    for (let part of match[1].split(";").map((piece) => piece.trim())) {
      if (!part) continue;
      if (Object.hasOwn(SOURCE_WORDS, part)) {
        part = SOURCE_WORDS[part];
      } else {
        part = part.replaceAll("NOCO v5 values noco_sheet", "values from NOCO calculator (v5)");
        part = part.replaceAll("noco_sheet", "NOCO calculator (v5)");
      }
      part = part[0].toUpperCase() + part.slice(1);
      if (!parts.includes(part)) parts.push(part);
    }
  }
  return [text, parts.join("; ")];
}

function assumptionTable(lines) {
  const rows = uniqueInOrder(lines)
    .map(splitAssumption)
    .map(([text, src]) =>
      `<tr><td>${escape(text)}</td><td class='src'>${escape(src || "Calculator note")}</td></tr>`)
    .join("");
  return `<table><tr><th>Assumption</th><th>Source</th></tr>${rows}</table>`;
}

const CSS = `
@page { size: letter; margin: 0.5in; }
* { box-sizing: border-box; }
body { font: 13px/1.45 -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: #1d2a33;
  margin: 0 auto; max-width: 8in; padding: 16px; background: #fff; }
header { display: flex; align-items: center; justify-content: space-between; gap: 16px;
  border-bottom: 3px solid #1f7a4d; padding-bottom: 10px; }
header img { height: 56px; }
.brand { font-size: 22px; font-weight: 700; color: #1f7a4d; }
h1 { font-size: 20px; margin: 14px 0 2px; }
h2 { font-size: 14px; text-transform: uppercase; letter-spacing: .04em; color: #1f7a4d;
  margin: 18px 0 6px; }
.muted { color: #5b6b75; font-size: 12px; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 12px; }
.card { border: 1px solid #cfe3d8; border-radius: 6px; padding: 8px 10px; background: #f3faf6; }
.card b { display: block; font-size: 18px; color: #14532d; }
.card span { font-size: 11px; color: #44535c; }
.demo, .card b.demo { color: #EF4444; font-weight: 600;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid #e3e8eb;
  vertical-align: top; }
th { font-size: 11px; color: #44535c; font-weight: 600; }
td.src { font-size: 11px; color: #5b6b75; }
ul { margin: 4px 0; padding-left: 18px; }
.callout { border-left: 4px solid #d97706; background: #fff7ed; padding: 6px 10px;
  margin-top: 10px; }
footer { margin-top: 16px; border-top: 1px solid #e3e8eb; padding-top: 6px; font-size: 11px;
  color: #5b6b75; }
@media print { body { padding: 0; } .card, table { break-inside: avoid; } }
`;

/** Options shared by the renderers: the embedded logo and the "Prepared" date. */
export const reportContext = { logoDataUrl: null, today: () => new Date() };

function logoHtml() {
  return reportContext.logoDataUrl
    ? `<img src="${reportContext.logoDataUrl}" alt="NOCO">`
    : '<div class="brand">NOCO</div>';
}

const money = (value) => (value === null || value === undefined ? "—" : `$${comma0(value)}`);
const num = (value, unit = "", digits = 0) =>
  value === null || value === undefined ? "—" : `${fixed(value, digits, true)}${unit}`;

function card(value, label, demo = false) {
  const style = demo ? ' class="demo"' : "";
  return `<div class='card'><b${style}>${escape(value)}</b><span>${escape(label)}</span></div>`;
}

/** Describe the actual scenario values; customer callers never pass a margin. */
function demoLegend(cost, margin = null, enabled = false) {
  if (cost === null && margin === null && !enabled) return "";
  const details = [];
  if (cost !== null) {
    details.push(
      `installed cost $${g(cost)}/sq ft is a demo scenario, not a NOCO price; ` +
        "the app default was chosen by team HELIX",
    );
  }
  if (margin !== null) {
    details.push(
      `margin ${percent0(margin)} is illustrative; the app default is the midpoint ` +
        "of the 30-40% NOCO mentioned verbally",
    );
  }
  const context = details.length ? ` (${details.join("; ")})` : "";
  return (
    '<p class="demo">Red values are DEMO values for illustration' +
    `${escape(context)}. They are not NOCO quotes.</p>`
  );
}

function source(facts, field) {
  const src = (facts.sources || {})[field];
  if (!src) return "";
  const label = Object.hasOwn(SOURCE_LABELS, src.source) ? SOURCE_LABELS[src.source] : src.source;
  const text = `${label} (${g(src.confidence)})`;
  const note = src.note || "";
  const repeats = label.toLowerCase().includes(note.toLowerCase()) || label.toLowerCase().endsWith(note.toLowerCase());
  return escape(note && !repeats ? `${text} · ${note}` : text);
}

function page(title, body, extraCss = "") {
  return (
    '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">' +
    `<title>${escape(title)}</title><style>${CSS}${extraCss}</style></head><body>` +
    `<header>${logoHtml()}<div class='muted'>Prepared ${longDate(reportContext.today())}</div>` +
    `</header>${body}</body></html>\n`
  );
}

const present = (v) => v !== null && v !== undefined;

function buildingRows(facts) {
  const rows = [
    ["Address", facts.address, "address"],
    ["Building type", facts.use_class, "use_class"],
    ["Neighborhood", facts.neighborhood, "neighborhood"],
    ["Floors", facts.floors, "floors"],
    ["Floor height", facts.floor_height_ft ? num(facts.floor_height_ft, " ft", 1) : null, "floor_height_ft"],
    ["Footprint", facts.footprint_sqft ? num(facts.footprint_sqft, " sq ft") : null, "footprint_sqft"],
    ["Perimeter", facts.perimeter_ft ? num(facts.perimeter_ft, " ft") : null, "perimeter_ft"],
  ];
  let html = rows
    .map(([label, value, key]) =>
      `<tr><th>${label}</th><td>${present(value) ? escape(String(value)) : MISSING}</td>` +
      `<td class='src'>${present(value) ? source(facts, key) : ""}</td></tr>`)
    .join("");
  if (facts.sources && "join" in facts.sources) {
    html +=
      "<tr><th>Map ↔ city records match</th><td></td>" +
      `<td class='src'>${source(facts, "join")}</td></tr>`;
  }
  return html;
}

/** One-page, printable customer report. Never shows NOCO revenue, profit or margin. */
export function renderCustomerReport(facts, inputs, result, opportunity = null) {
  const program = (opportunity ? opportunity.incentive_program : null) || "the utility program";
  const utility = opportunity ? opportunity.utility : null;
  const supplier = opportunity ? opportunity.current_supplier : NOT_IN_PUBLIC_DATA;
  const heating = Object.hasOwn(HEATING, inputs.heating_fuel) ? HEATING[inputs.heating_fuel] : inputs.heating_fuel;

  let payback;
  if (result.project_cost !== null) {
    payback =
      "<div class='cards'>" +
      card(money(result.project_cost), "Project cost · Illustrative estimate", true) +
      card(money(result.net_investment), "Net investment after incentive · Illustrative estimate", true) +
      card(
        result.simple_payback_years !== null ? `${fixed(result.simple_payback_years, 1, true)} years` : "Unavailable",
        "Simple payback · Illustrative estimate",
        result.simple_payback_years !== null,
      ) +
      "</div>";
  } else {
    payback =
      "<div class='callout'><b>Needs an installation quote.</b> Payback depends on the " +
      "installed cost, which a NOCO site visit confirms. We do not estimate it without " +
      "a real quote.</div>";
  }

  let energy = `${num(result.total_kwh, " kWh")} electricity`;
  if (result.heating_therms) energy += ` + ${num(result.heating_therms, " therms")} gas`;
  const headline =
    card(money(result.annual_cost_savings), "Energy cost saved per year") +
    card(num(result.site_mmbtu, " MMBtu", 1), `${energy} saved per year`) +
    card(money(result.incentive), `Estimated incentive (${program})`) +
    card(money(result.ten_year_energy_value), "Energy value over 10 years");
  const heatingRow = `${heating} (efficiency ${g(inputs.heating_efficiency)})`;

  const body = `
<h1>Wall insulation upgrade: savings estimate</h1>
<div class="muted">${escape(facts.address)}</div>
${demoLegend(inputs.cost_per_sqft, null, result.project_cost !== null)}
<div class="cards">${headline}</div>
${payback}

<h2>Recommended upgrade</h2>
<table>
<tr><th>Wall insulation</th><td>R-${g(inputs.existing_r)} → R-${g(inputs.proposed_r)}</td></tr>
<tr><th>Insulated wall area</th><td>${num(result.insulated_wall_area_sqft, " sq ft")}</td></tr>
<tr><th>Heating system</th><td>${escape(heatingRow)}</td></tr>
<tr><th>Cooling efficiency</th><td>COP ${g(inputs.cooling_cop)}</td></tr>
${utility ? `<tr><th>Utility</th><td>${escape(utility)}</td></tr>` : ""}
<tr><th>Current energy supplier</th><td>${escape(supplier)}</td></tr>
</table>

<h2>Your building, from public records</h2>
<table>${buildingRows(facts)}</table>

<h2>Next steps</h2>
<ul>
<li>A NOCO specialist visits to confirm walls, existing insulation and the heating system.</li>
<li>NOCO prepares an installed-cost quote, so the payback above becomes exact.</li>
<li>NOCO checks every program you may qualify for (${escape(program)}, and also NYSERDA and
National Fuel where they apply).</li>
</ul>

<h2>Assumptions and notes</h2>
${assumptionTable([...result.assumptions, ...result.flags])}

<footer>This is an estimate from public data and NOCO's reference insulation calculator, not a
quote. Building data: ${escape(OSM_ATTRIBUTION)} (ODbL); City of Buffalo assessment roll;
US Census geocoder.</footer>
`;
  return page(`Insulation savings estimate: ${facts.address}`, body);
}

const MANAGER_CSS = `
@page { size: letter landscape; margin: 0.4in; }
body { max-width: 10.2in; }
.wide th, .wide td { font-size: 11px; padding: 3px 4px; }
.wide td.n { text-align: right; white-space: nowrap; }
th.green, td.green { background: #e7f6ec; }
th.ill, td.ill { background: #fff4e5; }
`;

// NOCO's green output cells (sheet SC, E5:E11), in the sheet's order.
export const GREEN_COLUMNS = [
  "Heating saved",
  "Cooling kWh",
  "Total electric kWh",
  "Site MMBtu",
  "Energy $ / yr",
  "Incentive",
  "10-yr energy value",
];

const heatingSaved = (r) => (r.heating_therms ? num(r.heating_therms, " therms") : num(r.heating_kwh, " kWh"));

function managerRow(p) {
  const f = p.facts;
  const r = p.result;
  const o = p.opportunity;
  const join = (f.sources || {}).join;
  const payback = r.simple_payback_years === null ? "needs cost" : `${fixed(r.simple_payback_years, 1)} yr`;
  const green = [
    heatingSaved(r),
    num(r.cooling_kwh),
    num(r.total_kwh),
    num(r.site_mmbtu, "", 1),
    money(r.annual_cost_savings),
    money(r.incentive),
    money(r.ten_year_energy_value),
  ];
  const illustrative = [
    [o.project_revenue !== null ? money(o.project_revenue) : "needs cost", o.project_revenue],
    [o.estimated_profit !== null ? money(o.estimated_profit) : "needs margin", o.estimated_profit],
  ];
  return (
    `<tr><td class='n'>${p.rank}</td><td>${escape(f.address)}</td>` +
    `<td>${escape(f.neighborhood || "—")}</td><td>${escape(f.use_class || "—")}</td>` +
    `<td class='n'>${f.floors ? num(f.floors) : "—"}</td>` +
    `<td class='n'>${join ? g(join.confidence) : "—"}</td>` +
    green.map((v) => `<td class='n green'>${v}</td>`).join("") +
    `<td class='n${r.simple_payback_years !== null ? " demo" : ""}'>${payback}</td>` +
    illustrative.map(([text, value]) => `<td class='n ill${value !== null ? " demo" : ""}'>${text}</td>`).join("") +
    "</tr>"
  );
}

function assumptionRows(prospects, a) {
  const total = prospects.length;
  const counts = new Map();
  for (const p of prospects) {
    for (const line of uniqueInOrder(p.result.assumptions)) counts.set(line, (counts.get(line) || 0) + 1);
  }
  const shared = (prospects.length ? prospects[0].result.assumptions : []).filter((l) => counts.get(l) === total);
  const varying = [...counts.keys()]
    .filter((l) => counts.get(l) < total)
    .sort((x, y) => counts.get(y) - counts.get(x) || cmpStr(x, y));
  const rows = uniqueInOrder(shared).map((line) => [line, `all ${total}`]);
  rows.push(...varying.map((line) => [line, `${counts.get(line)} of ${total}`]));

  const pricesSrc = pricesEqualDefault(a.prices) ? "noco_sheet" : "user";
  const cost = a.cost_per_sqft === null ? "not set" : `$${g(a.cost_per_sqft)}/sq ft`;
  const margin = a.margin_pct === null ? "not set" : percent0(a.margin_pct);
  rows.push(
    [`Installed cost=${cost} [DEMO value; ILLUSTRATIVE]`, "revenue, payback"],
    [`NOCO margin=${margin} [DEMO value; ILLUSTRATIVE]`, "profit"],
    [
      `Electricity=$${g(a.prices.electricity_per_kwh)}/kWh, gas=$${g(a.prices.gas_per_therm)}` +
        `/therm [${pricesSrc}]`,
      "energy $ / yr",
    ],
  );
  return rows
    .map(([line, scope]) => {
      const [text, src] = splitAssumption(line);
      const demo =
        (line.startsWith("Installed cost=") && a.cost_per_sqft !== null) ||
        (line.startsWith("NOCO margin=") && a.margin_pct !== null);
      return (
        `<tr><td class='${demo ? "demo" : ""}'>${escape(text)}</td>` +
        `<td class='src'>${escape(src)}</td><td class='src'>${escape(scope)}</td></tr>`
      );
    })
    .join("");
}

const sum = (values) => values.reduce((acc, v) => acc + v, 0);

/** Printable ranked prospect list for NOCO managers. */
export function renderManagerReport(prospects, a) {
  const knownRevenue = prospects.map((p) => p.opportunity.project_revenue).filter((v) => v !== null);
  const knownProfit = prospects.map((p) => p.opportunity.estimated_profit).filter((v) => v !== null);
  const cards =
    card(comma0(prospects.length), "Prospects in this list") +
    card(money(sum(prospects.map((p) => p.result.annual_cost_savings))), "Energy $ saved / yr") +
    card(money(sum(prospects.map((p) => p.result.incentive))), "Incentives available") +
    card(knownProfit.length ? money(sum(knownProfit)) : "needs cost + margin", "NOCO profit (ILLUSTRATIVE)", knownProfit.length > 0);
  const header =
    "<tr><th>#</th><th>Address</th><th>Neighborhood</th><th>Building type</th>" +
    "<th>Floors</th><th>Match</th>" +
    GREEN_COLUMNS.map((c) => `<th class='green'>${c}</th>`).join("") +
    "<th>Payback</th><th class='ill'>Project revenue ILLUSTRATIVE</th>" +
    "<th class='ill'>NOCO profit ILLUSTRATIVE</th></tr>";
  const revenueNote = knownRevenue.length
    ? `${knownRevenue.length} of ${prospects.length} prospects have an illustrative revenue`
    : "No installed cost is set, so revenue and profit show 'needs cost'";
  const body = `
<h1>NOCO prospect list: wall insulation, Buffalo</h1>
${demoLegend(a.cost_per_sqft, a.margin_pct, knownRevenue.length > 0 || knownProfit.length > 0)}
<div class="muted">Ranked by energy cost saved per year. Green columns are NOCO's calculator
outputs; orange columns are ILLUSTRATIVE.</div>
<div class="cards">${cards}</div>
<h2>Ranked prospects</h2>
<table class="wide">${header}${prospects.map(managerRow).join("")}</table>
<h2>Assumptions</h2>
<div class="muted">As used by the calculator for these prospects, with the source of each.</div>
<table><tr><th>Assumption</th><th>Source</th><th>Applies to</th></tr>
${assumptionRows(prospects, a)}</table>
<h2>Data limits</h2>
<ul>
<li>NOCO revenue and profit are ILLUSTRATIVE: ${escape(revenueNote)}. Margin guidance from
NOCO is 30 to 40%; installed cost per sq ft is not yet provided.</li>
<li>Footprints and floors come from OpenStreetMap; building type and story height from the
City of Buffalo assessment roll. "Match" is the confidence of that OSM ↔ roll join.</li>
<li>The customer's current energy supplier is not public data: ask the customer.</li>
<li>Buffalo HDD and CDD and the heating and cooling realization factors come from NOCO's own
calculator workbook (v5), shown as "NOCO calculator (v5)". Building-specific inputs (operating
profile, heating system, DAC status) are assumptions until confirmed with the customer.</li>
</ul>
<footer>Building data: ${escape(OSM_ATTRIBUTION)} (ODbL); City of Buffalo assessment roll;
US Census geocoder. Internal NOCO document.</footer>
`;
  return page("NOCO prospect list", body, MANAGER_CSS);
}

export const CSV_COLUMNS = [
  "rank", "address", "neighborhood", "use_class", "floors", "footprint_sqft", "perimeter_ft",
  "join_confidence", "insulated_wall_area_sqft", "heating_kwh", "heating_therms", "cooling_kwh",
  "total_kwh", "site_mmbtu", "annual_cost_savings_usd", "incentive_usd",
  "ten_year_energy_value_usd", "project_cost_usd", "net_investment_usd", "simple_payback_years",
  "project_revenue_usd_illustrative", "estimated_profit_usd_illustrative",
  "margin_pct_illustrative", "utility", "incentive_program", "current_supplier", "osm_id", "flags",
];

/** Neutralise spreadsheet formulas (CSV injection) in free-text cells. */
export function csvCell(text) {
  return ["=", "+", "-", "@", "\t", "\r"].includes(text.slice(0, 1)) ? `'${text}` : text;
}

// Value kinds matter for Python's csv: ints print as-is, floats as repr(round(v, 2)).
const INT = (v) => ({ kind: "int", v });
const FLOAT = (v) => ({ kind: "float", v });
const STR = (v) => ({ kind: "str", v });

function csvValue(item) {
  const { kind, v } = item;
  if (v === null || v === undefined) return "";
  if (kind === "float") return floatRepr(pyRound(v, 2));
  if (kind === "str") return csvCell(v);
  return String(v);
}

function csvQuote(field) {
  return /[",\n\r]/.test(field) ? `"${field.replace(/"/g, '""')}"` : field;
}

/** One row per prospect; empty cells for unknown values; NOCO money suffixed _illustrative. */
export function prospectsToCsv(prospects) {
  const lines = [CSV_COLUMNS.join(",")];
  for (const p of prospects) {
    const f = p.facts;
    const r = p.result;
    const o = p.opportunity;
    const join = (f.sources || {}).join;
    const values = [
      INT(p.rank), STR(f.address), STR(f.neighborhood), STR(f.use_class), INT(f.floors),
      FLOAT(f.footprint_sqft), FLOAT(f.perimeter_ft), FLOAT(join ? join.confidence : null),
      FLOAT(r.insulated_wall_area_sqft), FLOAT(r.heating_kwh), FLOAT(r.heating_therms),
      FLOAT(r.cooling_kwh), FLOAT(r.total_kwh), FLOAT(r.site_mmbtu),
      FLOAT(r.annual_cost_savings), FLOAT(r.incentive), FLOAT(r.ten_year_energy_value),
      FLOAT(r.project_cost), FLOAT(r.net_investment), FLOAT(r.simple_payback_years),
      FLOAT(o.project_revenue), FLOAT(o.estimated_profit), FLOAT(o.margin_pct),
      STR(o.utility), STR(o.incentive_program), STR(o.current_supplier), INT(f.osm_id),
      STR(r.flags.join("; ")),
    ];
    lines.push(values.map(csvValue).map(csvQuote).join(","));
  }
  return lines.join("\n") + "\n";
}
