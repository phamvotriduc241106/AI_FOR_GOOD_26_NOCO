// Source-labelled building rows for the Buffalo 3D map (port of mapdata.py).

import { OSM_ATTRIBUTION } from "./contract.js";
import { comma0, escapeHtml, pyRoundInt } from "./pyfmt.js";

export const FT_TO_M = 0.3048;

function source(facts, field) {
  const src = (facts.sources || {})[field];
  return src ? escapeHtml(src.source) : "source not recorded";
}

const money = (value, missing) => (value !== null && value !== undefined ? `$${comma0(value)}` : missing);

/** Escape dynamic text before it enters the fixed HTML tooltip template. */
export function tooltipLines(p) {
  const f = p.facts;
  const r = p.result;
  const floors = f.floors !== null && f.floors !== undefined ? String(f.floors) : "unknown";
  const sample = Object.values(f.sources || {}).some((s) => (s.note || "").toLowerCase().includes("synthetic"))
    ? "SYNTHETIC SAMPLE · "
    : "";
  return [
    escapeHtml(f.address),
    `Use: ${escapeHtml(f.use_class || "unknown")} [${source(f, "use_class")}]`,
    `Floors: ${floors} [${source(f, "floors")}]`,
    `Savings/year: ${money(r.annual_cost_savings, "unavailable")} [NOCO calc]`,
    `Incentive: ${money(r.incentive, "unavailable")} [NOCO calc]`,
    `${sample}${OSM_ATTRIBUTION}`,
  ];
}

/** Fixed tooltip order with escaped public data and explicit sources. */
export function prospectTooltipHtml(p) {
  const lines = tooltipLines(p);
  return `<strong>${lines[0]}</strong><br/>` + lines.slice(1).join("<br/>");
}

export function polygonOf(facts) {
  const geojson = facts.footprint_geojson;
  if (!geojson || typeof geojson !== "object" || geojson.type !== "Polygon") return null;
  const coordinates = geojson.coordinates;
  if (!Array.isArray(coordinates) || !coordinates.length) return null;
  const ring = coordinates[0];
  if (!Array.isArray(ring) || ring.length < 3) return null;
  const polygon = [];
  for (const pair of ring) {
    if (!Array.isArray(pair) || pair.length < 2) return null;
    const lon = Number(pair[0]);
    const lat = Number(pair[1]);
    if (!Number.isFinite(lon) || !Number.isFinite(lat)) return null;
    polygon.push([lon, lat]);
  }
  return polygon;
}

/** Ranked prospects -> PolygonLayer rows; footprints missing a polygon are omitted. */
export function prospectsToDeckRows(prospects) {
  const positive = prospects.map((p) => p.score).filter((s) => Number.isFinite(s) && s > 0);
  const maximum = positive.length ? Math.max(...positive) : 0.0;
  const rows = [];
  prospects.forEach((prospect, index) => {
    const polygon = polygonOf(prospect.facts);
    if (polygon === null) return;
    const facts = prospect.facts;
    let strength = 0.0;
    if (maximum && Number.isFinite(prospect.score)) strength = Math.max(0.0, prospect.score) / maximum;
    const floors = facts.floors !== null && facts.floors !== undefined && facts.floors > 0 ? facts.floors : 1;
    const floorHeight =
      facts.floor_height_ft !== null && facts.floor_height_ft !== undefined && facts.floor_height_ft > 0
        ? facts.floor_height_ft
        : 12.0;
    const lines = tooltipLines(prospect);
    const row = {
      polygon,
      elevation: floors * floorHeight * FT_TO_M,
      color: [
        pyRoundInt(48 + 207 * strength),
        pyRoundInt(146 - 26 * strength),
        pyRoundInt(208 - 154 * strength),
        210,
      ],
      tooltip_html: prospectTooltipHtml(prospect),
      address: facts.address,
      prospect_index: index,
    };
    lines.forEach((line, i) => {
      row[`tooltip_${i}`] = line;
    });
    rows.push(row);
  });
  return rows;
}
