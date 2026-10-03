"""Export reference outputs from the Python implementation for the JavaScript parity tests.

Usage: python web/tools/export_parity.py OUT.json
The JS port (web/js/) must reproduce every number, string, report and CSV in OUT.json exactly.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import sys
from pathlib import Path

from features.noco_scout import SAMPLE_RESPONSE, SiteNote, geo, report
from features.noco_scout import rules as site_rules
from features.noco_scout.calc import estimate_insulation, inputs_from_facts
from features.noco_scout.contract import Assumptions
from features.noco_scout.fixtures import SAMPLE_BUILDINGS
from features.noco_scout.mapdata import prospects_to_deck_rows
from features.noco_scout.prospect import build_opportunity, rank_prospects
from hackkit.schemas import review_flags_for

FIXED_DATE = dt.date(2026, 10, 3)

# Assumptions(**kwargs) scenarios: the two pages' real calls plus edge cases that exercise every
# branch (explicit vs default fields, gas, DAC, legacy HDD, user incentive rate, profiles).
SCENARIOS = {
    "default": {},
    "address_page": {"cost_per_sqft": 8.0},
    "prospect_page": {"cost_per_sqft": 8.0, "margin_pct": 0.35},
    "toggles_off": {"cost_per_sqft": None, "margin_pct": None},
    "gas": {"heating_fuel": "natural_gas", "heating_efficiency": 0.8, "cost_per_sqft": 6.5},
    "dac_true": {"is_dac": True},
    "dac_false": {"is_dac": False},
    "explicit_hdd": {"hdd": 6075.0},
    "legacy": {"heating_realization_factor": None, "operating_profile": None},
    "user_rate": {"incentive_per_sqft": 4.0},
    "profile_retail": {"operating_profile": "retail"},
    "small_delta_r": {"existing_r": 13.0, "proposed_r": 19.0, "margin_pct": 0.3},
    "overrides": {"floor_height_ft": 14.0, "window_door_pct": 0.2, "operating_load_factor": 0.9},
}

ADDRESS_QUERIES = [
    "110 Franklin St",
    "110 Franklin Street",
    "110 FRANKLIN, BUFFALO",
    "110 franklin st buffalo ny",
    "110 Franklin St., Buffalo, NY 14202",
    "110 franklin st buffalo ny 14202",
    "110 franklin st 1402",  # a 4-digit token is not a ZIP and must stay
    "33 Franklin St",
    "333 Franklin Street",
    "34 Franklin St",
    "3 Franklin St",
    "107 Delaware Avenue",
    "1 Seneca Street Buffalo NY",
    "101 Example Main Street, Buffalo NY",
    "   ",
    "Franklin",
]

SITE_NOTE_CASES = [
    json.loads(SAMPLE_RESPONSE),
    {
        "address": "  ",
        "floors": 3,
        "evidence": "",
        "confidence": 0.4,
        "uncertain_fields": ["floors"],
    },
    {
        "address": "12 Main St",
        "heating_system": "gas boiler",
        "existing_insulation_r": 13.5,
        "evidence": "R-13.5 walls",
    },
    {"floors": 2.5},
    {"floors": 0},
    {"monthly_bill_usd": -1},
    {"owner": "someone"},
    {"uncertain_fields": ["payback"]},
    {"year_built": 1890, "monthly_bill_usd": 0, "evidence": "Built 1890."},
]


def dump(model) -> dict:
    return model.model_dump(mode="json")


def main(out: Path) -> None:
    report.date = type("FixedDate", (), {"today": staticmethod(lambda: FIXED_DATE)})
    demo = geo.load_demo_buildings()
    buildings = [*demo, *SAMPLE_BUILDINGS]
    logo = base64.b64encode(report.LOGO_PATH.read_bytes()).decode("ascii")

    calc = {}
    for name, kwargs in SCENARIOS.items():
        a = Assumptions(**kwargs)
        rows = []
        for facts in buildings:
            inputs = inputs_from_facts(facts, a)
            result = estimate_insulation(inputs)
            rows.append(
                {
                    "inputs": dump(inputs),
                    "result": dump(result),
                    "opportunity": dump(build_opportunity(facts, result, a)),
                }
            )
        calc[name] = rows

    ranking, deck, reports = {}, {}, {}
    for name in ("default", "prospect_page", "gas"):
        a = Assumptions(**SCENARIOS[name])
        ranked = rank_prospects(demo, a, top=len(demo))
        ranking[name] = [[p.rank, p.facts.address, p.score] for p in ranked]
        top = ranked[:25]
        deck[name] = {
            "top25": prospects_to_deck_rows(top),
            "all": prospects_to_deck_rows(ranked),
        }
        reports[name] = {
            "manager_top25": report.render_manager_report(top, a),
            "csv_top25": report.prospects_to_csv(top),
            "csv_all": report.prospects_to_csv(ranked),
            "customer": [
                report.render_customer_report(p.facts, p.inputs, p.result, p.opportunity)
                for p in (ranked[0], ranked[7], ranked[150], ranked[-1])
            ],
            "customer_no_opportunity": report.render_customer_report(
                ranked[3].facts, ranked[3].inputs, ranked[3].result
            ),
        }
    a = Assumptions()
    reports["empty"] = {
        "manager": report.render_manager_report([], a),
        "csv": report.prospects_to_csv([]),
    }
    sample_ranked = rank_prospects(SAMPLE_BUILDINGS, Assumptions(cost_per_sqft=8.0), top=5)
    reports["synthetic"] = {
        "manager": report.render_manager_report(sample_ranked, Assumptions(cost_per_sqft=8.0)),
        "csv": report.prospects_to_csv(sample_ranked),
        "deck": prospects_to_deck_rows(sample_ranked),
    }

    lines = sorted(
        {line for rows in calc.values() for r in rows for line in r["result"]["assumptions"]}
    )
    split = {line: list(report.split_assumption(line)) for line in lines}

    addresses = {
        q: {
            "normalized": geo._normalize_address(q),
            "street_key": geo._street_key(q),
            "match": (m.address if (m := geo.match_address(q, demo)) else None),
        }
        for q in ADDRESS_QUERIES
    }

    notes = []
    for raw in SITE_NOTE_CASES:
        try:
            note = SiteNote.model_validate(raw)
        except Exception:  # noqa: BLE001 - only the outcome matters for parity
            notes.append({"raw": raw, "ok": False})
            continue
        rules = site_rules(note)
        notes.append(
            {
                "raw": raw,
                "ok": True,
                "metrics": rules.metrics,
                "summary": rules.summary,
                "flags": [f.model_dump() for f in [*review_flags_for(note), *rules.flags]],
            }
        )

    payload = {
        "fixed_date": FIXED_DATE.isoformat(),
        "logo_data_url": f"data:image/png;base64,{logo}",
        "scenarios": SCENARIOS,
        "buildings": [dump(b) for b in buildings],
        "calc": calc,
        "ranking": ranking,
        "deck": deck,
        "reports": reports,
        "split_assumption": split,
        "addresses": addresses,
        "site_notes": notes,
    }
    out.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
