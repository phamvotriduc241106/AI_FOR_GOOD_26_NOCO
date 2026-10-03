# Public data for the NOCO Buffalo demo

`demo_buildings.json` is the offline demo set: a JSON list of `BuildingFacts` (see
`src/features/noco_scout/contract.py`) for commercial buildings in Downtown, Allentown and
Elmwood, Buffalo NY. Rebuild it with `python scripts/prefetch_noco_data.py` (re-runnable; HTTP
responses are cached in `data/public/cache/`, which is git-ignored).

## Sources and licences

| Data | Source | Licence / terms |
|---|---|---|
| Footprints, building levels, OSM house numbers and street names | OpenStreetMap via Overpass API | © OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/). This file is a derived database and is shared under ODbL. |
| Property class, story height, property address, ZIP, neighbourhood, parcel point | City of Buffalo Final Assessment Roll (`data.buffalony.gov`, dataset `4t8s-9yih`) | City of Buffalo Open Data |
| Address and point for the ~30 standout buildings | US Census Geocoder | US government work, public domain |

## Data rules

- Only the columns listed in `ROLL_COLUMNS` in the script are requested from the assessment roll.
  Owner and mailing columns are never queried, stored or shown; the script asserts this and
  `tests/test_noco_demo_data.py` checks the file.
- Every field carries a source and confidence in `sources`, including `join` for the
  OSM <-> assessment-roll match.
- Row buildings with common walls are noted in `sources` and ranked lower: part of their
  perimeter is a shared wall, so the default 100 % exposed wall overstates their savings.
- Floors come from OSM `building:levels` (0.9) or `height` (0.4), or from a "ONE STORY" roll
  class (0.7). Buildings with none of these get 1 floor labelled `assumed` (0.3), which
  understates their wall area, and rank after buildings with known floors. Use
  `--osm-floors-only` to leave them out.
