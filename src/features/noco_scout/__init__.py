"""NOCO Address-to-Quote: public GIS data and NOCO's insulation calculator for Buffalo buildings.

This module registers the `noco_scout` feature for the shared demo shell. The LLM part only
reads a SYNTHETIC field note or utility-bill snippet into a SiteNote; numbers are always computed
by code (calc.py). Skeleton from T1; T11 (COULD) completes the extraction rules and evals.
The data contract lives in `contract.py`; reference data in `fixtures.py`.
"""

from __future__ import annotations

import json

from pydantic import Field

from hackkit.feature import Feature, RulesResult, register
from hackkit.schemas import Reviewable, ReviewFlag


class SiteNote(Reviewable):
    address: str | None = Field(default=None, description="Building street address as written.")
    building_use: str | None = Field(
        default=None, description="What the building is used for, e.g. office, retail, school."
    )
    floors: int | None = Field(default=None, description="Number of floors above ground.")
    year_built: int | None = Field(default=None, description="Year the building was built.")
    heating_system: str | None = Field(
        default=None, description="Heating system as written, e.g. electric resistance, gas boiler."
    )
    existing_insulation_r: float | None = Field(
        default=None, description="Existing wall insulation R-value, e.g. 11 for R-11."
    )
    monthly_bill_usd: float | None = Field(
        default=None, description="Monthly energy bill in US dollars, as written."
    )
    evidence: str = Field(
        default="", description="Exact sentences from the note that support the fields above."
    )


INSTRUCTIONS = """Read this field note or utility-bill snippet about a commercial building in
Buffalo, NY. Extract only what is written: address, building use, floors, year built, heating
system, existing wall insulation R-value and monthly energy bill in USD. Leave a field empty if
it is not written. Never estimate savings, costs or payback; never guess the owner or the energy
supplier."""

_CHECKED = ("address", "heating_system", "existing_insulation_r")


def rules(note: SiteNote) -> RulesResult:
    """Deterministic checks only; savings come from calc.py, never from the model."""
    flags = [
        ReviewFlag(field=name, reason="Not found in the note; ask the customer or use defaults.")
        for name in _CHECKED
        if getattr(note, name) is None
    ]
    found = sum(
        getattr(note, name) is not None for name in SiteNote.model_fields if name != "evidence"
    )
    return RulesResult(
        metrics={"fields_found": found},
        flags=flags,
        summary=f"Site note for {note.address or 'an unknown address'}.",
    )


# Synthetic note: made-up address and numbers, safe to send to any LLM provider.
SAMPLE_TEXT = """Site visit, 101 Example Main St, Buffalo NY (synthetic note).
Six-storey office building, built 1962. Heating is electric resistance baseboard.
Walls have R-11 batts per the facilities manager. Last electric bill was $4,250 for the month."""

SAMPLE_RESPONSE = json.dumps(
    {
        "address": "101 Example Main St, Buffalo NY",
        "building_use": "office",
        "floors": 6,
        "year_built": 1962,
        "heating_system": "electric resistance baseboard",
        "existing_insulation_r": 11,
        "monthly_bill_usd": 4250.0,
        "evidence": "Six-storey office building, built 1962. Heating is electric resistance "
        "baseboard. Walls have R-11 batts. Last electric bill was $4,250 for the month.",
        "confidence": 0.85,
        "uncertain_fields": [],
    }
)

FEATURE = register(
    Feature(
        key="noco_scout",
        title="NOCO Address-to-Quote (Buffalo)",
        description="Turns a site note into building facts for NOCO's insulation savings estimate.",
        schema=SiteNote,
        instructions=INSTRUCTIONS,
        rules=rules,
        accepts=("text",),
        sample_text=SAMPLE_TEXT,
        sample_response=SAMPLE_RESPONSE,
        tags=("noco",),
    )
)
