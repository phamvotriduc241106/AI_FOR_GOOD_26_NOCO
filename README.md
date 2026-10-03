# NOCO Scout

**From an address to a customer-ready quote in seconds.**

Team **HELIX** · UB *AI for Good* Hackathon · NOCO challenge · Buffalo, NY

NOCO Scout helps a NOCO energy sales team quote commercial wall-insulation upgrades without a site
visit first. Type a Buffalo address: public data fills in the building facts, NOCO's own savings
calculator turns them into savings and incentives, and every number shows where it came from. The
same engine ranks hundreds of Buffalo buildings on a 3D map so a sales manager knows whom to call first.

---

## The problem

Today a NOCO rep visits the building, collects data, goes back to the office to research, and only
then writes a quote. Each quote needs one or two specialists, and most buildings in the city are
never quoted at all.

## What NOCO Scout does

| Page | For | What you get |
|---|---|---|
| **Home** | Everyone | What the tool does and where to click |
| **Address to Quote** | Sales rep | Address → 3D footprint → building facts with source and confidence → annual savings, incentive and payback → one-page **customer report** (HTML, print to PDF) |
| **Prospect Map** | Sales manager | **Show potential customers** ranks 300 Buffalo buildings on a 3D map (blue → orange = low → high savings); hover for sourced facts, click for details; filters; **manager report** and **CSV** |
| **AI site notes** | Rep in the field | An LLM reads a free-text site note or bill into structured fields. It never decides a number |

## How it works

```
Buffalo address
   │
   ├─► US Census Geocoder ............ address → coordinates
   ├─► OpenStreetMap (Overpass) ...... building outline → footprint, perimeter, floors
   ├─► City of Buffalo assessment roll building use, story height
   │
   ▼
BuildingFacts (every field: value + source + confidence)
   │
   ▼
Insulation calculator ─ rebuilt cell by cell from NOCO's "Commercial Insulation Savings Calculator v5"
   │   heating/cooling savings, kWh, MMBtu, $/year, National Grid incentive (fuel, ΔR and
   │   disadvantaged-community tiers, $150k electric / $250k gas caps), 10-year value
   ▼
Quote · ranked prospect map · customer report · manager report · CSV
```

- **The calculator is plain, tested Python.** It reproduces NOCO's own worked example, and its
  constants and incentive rules come from NOCO's workbook (labelled *NOCO calculator (v5)*).
- **GIS replaces the tape measure.** Perimeter, footprint and floors come from the real building
  outline instead of a site visit; when a value is missing the app says so instead of guessing.
- **The LLM only reads.** Extraction goes in; deterministic rules and numbers come out.

## Honesty rules (built into the app)

| Situation | What the app does |
|---|---|
| Any number on screen or in a report | Shows its source: OpenStreetMap, Buffalo assessment roll, Census geocoder, NOCO calculator (v5), Assumption, or DEMO value |
| NOCO has not provided installed cost or margin | Uses **DEMO values shown in red**: $8/sq ft (chosen by the team) and 35 % margin (middle of the 30–40 % NOCO mentioned). Turn the toggles off to see "Needs installed cost" |
| Heating system unknown | Assumes electric resistance (as in NOCO's example) and flags it: confirm with the customer |
| Current energy supplier | Not public data: "Not in public data: ask the customer". Never guessed |
| Customer report | Never shows NOCO's revenue, profit or margin |
| Privacy | Owner names and mailing addresses from the assessment roll are never requested, stored or shown |

## Quickstart

Requires Python 3.11+ (macOS or Linux).

```bash
git clone https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD.git && cd AI_FOR_GOOD
make setup                    # creates .venv, installs the project, copies .env.example to .env
source .venv/bin/activate     # in every new terminal

NOCO_OFFLINE=1 make run       # demo with no network: saved Buffalo buildings, no basemap
make run                      # with internet: street basemap and live lookup of other addresses
```

Open http://localhost:8501, then **Address to Quote** or **Prospect Map**.

Try these addresses: `33 Franklin St`, `110 Franklin St`, `1 Seneca St`, `532 Main St`,
`107 Delaware Ave`.

The **AI site notes** page needs an LLM provider in `.env` (`LLM_PROVIDER=anthropic`, `groq` or
`ollama`), or runs offline with `LLM_PROVIDER=fake` (`make demo`).

## Development

```bash
make test     # 894 tests, no network and no API key needed
make lint     # ruff check + format check (same as CI)
make eval     # LLM extraction accuracy on labelled cases (fake provider by default)
python scripts/prefetch_noco_data.py   # rebuild data/public/demo_buildings.json from public APIs
```

| Path | What it is |
|---|---|
| `app/NOCO_Scout.py` | App entry point: home page and navigation |
| `app/pages/` | Address to Quote, Prospect Map, shared map and styling helpers |
| `src/features/noco_scout/contract.py` | Shared data model (`BuildingFacts`, `Assumptions`, `CalcResult`, `Prospect`, ...) |
| `src/features/noco_scout/calc.py` | Deterministic insulation calculator (NOCO v5 formulas and incentive rules) |
| `src/features/noco_scout/geo.py` | Census, OpenStreetMap and Buffalo roll connectors, offline address lookup |
| `src/features/noco_scout/prospect.py` | Prospect ranking and illustrative NOCO opportunity |
| `src/features/noco_scout/mapdata.py` | 3D map rows and tooltips |
| `src/features/noco_scout/report.py` | Customer report, manager report, CSV |
| `src/features/noco_scout/__init__.py` | AI site-note extraction feature |
| `data/public/` | 300 Buffalo buildings in 11 neighborhoods, with sources and licences |
| `src/hackkit/` | Underlying framework: LLM providers, validation retry, cache, evals |
| `docs/` | Spec, data notes, task board, pitch material |

## Data sources and licences

| Data | Source | Terms |
|---|---|---|
| Building outlines, levels | OpenStreetMap via Overpass API | © OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/) |
| Building use, story height | City of Buffalo Final Assessment Roll (`data.buffalony.gov`, `4t8s-9yih`) | City of Buffalo Open Data |
| Address → coordinates | US Census Geocoder | Public domain |
| Calculator formulas, constants, incentive rules | NOCO Commercial Insulation Savings Calculator v5 | Provided by NOCO for the hackathon |

See [data/public/README.md](data/public/README.md) for the data rules.

## Limitations and next steps

**Limitations today.**
- Buffalo only.
- One measure: wall insulation.
- Installed cost and margin are demo values until NOCO provides them.
- Landmarks that OpenStreetMap splits into several parts (for example City Hall) are not modelled
  yet.

**Next steps.**
- Windows, HVAC, lighting and rooftop solar.
- NYSERDA and National Fuel incentives.
- NYSERDA disadvantaged-community map layer.
- Utility-bill upload.
- NOCO CRM integration and a React front end.
- Every city NOCO serves.

## Team HELIX

| Member | Role |
|---|---|
| [Nguyen-Le-Tuan](https://github.com/Nguyen-Le-Tuan) | Integrator: workflow, code review and merges, QA, demo |
| [Anh-08](https://github.com/Anh-08) | Developer: GIS data pipeline, reports, UI |
| [phamvotriduc241106](https://github.com/phamvotriduc241106) | Developer: NOCO calculator, 3D map, prospect ranking, AI extraction |
| [NguyenQBao](https://github.com/NguyenQBao) | Research and NOCO liaison, pitch |

Built with Streamlit and pydeck on top of **hackkit**, the team's hackathon framework.
Map data © OpenStreetMap contributors. Code under the [MIT License](LICENSE).
