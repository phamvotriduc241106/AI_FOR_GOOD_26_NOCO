# NOCO Scout — web edition (HTML, CSS, JavaScript)

Experimental branch `experiment/web-js`: the whole NOCO Scout demo rebuilt as a static web app,
with a new layout. No build step, no npm packages at runtime, no Python needed to run it.

```bash
make web          # serves the repo at http://localhost:8600 ; open http://localhost:8600/web/
make web-test     # Python reference -> Node parity tests (also part of `make test`)
```

Any static server works, as long as it serves the repo root (the app reads
`data/public/demo_buildings.json` and `docs/pitch/assets/noco_logo.png` from there).

## Pages

| Route | Streamlit page it replaces | What changed in the layout |
|---|---|---|
| `#/` Home | `app/NOCO_Scout.py` | Hero with live district totals computed by the calculator, two feature cards, 3 steps |
| `#/quote` Address to Quote | `pages/1_Address_to_Quote.py` | Search bar with address suggestions, map + facts side by side, facts as source chips with confidence bars, KPI cards |
| `#/map` Prospect Map | `pages/2_Prospect_Map.py` | Full-screen map, floating filter panel, slide-in details drawer, colour legend, ranked table below with exports; the map frames the buildings between the panels |
| `#/notes` AI site notes | `streamlit_app.py` (T11 feature) | Input and results side by side |

Behaviour kept from the Streamlit app: DEMO cost ($8/sq ft) and margin (35%) on by default and
shown in red; the estimate appears after "Estimate insulation upgrade"; buildings stay one
colour until "Show potential customers"; exact house-number address matching (T14); customer
report never shows NOCO revenue, profit or margin; manager report + CSV with ILLUSTRATIVE labels;
`© OpenStreetMap contributors` everywhere the map or data appears.

URL options: `?offline=1` (like `NOCO_OFFLINE=1`: no basemap), `?map=svg` (force the
dependency-free 2D map, e.g. on a projector without WebGL).

## Code

| JavaScript (`web/js/`) | Ported from |
|---|---|
| `contract.js` | `contract.py` — Assumptions also remember explicitly set fields (`model_fields_set`) |
| `calc.js` | `calc.py` — NOCO v5 calculator, operating profiles, incentive tiers and caps |
| `prospect.js` | `prospect.py` — illustrative opportunity, ranking |
| `geo.js` | `geo.py` — offline address normalisation and matching |
| `mapdata.js` | `mapdata.py` — tooltips, elevation, colours |
| `report.js` | `report.py` — customer report, manager report, CSV (same HTML, byte for byte) |
| `sitenotes.js` | `noco_scout/__init__.py` + hackkit pipeline/export — site-note checks |
| `pyfmt.js` | Python number formatting (`:g`, `:,.0f`, half-even rounding, float `repr`), `html.escape` |
| `map.js`, `app.js` | New: deck.gl/MapLibre map with an SVG fallback; router and pages |

## Proof that the port is faithful

`web/tools/export_parity.py` runs the Python implementation and writes reference outputs;
`web/tests/parity.test.mjs` runs the JavaScript on the same inputs and requires exact equality:
13 assumption scenarios × 305 buildings (inputs, results, opportunity), full ranking order, map
rows, manager and customer reports and CSV character for character, address matching, and
site-note validation. `tests/test_web_parity.py` wires this into `make test` (skipped if Node is
missing). A mutation check (changing one constant, one word of a report, one regex) makes the
tests fail.

## Limits (by design, browser-only)

- **Live address lookup**: the US Census geocoder does not allow browser (CORS) requests, so the
  web app looks addresses up in the saved 300-building Buffalo set, like the Streamlit app in
  offline mode. The Python `geo.py` connector and `scripts/prefetch_noco_data.py` still build
  that data set.
- **AI site notes**: an API key cannot be kept secret in a browser, so the page replays the
  feature's saved sample response (the fake provider, like `make demo`) and runs the same
  deterministic checks. A real model needs a small server-side proxy.
- **Map libraries** load from a CDN (deck.gl 9.1, MapLibre 4.7, CARTO basemap). Without network
  the app falls back to its own SVG map; everything else works offline.
