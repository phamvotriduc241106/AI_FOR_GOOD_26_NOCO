# PLANS

Assignment: UNKNOWN (see BRIEF.md), so no plan is marked ASSIGNED. Order below is by fit to hackkit
(extract -> rules), not a recommendation to pick; humans decide. ~5h build. All data synthetic or public.
Proposals only; `docs/spec.md` holds the approved decisions.

---

## Plan A: NOCO (building energy savings and ROI)

- **Problem:** NOCO staff spend long manual effort to estimate savings, cost, incentives and payback for a commercial building.
- **User:** a NOCO energy sales consultant preparing a customer proposal.
- **Demo flow:** building description / pasted utility bill text -> LLM extracts building facts + usage -> `rules()` computes per-measure savings, cost, incentives, payback, net investment, ranking -> ranked table + simple customer report (Markdown export).
- **Feature key:** `building_roi`
- **Schema sketch (`BuildingProfile(Reviewable)`):**
  - `address: str | None` (as written), `building_type: str` (office, warehouse, school, retail, other), `square_feet: float | None`, `year_built: int | None`
  - `heating_system`, `cooling_system: str | None` (as written), `has_solar_or_ev: bool | None`
  - `annual_kwh: float | None`, `annual_therms: float | None`, `annual_utility_cost: float | None` (as printed on bill)
  - `evidence: str` per key fact (exact quote)
- **LLM extracts:** the fields above, copied as written. **rules() computes:** per-measure (lighting, HVAC, weatherization, solar, battery, EV charging, monitoring) annual kWh/therm savings = usage x assumed % from a clearly labeled assumptions table; cost savings = savings x rate; project cost = $/sqft or $/unit table; incentives = rule table by measure and state; payback = net cost / annual savings; ranking by payback or net present value. Flags: missing usage, bill vs sqft sanity (kWh/sqft outside range), assumptions used.
- **API (HttpConnector):** optional public: NREL PVWatts (solar estimate by lat/lon) and/or utility rate data (OpenEI) if keys/network allowed; cache + demo mode replay. Core demo works without them.
- **Novel feature:** "assumption ledger": every number in the report links to the assumption row and source that produced it, and users can edit an assumption and see ranking re-sort live (sensitivity), plus an incentive stack with eligibility reasons.
- **sample_text:** 3-month utility bill text + intake note for "Maple Street Elementary, 62,000 sqft, built 1974, gas boiler". `sample_response`: the matching JSON.
- **3 eval cases:** (1) clean bill with kWh, therms, cost; (2) bill missing gas usage (expect null + flag); (3) mixed units / "approx 5k sqft" phrasing, building type "warehouse".
- **Tasks:**
  1. Scaffold `building_roi`, schema, instructions, sample (45m)
  2. Assumptions + incentives tables as Python/JSON, with tests (60m)
  3. `rules()`: savings, cost, payback, net investment, ranking, flags + pytest (60m)
  4. Report export (customer-facing Markdown) + assumption ledger UI (45m)
  5. Optional PVWatts connector, cached (30m)
  6. Evals, demo rehearsal with `make demo` (30m)
- **Risks:** (1) no real savings %/cost/incentive data, so numbers look invented unless clearly labeled assumptions; (2) incentive eligibility varies by region and changes; (3) scope creep across 10 measures: do 3-4.
- **Ask partner:** (1) Which utility territory/state and building types first? (2) Can you share per-measure cost and savings benchmarks or your pricing catalog? (3) Which incentive sources do you trust, and are bonus items (GIS, public property data) expected or optional?

---

## Plan B: AAO (rescue intake and knowledge system)

- **Problem:** AAO staff lose time turning fragmented surrender/placement requests into a decision-ready case and finding what AAO already knows.
- **User:** an AAO intake coordinator (staff only).
- **Demo flow:** pasted messy request (email/text/DM) + a small synthetic case-history file -> LLM extracts a standard intake record -> `rules()` finds missing info, urgency, safety flags and pathway candidates against a capacity table -> case card + follow-up questions + draft reply marked "for staff review" + "ask the records" answers with source citations.
- **Feature key:** `rescue_intake`
- **Schema sketch (`IntakeRecord(Reviewable)`):**
  - `requester_name`, `requester_type` (owner, shelter, rescue, family), `contact_channel`
  - `species`, `breed`, `age_years: float | None`, `sex`, `spayed_neutered: bool | None`
  - `reason_for_request: str`, `deadline_stated: str | None` (as written)
  - `medical_issues: list[str]`, `behavior_issues: list[str]`, `bite_history: str | None` (quote), `other_animals_in_home: str | None`
  - `mentions_euthanasia_risk: bool`, `financial_or_housing_crisis: bool`
  - `evidence: str` quote per risky field; `missing_info` is computed, not extracted
- **LLM extracts:** what the message says, with quotes; never infers a bite history that is not written. **rules() computes:** required-field check -> missing list + follow-up question templates; urgency score from keyword/field rules (euthanasia risk, deadline < N days, bite, medical); pathway candidates from rules over species/behavior/medical vs a synthetic capacity table (foster slots, kennel space, funds); referral alternatives when capacity is 0. Conflict flag: same animal in history file with a different fact.
- **API:** none given. Shelterluv is named but no access; use a CSV of synthetic cases. Local Ollama if the partner bars cloud AI.
- **Novel feature:** "evidence-first answers + conflict detector": every staff answer ("Does this dog have a bite history?") quotes the source record, and contradictions or stale entries across sources are flagged instead of smoothed over; also shows the animal's journey timeline.
- **sample_text:** a text-thread surrender for a 3-year-old shepherd mix, "snapped at a neighbor's kid once", owner moving in 10 days. `sample_response`: matching JSON.
- **3 eval cases:** (1) clear cat surrender, no issues; (2) dog with bite mention and a deadline (expect bite flag, urgent); (3) vague DM missing species/age (expect nulls, no guessing).
- **Tasks:**
  1. Scaffold `rescue_intake`, schema, instructions, sample (45m)
  2. Synthetic case-history + capacity data, ~10 records (30m)
  3. `rules()`: missing info, urgency, flags, pathway, referrals + pytest (75m)
  4. Draft reply + follow-up questions (LLM text from rules output, review banner) (45m)
  5. "Ask the records" lookup with citations + conflict flags (60m)
  6. Evals, rehearsal with `make demo` (30m)
- **Risks:** (1) sensitive data: synthetic only, and ask before using any cloud AI on real records; (2) unsafe or overconfident advice on bites/medical: keep all outputs "for staff review"; (3) scope (11 optional items): pick intake + one query.
- **Ask partner:** (1) Can you give anonymized samples or a fake Shelterluv export, and may they go to cloud AI? (2) Which of the suggested capabilities matters most to staff? (3) Where is capacity kept today, and what counts as "full"?

---

## Plan C: ACV + Copart (open-ended automotive commerce)

- **Problem:** vehicle buyers and sellers across ACV and Copart cannot easily see a vehicle's true condition and value in one place (our chosen framing; the source is open-ended).
- **User:** a wholesale dealer deciding whether and how much to bid on a vehicle.
- **Demo flow:** inspection notes + listing text (+ optional VIN) -> LLM extracts condition findings -> `rules()` estimates repair cost, adjusts value and gives a bid-range and channel suggestion with risk flags -> one-page bid brief.
- **Feature key:** `bid_brief`
- **Schema sketch (`VehicleReport(Reviewable)`):**
  - `vin: str | None`, `year`, `make`, `model`, `trim`, `odometer: int | None`
  - `title_status: str | None` (clean, salvage, rebuilt, as written), `asking_or_reserve_price: float | None`
  - `damages: list[Damage]` where `Damage(area, severity: minor|moderate|severe, description, evidence)`
  - `mechanical_notes: list[str]`, `reported_warning_lights: list[str]`
- **LLM extracts:** damage items and severity words as written, title wording. **rules() computes:** repair cost from an area x severity table; base value from a small synthetic comps table (year/make/model/mileage adjustment); expected resale = base - repair - fees; bid ceiling; flags for title brand, mileage vs age, undisclosed-sounding gaps, repair > X% of value.
- **API (HttpConnector):** NHTSA vPIC VIN decode (free, public) and optionally NHTSA recalls; cached and replayable.
- **Novel feature:** "same car, two channels": compares expected net outcome if sold via online condition-report auction (ACV-style) vs salvage/physical auction (Copart-style), choosing by repair-cost threshold. This uses the combined ecosystem the prompt asks for. Channel economics are labeled assumptions.
- **sample_text:** inspection note for a 2018 Honda Civic, 74k miles, "rear bumper cracked, driver door dent, check-engine light, title: clean". `sample_response`: matching JSON.
- **3 eval cases:** (1) minor cosmetic damage, clean title; (2) salvage title with front-end collision (expect flags); (3) sparse listing with no mileage (expect null + flag).
- **Tasks:**
  1. Scaffold `bid_brief`, schema, instructions, sample (45m)
  2. Synthetic comps + repair-cost + fee tables, tests (45m)
  3. `rules()`: value, repair, bid ceiling, channel comparison, flags + pytest (75m)
  4. NHTSA VIN decode through HttpConnector with cache (30m)
  5. Bid brief export + channel comparison UI (45m)
  6. Evals, rehearsal with `make demo` (30m)
- **Risks:** (1) no real data or baseline for "3-5x value": the demo's value claim is only our assumptions; (2) too open-ended, so judges may not see a clear tie to the prompt; (3) synthetic comps may look fake.
- **Ask partner:** (1) Is a working prototype expected or a concept, and what does "3-5x value" mean? (2) Any sample inspection reports or public datasets we may use? (3) Which user matters most: buyer, seller, or internal operations?

---

## Cross-plan notes
- Whichever is chosen, copy the plan into `docs/spec.md` after human approval; the numbers in every plan are demo assumptions, not partner facts.
- Pre-event checks: `make test`, `make demo`, record real-model outputs once so demo mode can replay them.
