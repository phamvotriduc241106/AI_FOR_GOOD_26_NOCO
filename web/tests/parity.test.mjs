// Parity tests: the JavaScript port must reproduce the Python reference exactly.
// Run: python web/tools/export_parity.py /tmp/parity.json && PARITY_JSON=/tmp/parity.json node --test web/tests/
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { estimateInsulation, inputsFromFacts } from "../js/calc.js";
import { makeAssumptions } from "../js/contract.js";
import { matchAddress, normalizeAddress, streetKey } from "../js/geo.js";
import { prospectsToDeckRows } from "../js/mapdata.js";
import { buildOpportunity, rankProspects } from "../js/prospect.js";
import {
  prospectsToCsv, renderCustomerReport, renderManagerReport, reportContext, splitAssumption,
} from "../js/report.js";
import { runFeature } from "../js/sitenotes.js";

const path = process.env.PARITY_JSON;
if (!path) throw new Error("Set PARITY_JSON to the file written by web/tools/export_parity.py");
const ref = JSON.parse(readFileSync(path, "utf-8"));

const [year, month, day] = ref.fixed_date.split("-").map(Number);
reportContext.logoDataUrl = ref.logo_data_url;
reportContext.today = () => new Date(year, month - 1, day);

const nullify = (obj) => Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, v ?? null]));
const assumptionsFor = (name) => makeAssumptions(nullify(ref.scenarios[name]));
const demo = ref.buildings.slice(0, ref.buildings.length - 5);
const plain = (obj) => JSON.parse(JSON.stringify(obj));

/** Exact string equality with a short context around the first difference. */
function sameText(actual, expected, label) {
  if (actual === expected) return;
  let i = 0;
  while (i < actual.length && actual[i] === expected[i]) i++;
  const ctx = (s) => JSON.stringify(s.slice(Math.max(0, i - 60), i + 60));
  assert.fail(`${label}: first difference at char ${i}\n  js: ${ctx(actual)}\n  py: ${ctx(expected)}`);
}

for (const name of Object.keys(ref.scenarios)) {
  test(`calculator, inputs and opportunity match Python: scenario "${name}"`, () => {
    const a = assumptionsFor(name);
    ref.buildings.forEach((facts, index) => {
      const expected = ref.calc[name][index];
      const inputs = inputsFromFacts(facts, a);
      assert.deepEqual(plain(inputs), expected.inputs, `${name} #${index} inputs (${facts.address})`);
      const result = estimateInsulation(inputs);
      assert.deepEqual(plain(result), expected.result, `${name} #${index} result (${facts.address})`);
      const opportunity = buildOpportunity(facts, result, a);
      assert.deepEqual(plain(opportunity), expected.opportunity, `${name} #${index} opportunity`);
    });
  });
}

for (const name of Object.keys(ref.ranking)) {
  test(`ranking, map rows and exports match Python: scenario "${name}"`, () => {
    const a = assumptionsFor(name);
    const ranked = rankProspects(demo, a, demo.length);
    assert.deepEqual(
      ranked.map((p) => [p.rank, p.facts.address, p.score]),
      ref.ranking[name],
      "ranking order",
    );
    const top = ranked.slice(0, 25);
    assert.deepEqual(plain(prospectsToDeckRows(top)), ref.deck[name].top25, "deck rows top 25");
    assert.deepEqual(plain(prospectsToDeckRows(ranked)), ref.deck[name].all, "deck rows, all");
    const r = ref.reports[name];
    sameText(renderManagerReport(top, a), r.manager_top25, `${name} manager report`);
    sameText(prospectsToCsv(top), r.csv_top25, `${name} CSV top 25`);
    sameText(prospectsToCsv(ranked), r.csv_all, `${name} CSV all`);
    [ranked[0], ranked[7], ranked[150], ranked.at(-1)].forEach((p, i) => {
      sameText(
        renderCustomerReport(p.facts, p.inputs, p.result, p.opportunity),
        r.customer[i],
        `${name} customer report ${i} (${p.facts.address})`,
      );
    });
    const p3 = ranked[3];
    sameText(renderCustomerReport(p3.facts, p3.inputs, p3.result), r.customer_no_opportunity, "no opportunity");
  });
}

test("empty and synthetic exports match Python", () => {
  const a = makeAssumptions();
  sameText(renderManagerReport([], a), ref.reports.empty.manager, "empty manager report");
  sameText(prospectsToCsv([]), ref.reports.empty.csv, "empty CSV");
  const cost = makeAssumptions({ cost_per_sqft: 8.0 });
  const samples = ref.buildings.slice(-5);
  const ranked = rankProspects(samples, cost, 5);
  sameText(renderManagerReport(ranked, cost), ref.reports.synthetic.manager, "synthetic manager");
  sameText(prospectsToCsv(ranked), ref.reports.synthetic.csv, "synthetic CSV");
  assert.deepEqual(plain(prospectsToDeckRows(ranked)), ref.reports.synthetic.deck, "synthetic deck");
});

test("assumption lines split into text and source like Python", () => {
  for (const [line, expected] of Object.entries(ref.split_assumption)) {
    assert.deepEqual(splitAssumption(line), expected, line);
  }
});

test("address normalisation and matching match Python (exact house numbers)", () => {
  for (const [query, expected] of Object.entries(ref.addresses)) {
    assert.equal(normalizeAddress(query), expected.normalized, `normalize ${query}`);
    assert.equal(streetKey(query), expected.street_key, `street key ${query}`);
    const match = matchAddress(query, demo);
    assert.equal(match ? match.address : null, expected.match, `match ${query}`);
  }
});

test("site-note validation, rules and review flags match Python", () => {
  for (const expected of ref.site_notes) {
    const result = runFeature("", () => JSON.stringify(expected.raw));
    assert.equal(result.ok, expected.ok, `ok for ${JSON.stringify(expected.raw)}`);
    if (!expected.ok) continue;
    assert.deepEqual(result.rules.metrics, expected.metrics);
    assert.equal(result.rules.summary, expected.summary);
    assert.deepEqual(result.flags, expected.flags);
  }
});
