# PLANS (proposals; humans decide, `docs/spec.md` is the approved record)

Basis: `BRIEF.md` (revised) and `CRITIQUE.md`. Build time about 5 h; demo freeze 2:00 p.m. (90 min before the 3:30 submission; our calculation). Public or synthetic data only.

---

## 1. NOCO: building energy savings, incentives and payback  **[ASSIGNED]**

**Problem.** NOCO staff visit a commercial building, go back to the office, and spend days researching before they can tell a customer what an upgrade would save, what incentives apply and when it pays back.

**User.** One NOCO sales/energy advisor producing a quote. The end reader is the commercial-building customer (a team assumption; ask the partner).

**Demo flow.**
- Input: a messy site-visit note or utility-bill text, plus the NOCO insulation spreadsheet inputs as the reference case.
- Processing: LLM extracts calculator inputs with evidence; `rules()` runs the deterministic calculator, incentive lookup, payback and ranking.
- Output: ranked measures, a customer-facing one-page report (recommendation, savings, incentives, net investment, payback, next steps), review flags, and a "reproduces NOCO sheet" check. Export via the existing Markdown/JSON.

**Feature key.** `python -m hackkit.scaffold noco_savings "NOCO energy savings"`

**Schema sketch** (inherits `Reviewable`; every field gets `description=`; money as `float`).
- `BuildingSite(Reviewable)`
  - `location: str`: city/state as written (e.g. "Buffalo, NY").
  - `building_type: str`: office, warehouse, school, retail, etc., as written.
  - `floor_area_sqft: float | None`: footprint or total area as stated; say which in `area_basis`.
  - `floors: int | None`; `shape: str | None` (e.g. "very long / narrow").
  - `existing_insulation_r: float | None`; `proposed_insulation_r: float | None`: wall R-values as written.
  - `heating_system: str | None`, `heating_cop: float | None`; `cooling_system: str | None`, `cooling_cop: float | None`.
  - `energy_prices: EnergyPrices`: `electricity_per_kwh`, `gas_per_therm`, `propane_per_gal`, `fuel_oil_per_gal`, `district_per_mmbtu`, each `float | None`, as printed.
  - `incentive_program: str | None`: program named in the note.
  - `annual_kwh`, `annual_therms`, `annual_bill_usd: float | None`: from a utility bill if pasted.
  - `quoted_project_cost_usd: float | None`: only if the note states a cost.
  - `evidence: dict[str, str]` or per-field `evidence` quote (follow the receipt pattern).

**LLM extracts vs. `rules()` computes.**
- LLM: copies the fields above exactly as written, quotes evidence, lists uncertain fields. It never converts units, estimates a missing R-value, or calculates anything.
- `rules()` (plain Python, unit tested): defaults for missing inputs (each default logged as an assumption flag); effective R, U = 1/R, dU; wall area = perimeter x height x (1 - window/door share) x shape multiplier; load = dU x area x HDD x 24 x load factor; kWh = Btu / 3,412 / COP; cost savings; incentive = rate x insulated area (rule from a lookup table); net investment = project cost - incentive; payback = net / annual savings with explicit handling of cost <= incentive (report "incentive covers cost", not a negative payback); ranking by net present value or payback across measures; low/base/high sensitivity.
- Calibration to the reference sheet: BRIEF numbers (R-11 -> R-49, 3,900 sq ft insulated wall, $15,600 incentive, 8,812 + 236 kWh, $1,448/yr) are the target outputs. HDD is a hypothesis to check: the BRIEF figures imply roughly 6,000 HDD under 75% load factor; do not hard-code it until the partner confirms the real HDD/CDD and the cooling formula.

**Sponsor / public API calls.** None named. Optional, only if time remains (bonus items): weather degree-days or address -> public property data via `HttpConnector` (cached, demo-mode replay). Core build uses a local JSON lookup (`data/` HDD/CDD by city, incentive programs, measure cost per sq ft) marked "synthetic/illustrative, confirm with NOCO".

**Novel feature (pick this one).** *Assumption ledger with a payback range.* Every number in the report is tagged as stated (with the quoted evidence), defaulted, or assumed; the report shows payback as a low-high band and which single missing input (e.g. project cost, true HDD) would narrow it most. It directly answers the false-precision risk, and most teams will show a single confident number.

**Measures in scope.** Insulation (full, matched to the NOCO sheet); then 2 more with simple table-driven rules (lighting upgrade, window/HVAC) so ranking is real. Solar, EV, batteries, generators are listed as "future development" only.

**sample_text / sample_response.**
- `sample_text`: a realistic site-visit note for the reference case ("Office, ~10,000 sq ft, 1 floor, long narrow, Buffalo NY, walls R-11, electric resistance heat COP 1, packaged rooftop AC COP 3, electricity $0.16/kWh, National Grid commercial weatherization, considering R-49 walls").
- `sample_response`: the matching JSON with evidence quotes; one deliberately missing field (project cost) so the demo shows the assumption flag and range.

**3 eval cases** (`evals/cases/noco_savings.jsonl`; top-level fields only, floats).
1. Reference case: the note above; expect area 10000, existing R 11, proposed R 49, heating COP 1.0, cooling COP 3.0, electricity 0.16.
2. Messy warehouse note (synthetic): units mixed ("approx 40k sf", "R-5 or so", gas heat 80% efficient, $1.20/therm); expect area 40000, existing R 5, `uncertain_fields` includes existing R.
3. School with a pasted bill snippet (synthetic): expect `annual_kwh` and `annual_bill_usd` from the bill, building type "school", no invented project cost (null).
Plus `rules()` tests: reference-case reproduction within tolerance (not forced equal), cost <= incentive, zero/missing overrides, ranking order.

**Ordered tasks (max 6).**
1. Spec + business story (30 min, humans): write `docs/spec.md`; settle problem, user, role split; collect the NOCO packet; ask mentors the questions below.
2. Scaffold `noco_savings`; schema + `INSTRUCTIONS` + sample text/response (45 min).
3. `rules()` with tests first: insulation calculator, incentive lookup, payback, reference-case reproduction (90 min).
4. Add 2 more measures + ranking + assumption ledger and payback range (60 min).
5. Customer-facing report (Markdown export + Streamlit tweaks, "reproduces NOCO sheet" badge); 3 eval cases, one real-model run (45 min).
6. Freeze at 2:00 p.m.: run all inputs on the real model, enable demo mode, build PDF/PPT, rehearse the 4-minute pitch (rubric order: impact, innovation, presentation, future, execution).

**Top 3 risks.**
1. Formula gaps (HDD/CDD, perimeter 500 ft vs shape multiplier, window deduction vs 0% override, cooling load) make the reproduction miss; mitigation: show the gap openly, ask NOCO, tolerance-based test.
2. False precision: no project cost or incentive rules; mitigation: assumption ledger, ranges, labelled illustrative tables.
3. Scope creep into solar/EV/GIS; mitigation: insulation slice first, others only as stub rows or "future development".

**3 questions to ask NOCO before building.**
1. Can we get the original spreadsheet (exact HDD/CDD, perimeter and window/door logic, which override wins, incentive unit and cap)?
2. What project cost per measure should we use, and which incentive programs (National Grid, NYSERDA, federal) are in scope for Buffalo?
3. Is a working insulation slice plus ranking enough, and is the user the NOCO advisor or the customer?

---
