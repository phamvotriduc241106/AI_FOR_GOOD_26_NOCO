// NOCO Scout web app: hash router + four pages (Home, Address to Quote, Prospect Map, AI site notes).
// All numbers come from the ported modules (calc/prospect/report), which are parity-tested
// against the Python implementation.

import { OSM_ATTRIBUTION, makeAssumptions } from "./contract.js";
import { findBuilding, loadDemoBuildings } from "./geo.js";
import { BuildingMap, hasDeck, viewFor } from "./map.js";
import { prospectsToDeckRows } from "./mapdata.js";
import { makeProspect, rankProspects } from "./prospect.js";
import { cmpStr, comma0, escapeHtml as esc, fixed, g, percent0 } from "./pyfmt.js";
import { prospectsToCsv, renderCustomerReport, renderManagerReport, reportContext } from "./report.js";
import * as notes from "./sitenotes.js";

const DEMO_COST_PER_SQFT = 8.0; // Demo chosen by team HELIX, NOT a NOCO price.
const DEMO_MARGIN_PCT = 0.35; // Midpoint of the 30–40% NOCO mentioned verbally.
const DEMO_NOTE = "Red = DEMO value for illustration, not from NOCO or public data.";
const OFFLINE = new URLSearchParams(location.search).get("offline") === "1";
const DATA_URL = "../data/public/demo_buildings.json";
const SAMPLE_URL = "data/sample_buildings.json";
const LOGO_URL = "../docs/pitch/assets/noco_logo.png";

const app = document.getElementById("app");
const state = {
  buildings: [],
  synthetic: false,
  quote: { query: "", facts: null, missing: false, estimated: false, useCost: true, cost: DEMO_COST_PER_SQFT },
  map: {
    use: "All", minSavings: 0, top: 25, useCost: true, cost: DEMO_COST_PER_SQFT,
    useMargin: true, margin: DEMO_MARGIN_PCT, showPotential: false, selected: 0, drawerOpen: true,
  },
  notes: { text: notes.SAMPLE_TEXT, result: null },
};
let activeMap = null;

// ---------------------------------------------------------------- helpers
const $ = (sel, root = document) => root.querySelector(sel);
const money = (v) => (v === null || v === undefined ? "—" : `$${comma0(v)}`);
const icon = {
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
  map: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/></svg>',
  doc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/></svg>',
  down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>',
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18"/></svg>',
};

function download(filename, text, mime) {
  const url = URL.createObjectURL(new Blob([text], { type: mime }));
  const a = Object.assign(document.createElement("a"), { href: url, download: filename });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function openReport(html) {
  const url = URL.createObjectURL(new Blob([html], { type: "text/html" }));
  window.open(url, "_blank", "noopener");
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

function stat(label, value, src, demo = false) {
  return `<div class="stat${demo ? " demo" : ""}"><div class="label">${esc(label)}</div>` +
    `<div class="value">${esc(value)}</div>${src ? `<div class="src">${esc(src)}</div>` : ""}</div>`;
}

function dataAlerts(where) {
  let html = "";
  if (state.synthetic) {
    html += `<div class="alert warn">SYNTHETIC SAMPLE: five made-up Buffalo buildings. Public data has not landed yet.</div>`;
  }
  if (OFFLINE) {
    html += `<div class="alert info">${where === "map"
      ? "Offline mode: no network lookup and no basemap. Building polygons remain interactive."
      : "Offline mode: address search uses saved buildings only; the map has no basemap."}</div>`;
  }
  return html;
}

/** fact_rows(): each visible fact beside its own source and confidence. */
function factRows(facts) {
  const fields = [
    ["address", "Address", facts.address],
    ["use_class", "Building use", facts.use_class || "unknown"],
    ["footprint_sqft", "Footprint", facts.footprint_sqft != null ? `${comma0(facts.footprint_sqft)} sq ft` : "unknown"],
    ["perimeter_ft", "Perimeter", facts.perimeter_ft != null ? `${comma0(facts.perimeter_ft)} ft` : "unknown"],
    ["floors", "Floors", facts.floors != null ? String(facts.floors) : "unknown"],
    ["floor_height_ft", "Floor height", facts.floor_height_ft != null ? `${g(facts.floor_height_ft)} ft` : "unknown"],
  ];
  return fields.map(([field, label, value]) => {
    const src = (facts.sources || {})[field];
    const conf = src ? src.confidence : 0;
    return `<div class="fact"><div class="k">${esc(label)}</div><div class="v">${esc(value)}</div>` +
      `<div class="s">${src
        ? `<span class="tag${src.source === "assumed" ? " assumed" : ""}">${esc(src.source)}</span>` +
          `<span class="conf" title="confidence ${fixed(conf, 2)}"><i style="width:${Math.round(conf * 100)}%"></i></span>` +
          `<span>${fixed(conf, 2)}${src.note ? ` · ${esc(src.note)}` : ""}</span>`
        : "<span>not recorded</span>"}</div></div>`;
  }).join("");
}

/** show_estimate(): savings, incentive, payback, flags and the calculator's assumptions. */
function estimateHtml(p) {
  const r = p.result;
  const hasCost = r.project_cost !== null;
  let html = `<div class="grid cols-3">` +
    stat("Annual savings", `$${comma0(r.annual_cost_savings)}`, "NOCO model + GIS") +
    stat("Incentive", `$${comma0(r.incentive)}`, "NOCO sheet") +
    stat(hasCost ? "Payback · ILLUSTRATIVE cost · DEMO value" : "Payback · ILLUSTRATIVE cost",
      r.simple_payback_years !== null ? `${fixed(r.simple_payback_years, 1)} years` : "Needs installed cost",
      hasCost ? "DEMO value" : "needs a NOCO installed-cost quote", hasCost) +
    `</div>`;
  if (hasCost) {
    html += `<p class="demo-text small">Project cost: $${comma0(r.project_cost)} · DEMO / ILLUSTRATIVE installed cost × NOCO wall area</p>`;
  }
  html += `<p class="faint">Reference model reproduces NOCO's example using sheet-confirmed HDD/CDD; ` +
    `site conditions and incentive eligibility still require verification.</p>`;
  html += `<div class="stack">${r.flags.map((f) => `<div class="alert warn">${esc(f)}</div>`).join("")}</div>`;
  html += `<details class="accordion"><summary>Calculation sources and assumptions</summary><ul>` +
    r.assumptions.map((a) => `<li>${esc(a)}</li>`).join("") + `</ul></details>`;
  return html;
}

function reportButtons(prefix) {
  return `<div style="display:flex;gap:10px;flex-wrap:wrap">` +
    `<button class="btn primary" id="${prefix}-report">${icon.doc} Generate customer report</button>` +
    `<button class="btn" id="${prefix}-report-dl">${icon.down} Download (.html)</button></div>`;
}

function bindReportButtons(prefix, p) {
  const html = () => renderCustomerReport(p.facts, p.inputs, p.result, p.opportunity);
  $(`#${prefix}-report`).onclick = () => openReport(html());
  $(`#${prefix}-report-dl`).onclick = () => download("noco-customer-report.html", html(), "text/html");
}

// ---------------------------------------------------------------- Home
function renderHome() {
  const ranked = state.buildings.length ? rankProspects(state.buildings, makeAssumptions(), state.buildings.length) : [];
  const savings = ranked.reduce((s, p) => s + p.result.annual_cost_savings, 0);
  const incentives = ranked.reduce((s, p) => s + p.result.incentive, 0);
  const hoods = new Set(state.buildings.map((b) => b.neighborhood).filter(Boolean)).size;
  const steps = [
    ["1", "Type a Buffalo address", "or open the prospect map of the whole district."],
    ["2", "Check the building facts", "footprint, perimeter, floors and use, each with its public source and confidence."],
    ["3", "Get the estimate and report", "savings, incentive and payback from NOCO's own calculator, then download the customer or manager report."],
  ];
  app.innerHTML = `<section class="page">
    ${dataAlerts("home")}
    <div class="hero">
      <div>
        <div class="hero-logo"><img src="${LOGO_URL}" alt="NOCO"><div class="eyebrow">Buffalo, NY · commercial wall insulation</div></div>
        <h1>From an address to a <span>customer-ready quote</span> in seconds.</h1>
        <p class="lede">Public building data + NOCO's own savings calculator. Every number shows its source, and the math reproduces NOCO's spreadsheet.</p>
        <div class="cta">
          <a class="btn primary" href="#/quote">${icon.search} Open Address to Quote</a>
          <a class="btn" href="#/map">${icon.map} Open Prospect Map</a>
        </div>
      </div>
      <div class="grid cols-2">
        ${stat("Buffalo buildings ready", comma0(state.buildings.length), "saved public data")}
        ${stat("Neighborhoods", comma0(hoods), "City of Buffalo assessment roll")}
        ${stat("Energy savings potential / yr", money(savings), "NOCO calculator + GIS")}
        ${stat("Incentives available", money(incentives), "National Grid schedule, capped")}
      </div>
    </div>
    <div class="grid cols-2">
      <div class="card feature">
        <div class="icon">${icon.search}</div>
        <h2>Address to Quote</h2>
        <p>One building: type an address, see its 3D footprint and sourced facts, then estimate savings, incentive and payback and download a one-page customer report.</p>
        <div><a class="btn primary small" href="#/quote">Open Address to Quote</a></div>
      </div>
      <div class="card feature">
        <div class="icon">${icon.map}</div>
        <h2>Prospect Map</h2>
        <p>The whole district: rank hundreds of Buffalo buildings by savings on a 3D map, hover for sources, click for details, export the manager report and CSV.</p>
        <div><a class="btn primary small" href="#/map">Open Prospect Map</a></div>
      </div>
    </div>
    <div class="section-title"><h2>How it works</h2></div>
    <div class="grid cols-3">${steps.map(([n, t, d]) => `<div class="step"><b>${n}</b><strong>${esc(t)}</strong><p>${esc(d)}</p></div>`).join("")}</div>
    <div class="footer attribution">${esc(OSM_ATTRIBUTION)} · City of Buffalo assessment roll · US Census geocoder · Estimates, not quotes: a NOCO site visit confirms them.</div>
  </section>`;
}

// ---------------------------------------------------------------- Address to Quote
function quoteProspect() {
  const q = state.quote;
  return makeProspect(q.facts, makeAssumptions({ cost_per_sqft: q.useCost ? q.cost : null }));
}

function renderQuote() {
  const q = state.quote;
  if (!q.facts && !q.missing) q.facts = state.buildings[0] || null;
  if (!q.query) q.query = state.buildings[0] ? state.buildings[0].address : "";
  const options = state.buildings.map((b) => `<option value="${esc(b.address)}">`).join("");
  let body = "";
  if (q.missing) {
    body = `<div class="alert warn">Address not found in the saved Buffalo buildings. Try a listed address.</div>`;
  } else if (!q.facts) {
    body = `<div class="alert error">No building is available to estimate.</div>`;
  } else {
    body = `
      <p class="demo-text small">${esc(DEMO_NOTE)}</p>
      <div class="grid split">
        <div class="card flush">
          <div class="card-head"><h2>Building footprint in 3D</h2><span class="chip">${hasDeck() ? "3D · hover for sources" : "2D offline map"}</span></div>
          <div class="map" id="quote-map" style="border-radius:0"></div>
          <div style="padding:10px 20px" class="faint">3D height uses sourced floors and floor height. Hover for sources.</div>
        </div>
        <div class="card flush">
          <div class="card-head"><h2>Facts and confidence</h2><span class="faint">public sources</span></div>
          <div class="facts">${factRows(q.facts)}</div>
          <div style="padding:10px 20px" class="attribution">${esc(OSM_ATTRIBUTION)}</div>
        </div>
      </div>
      <div id="quote-estimate" style="margin-top:22px"></div>`;
  }
  app.innerHTML = `<section class="page">
    <div class="page-head"><div>
      <div class="eyebrow">Buffalo, NY · public building facts → deterministic insulation estimate</div>
      <h1>Address to Quote</h1>
      <p class="lede">Type a Buffalo address. We fill the calculator's inputs from GIS instead of a site visit.</p>
    </div></div>
    <div class="stack">${dataAlerts("quote")}</div>
    <div class="card" style="margin:14px 0 18px">
      <form class="search" id="quote-form">
        <input class="input" id="quote-address" list="quote-addresses" value="${esc(q.query)}" placeholder="e.g. 110 Franklin St" aria-label="Buffalo building address" autocomplete="off">
        <datalist id="quote-addresses">${options}</datalist>
        <button class="btn primary" type="submit">${icon.search} Find building</button>
      </form>
      <div class="toolbar" style="padding:14px 0 0">
        <label class="switch"><input type="checkbox" id="quote-use-cost" ${q.useCost ? "checked" : ""}> Enter an ILLUSTRATIVE installed cost</label>
        <label class="field" style="width:280px" ${q.useCost ? "" : "hidden"} id="quote-cost-field">
          <span class="demo-text">Installed cost per insulated wall sq ft (USD) · DEMO</span>
          <input class="input demo" type="number" min="0" step="0.5" id="quote-cost" value="${q.cost}">
        </label>
      </div>
    </div>
    ${body}
  </section>`;

  $("#quote-form").onsubmit = (e) => {
    e.preventDefault();
    q.query = $("#quote-address").value;
    const found = findBuilding(q.query, state.buildings);
    q.missing = found === null;
    q.facts = found;
    q.estimated = false;
    renderQuote();
  };
  const costChanged = () => {
    q.useCost = $("#quote-use-cost").checked;
    q.cost = Math.max(0, Number($("#quote-cost").value) || 0);
    $("#quote-cost-field").hidden = !q.useCost;
    if (q.facts) renderQuoteEstimate();
  };
  $("#quote-use-cost").onchange = costChanged;
  $("#quote-cost").oninput = costChanged;
  if (!q.facts) return;

  const p = quoteProspect();
  activeMap = new BuildingMap($("#quote-map"), { offline: OFFLINE });
  activeMap.update(prospectsToDeckRows([p]), viewFor([p], [q.facts.lat, q.facts.lon]));
  renderQuoteEstimate();
}

function renderQuoteEstimate() {
  const q = state.quote;
  const box = $("#quote-estimate");
  if (!box) return;
  if (!q.estimated) {
    box.innerHTML = `<button class="btn primary" id="quote-estimate-btn">Estimate insulation upgrade</button>`;
    $("#quote-estimate-btn").onclick = () => {
      q.estimated = true;
      renderQuoteEstimate();
    };
    return;
  }
  const p = quoteProspect();
  box.innerHTML = `<div class="card"><div class="stack">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
      <h2 style="margin:0">Insulation estimate</h2>${reportButtons("quote")}
    </div>
    ${estimateHtml(p)}
  </div></div>`;
  bindReportButtons("quote", p);
}

// ---------------------------------------------------------------- Prospect Map
function mapAssumptions() {
  const m = state.map;
  return makeAssumptions({
    cost_per_sqft: m.useCost ? m.cost : null,
    margin_pct: m.useMargin ? m.margin : null,
  });
}

function filteredProspects() {
  const m = state.map;
  const a = mapAssumptions();
  const ranked = rankProspects(state.buildings, a, state.buildings.length);
  const filtered = ranked
    .filter((p) => (m.use === "All" || p.facts.use_class === m.use) && p.result.annual_cost_savings >= m.minSavings)
    .slice(0, m.top);
  return { a, filtered };
}

function renderMap() {
  const m = state.map;
  if (!state.buildings.length) {
    app.innerHTML = `<section class="page"><div class="alert error">No saved Buffalo buildings are available.</div></section>`;
    return;
  }
  const useClasses = [...new Set(state.buildings.map((b) => b.use_class).filter(Boolean))].sort(cmpStr);
  m.top = Math.min(m.top, state.buildings.length);
  app.innerHTML = `
    <div class="explorer">
      <div class="map" id="pm-map"></div>
      <aside class="float-panel" aria-label="Filters">
        <div class="eyebrow">Buffalo, NY</div>
        <h1>Prospect Map</h1>
        <p class="muted small" style="margin:0 0 14px">Ranked insulation opportunities from saved public building data.</p>
        <div class="stack">
          ${dataAlerts("map")}
          <label class="field"><span>Building use</span>
            <select class="input" id="pm-use">${["All", ...useClasses].map((u) => `<option ${u === m.use ? "selected" : ""}>${esc(u)}</option>`).join("")}</select></label>
          <label class="field"><span>Minimum annual savings (USD)</span>
            <input class="input" type="number" min="0" step="500" id="pm-min" value="${m.minSavings}"></label>
          <label class="field"><span>Top buildings: <b id="pm-top-label">${m.top}</b></span>
            <input type="range" min="1" max="${state.buildings.length}" id="pm-top" value="${m.top}"></label>
          <details class="accordion"><summary>ILLUSTRATIVE NOCO cost and margin inputs</summary>
            <div class="stack" style="padding:0 14px 14px">
              <label class="switch"><input type="checkbox" id="pm-use-cost" ${m.useCost ? "checked" : ""}> Enter an illustrative installed cost</label>
              <label class="field" id="pm-cost-field" ${m.useCost ? "" : "hidden"}><span class="demo-text">Installed cost per insulated wall sq ft (USD) · DEMO</span>
                <input class="input demo" type="number" min="0" step="0.5" id="pm-cost" value="${m.cost}"></label>
              <label class="switch"><input type="checkbox" id="pm-use-margin" ${m.useMargin ? "checked" : ""}> Enter an illustrative NOCO margin</label>
              <label class="field" id="pm-margin-field" ${m.useMargin ? "" : "hidden"}><span class="demo-text">NOCO margin fraction · DEMO: <b id="pm-margin-label">${percent0(m.margin)}</b></span>
                <input type="range" class="demo" min="0" max="0.5" step="0.01" id="pm-margin" value="${m.margin}"></label>
            </div>
          </details>
          <button class="btn primary" id="pm-show">${icon.map} Show potential customers</button>
          <p class="demo-text small" style="margin:0">${esc(DEMO_NOTE)}</p>
          <div id="pm-summary"></div>
        </div>
      </aside>
      <aside class="drawer" id="pm-drawer" aria-label="Building details"></aside>
      <div class="legend" id="pm-legend">
        <div>Annual savings · NOCO calc</div><div class="bar"></div>
        <div class="ends"><span>lower</span><span>higher</span></div>
      </div>
      <div class="map-badge"><span class="chip">${hasDeck() ? "3D · hover for sources, click for details" : "2D offline map"} · ${esc(OSM_ATTRIBUTION)}</span></div>
    </div>
    <section class="page" id="pm-ranked"></section>`;

  activeMap = new BuildingMap($("#pm-map"), {
    offline: OFFLINE,
    onSelect: (index) => {
      m.selected = index;
      m.drawerOpen = true;
      updateMapPage(false);
    },
  });
  const rerank = () => {
    m.selected = 0;
    updateMapPage(true);
  };
  $("#pm-use").onchange = (e) => { m.use = e.target.value; rerank(); };
  $("#pm-min").oninput = (e) => { m.minSavings = Math.max(0, Number(e.target.value) || 0); rerank(); };
  $("#pm-top").oninput = (e) => { m.top = Number(e.target.value); $("#pm-top-label").textContent = m.top; rerank(); };
  $("#pm-use-cost").onchange = (e) => { m.useCost = e.target.checked; $("#pm-cost-field").hidden = !m.useCost; updateMapPage(true); };
  $("#pm-cost").oninput = (e) => { m.cost = Math.max(0, Number(e.target.value) || 0); updateMapPage(true); };
  $("#pm-use-margin").onchange = (e) => { m.useMargin = e.target.checked; $("#pm-margin-field").hidden = !m.useMargin; updateMapPage(true); };
  $("#pm-margin").oninput = (e) => { m.margin = Number(e.target.value); $("#pm-margin-label").textContent = percent0(m.margin); updateMapPage(true); };
  $("#pm-show").onclick = () => { m.showPotential = true; m.drawerOpen = true; updateMapPage(true); };
  updateMapPage(true);
}

function updateMapPage(redrawMap) {
  const m = state.map;
  const { a, filtered } = filteredProspects();
  if (redrawMap) {
    const wide = window.innerWidth > 1100;
    activeMap.update(
      prospectsToDeckRows(filtered),
      viewFor(filtered.length ? filtered : state.buildings.map((facts) => ({ facts }))),
      {
        ranked: m.showPotential,
        // Keep the buildings clear of the floating filter panel and the details drawer.
        padding: wide ? { top: 70, bottom: 70, left: 390, right: m.showPotential ? 470 : 60 } : 40,
      },
    );
  }
  $("#pm-legend").hidden = !m.showPotential;
  const total = filtered.reduce((s, p) => s + p.result.annual_cost_savings, 0);
  $("#pm-summary").innerHTML = m.showPotential && filtered.length
    ? `<div class="grid cols-2">${stat("Buildings shown", comma0(filtered.length), "filters above")}${stat("Savings / yr", money(total), "NOCO calc")}</div>`
    : "";

  const drawer = $("#pm-drawer");
  if (!m.showPotential) {
    drawer.classList.remove("open");
    $("#pm-ranked").innerHTML = `<div class="alert info">Click 'Show potential customers' to rank the saved Buffalo buildings.</div>`;
    return;
  }
  if (!filtered.length) {
    drawer.classList.remove("open");
    $("#pm-ranked").innerHTML = `<div class="alert info">No building matches these filters.</div>`;
    return;
  }
  if (m.selected >= filtered.length) m.selected = 0;
  const p = filtered[m.selected];
  activeMap.setSelected(m.selected);
  const o = p.opportunity;
  const revenue = o.project_revenue !== null ? `$${comma0(o.project_revenue)}` : "needs NOCO cost";
  const profit = o.estimated_profit !== null ? `$${comma0(o.estimated_profit)}` : "needs NOCO margin";
  drawer.classList.toggle("open", m.drawerOpen);
  drawer.innerHTML = `<div class="inner">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div class="eyebrow">Building details</div>
      <button class="btn ghost small" id="pm-close" aria-label="Close details">${icon.x}</button>
    </div>
    <label class="field"><span>Select a building</span>
      <select class="input" id="pm-select">${filtered.map((q, i) => `<option value="${i}" ${i === m.selected ? "selected" : ""}>#${q.rank} ${esc(q.facts.address)}</option>`).join("")}</select></label>
    <h2 style="margin:4px 0 0"><span class="rank">#${p.rank}</span> ${esc(p.facts.address)}</h2>
    <div class="facts">${factRows(p.facts)}</div>
    <div class="attribution">${esc(OSM_ATTRIBUTION)}</div>
    ${estimateHtml(p)}
    <div class="card" style="padding:14px">
      <h3>NOCO opportunity</h3>
      <p class="faint" style="margin:0 0 6px">Utility: ${esc(o.utility)} [noco_sheet] · Program: ${esc(o.incentive_program || "not confirmed")} [noco_sheet reference]</p>
      <p class="small" style="margin:0 0 6px">Current supplier: ${esc(o.current_supplier)}</p>
      <p class="small ${o.project_revenue !== null ? "demo-text" : ""}" style="margin:0">NOCO revenue (ILLUSTRATIVE${o.project_revenue !== null ? " / DEMO" : ""}): ${esc(revenue)}</p>
      <p class="small ${o.estimated_profit !== null ? "demo-text" : ""}" style="margin:0">NOCO profit (ILLUSTRATIVE${o.estimated_profit !== null ? " / DEMO" : ""}): ${esc(profit)}</p>
      ${o.margin_pct !== null ? `<p class="small demo-text" style="margin:0">NOCO margin (ILLUSTRATIVE / DEMO): ${percent0(o.margin_pct)}</p>` : ""}
    </div>
    ${reportButtons("pm")}
  </div>`;
  $("#pm-close").onclick = () => { m.drawerOpen = false; drawer.classList.remove("open"); };
  $("#pm-select").onchange = (e) => { m.selected = Number(e.target.value); m.drawerOpen = true; updateMapPage(false); };
  bindReportButtons("pm", p);

  const rows = filtered.map((q, i) => `<tr data-i="${i}" class="${i === m.selected ? "selected" : ""}">
      <td><span class="rank">${q.rank}</span></td><td>${esc(q.facts.address)}</td><td class="muted">${esc(q.facts.use_class || "unknown")}</td>
      <td class="n">$${comma0(q.result.annual_cost_savings)}</td><td class="n">$${comma0(q.result.incentive)}</td>
      <td class="n ${q.result.simple_payback_years !== null ? "demo-text" : ""}">${q.result.simple_payback_years !== null ? `${fixed(q.result.simple_payback_years, 1)} years` : "needs cost"}</td></tr>`).join("");
  $("#pm-ranked").innerHTML = `<div class="card flush">
      <div class="card-head"><h2>Ranked prospects</h2>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn small" id="pm-manager">${icon.doc} Manager report (HTML)</button>
          <button class="btn small" id="pm-csv">${icon.down} Prospect CSV</button>
        </div></div>
      <div class="table-wrap"><table class="data">
        <thead><tr><th>Rank · calculated</th><th>Address</th><th>Use · assessor/OSM</th><th>Annual savings · NOCO + GIS</th><th>Incentive · NOCO sheet</th><th>Payback · ILLUSTRATIVE cost</th></tr></thead>
        <tbody>${rows}</tbody></table></div></div>`;
  $("#pm-ranked tbody").onclick = (e) => {
    const tr = e.target.closest("tr");
    if (!tr) return;
    m.selected = Number(tr.dataset.i);
    m.drawerOpen = true;
    updateMapPage(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  $("#pm-manager").onclick = () => {
    const html = renderManagerReport(filtered, a);
    openReport(html);
    download("noco-manager-report.html", html, "text/html");
  };
  $("#pm-csv").onclick = () => download("noco-prospects.csv", prospectsToCsv(filtered), "text/csv");
}

// ---------------------------------------------------------------- AI site notes
function renderNotes() {
  const n = state.notes;
  app.innerHTML = `<section class="page">
    <div class="page-head"><div>
      <div class="eyebrow">AI site notes · stated facts only</div>
      <h1>${esc(notes.TITLE)}</h1>
      <p class="lede">${esc(notes.DESCRIPTION)}</p>
    </div></div>
    <div class="alert info" style="margin-bottom:18px">Offline replay: in the browser the model step replays the feature's saved sample response (the fake provider, like <code>make demo</code>), so no API key ever reaches the page. Numbers are never decided by the model: savings come from the calculator.</div>
    <div class="grid split">
      <div class="card stack">
        <h2>Input text</h2>
        <textarea class="input" id="notes-text">${esc(n.text)}</textarea>
        <div><button class="btn primary" id="notes-run">Run</button></div>
      </div>
      <div class="card stack" id="notes-result"><p class="muted">Run the feature to see the extracted facts and the review flags.</p></div>
    </div>
  </section>`;
  $("#notes-text").oninput = (e) => { n.text = e.target.value; };
  $("#notes-run").onclick = () => {
    n.result = notes.runFeature(n.text);
    renderNotesResult();
  };
  if (n.result) renderNotesResult();
}

function renderNotesResult() {
  const r = state.notes.result;
  const box = $("#notes-result");
  if (!r.ok) {
    box.innerHTML = `<div class="alert error">Could not extract data. ${esc(r.error || "")}</div>` +
      (r.rawText ? `<details class="accordion"><summary>Model output</summary><pre class="code">${esc(r.rawText)}</pre></details>` : "");
    return;
  }
  const d = r.data;
  const kv = notes.FACT_FIELDS.map((k) => `<div>${esc(k.replace(/_/g, " "))}</div><div>${d[k] === null ? '<span class="faint">not stated</span>' : esc(String(d[k]))}</div>`).join("");
  box.innerHTML = `
    <p class="faint" style="margin:0">From ${r.attempts} model call(s).</p>
    <h2 style="margin:0">${esc(r.rules.summary)}</h2>
    <div class="grid cols-2">${Object.entries(r.rules.metrics).map(([k, v]) => stat(k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()), String(v), "deterministic rules")).join("")}
      ${stat("Model confidence", fixed(d.confidence, 2), "self-reported")}</div>
    ${r.flags.length
      ? `<div class="stack"><strong>Needs human review</strong>${r.flags.map((f) => `<div class="alert warn">${esc(f.field)}: ${esc(f.reason)}</div>`).join("")}</div>`
      : `<div class="alert ok">Nothing flagged for review.</div>`}
    <div class="kv">${kv}</div>
    <details class="accordion"><summary>Extracted data (JSON)</summary><pre class="code">${esc(JSON.stringify(d, null, 2))}</pre></details>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <button class="btn small" id="notes-md">${icon.down} Download report (.md)</button>
      <button class="btn small" id="notes-json">${icon.down} Download data (.json)</button>
    </div>`;
  $("#notes-md").onclick = () => download("report.md", notes.toMarkdown(r), "text/markdown");
  $("#notes-json").onclick = () => download("result.json", notes.toJson(r), "application/json");
}

// ---------------------------------------------------------------- router + boot
const ROUTES = { "": renderHome, quote: renderQuote, map: renderMap, notes: renderNotes };

function route() {
  if (activeMap) {
    activeMap.destroy();
    activeMap = null;
  }
  const name = location.hash.replace(/^#\/?/, "").split("?")[0];
  const render = ROUTES[name] || renderHome;
  document.querySelectorAll(".nav a").forEach((a) => {
    a.classList.toggle("active", (a.dataset.route === "home" ? "" : a.dataset.route) === (ROUTES[name] ? name : ""));
  });
  const titles = { "": "NOCO Scout", quote: "Address to Quote · NOCO", map: "Prospect Map · NOCO", notes: "AI site notes · NOCO" };
  document.title = titles[ROUTES[name] ? name : ""];
  window.scrollTo(0, 0);
  render();
}

async function loadLogo() {
  try {
    const blob = await (await fetch(LOGO_URL)).blob();
    reportContext.logoDataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch {
    reportContext.logoDataUrl = null; // reports fall back to the "NOCO" wordmark
  }
}

async function boot() {
  app.innerHTML = `<section class="page"><p class="muted">Loading Buffalo buildings…</p></section>`;
  try {
    state.buildings = await loadDemoBuildings(DATA_URL);
  } catch {
    state.buildings = await loadDemoBuildings(SAMPLE_URL);
    state.synthetic = true;
  }
  await loadLogo();
  $("#status").innerHTML =
    `<span class="chip${state.synthetic ? " warn" : ""}"><span class="dot"></span>${comma0(state.buildings.length)} ${state.synthetic ? "synthetic sample" : "Buffalo buildings · saved public data"}</span>` +
    `<span class="chip"><span class="dot" style="background:${hasDeck() ? "var(--accent)" : "var(--warn)"}"></span>${hasDeck() ? (OFFLINE ? "3D map · no basemap" : "3D map · CARTO basemap") : "2D offline map"}</span>`;
  window.addEventListener("hashchange", route);
  route();
}

boot();
