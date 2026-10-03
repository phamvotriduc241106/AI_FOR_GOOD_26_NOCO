# Plan review

Proposals for human decision, based on BRIEF.md, PLANS.md, CLAUDE.md, README.md and repo instructions. Assignment, partner data/API access and event logistics remain unconfirmed; spec and task contracts are still placeholders.

The listed tasks total A: 270m, B: 285m, C: 270m. Each leaves less than the required 90m demo freeze in a five-hour window, before integration or pitch work. Budget at most 210m before freeze. Below, each task is capped at 30m; cut further if it cannot fit. Use spare time for integration and human review, not extra features.

## A — NOCO

- **Over-scoped:** seven measure models, incentive stacking, editable sensitivity UI, NPV, and two possible APIs. Even three or four measures require defensible benchmarks. Cut to lighting for one building type and one territory; omit solar, batteries, EV, GIS and API work unless humans confirm a requirement.
- **Duplicates:** scaffolding, validation, provider setup, caching, replay, generic results and Markdown/JSON downloads already exist. Only feature-specific assumptions and report content need work; a new export system does not.
- **Missing:** three months of bills cannot silently become annual usage. Define billing periods, units, rate provenance and any annualization assumption. Whole-building usage is not automatically lighting usage. Define zero/negative-savings behavior, simple ROI versus payback, and evidence mapping per field. Incentives need verified eligibility; otherwise show “unknown/excluded,” not an invented available rebate. Multiple measures would also need overlap handling.
- **Cut-down version (four tasks):**
  1. Scaffold a nullable lighting input schema with field descriptions, quoted evidence, annual usage or an explicit illustrative baseline, and fake sample data.
  2. Add one labeled lighting assumptions row and deterministic savings, net cost, simple ROI and payback; test missing inputs, units and zero savings. Defer results when essential inputs are absent.
  3. Show one recommendation with an assumption/source ledger and next steps in the existing results/export flow; no editable sensitivity controls. Mark it an illustrative estimate.
  4. Add three labeled eval cases with fake responses, run tests/lint and an allowed real-model extraction check, then verify the chosen feature offline before freeze.

## B — AAO

- **Over-scoped:** intake, scored urgency, placement/capacity matching, referrals, generated replies, open-ended records questions, conflict detection and a journey timeline are several products. A second LLM generation step also exceeds the template's extraction-only pattern. Keep intake plus one fixed history check; defer placement and general Q&A.
- **Duplicates:** structured extraction, validation retry, confidence/review flags, the demo shell, exports and replay already exist. Source citations, identity matching and conflict semantics do not; they are the actual feature work.
- **Missing:** reliable case identity, source IDs/dates, unknown versus explicitly denied bite history, and handling ambiguous deadlines. “Snapped” does not establish a bite. Staff must validate escalation rules; no automatic acceptance or care advice. “Staff only” is not authentication. Confirm whether a local synthetic prototype with limited history meets the challenge's broader journey/security expectation; anonymization alone does not authorize real records.
- **Cut-down version (four tasks):**
  1. Scaffold nullable intake facts, evidence and a human-selected synthetic case ID; provide a fake sample and two dated history records for that case.
  2. Implement missing-field questions and explicit staff-review flags with tests for ambiguous wording and unknown facts; omit urgency scores and capacity/pathway decisions.
  3. Add one fixed “reported bite history” view quoting dated sources, flag explicit contradictions for the selected case, and assemble a compassionate template reply for staff review only.
  4. Add three extraction eval cases plus rule tests for conflict/unknown handling, run tests/lint and an allowed real-model check, then verify offline output before freeze.

## C — ACV + Copart

- **Over-scoped:** market valuation, repairs, bid ranges, two-channel economics, VIN decoding, recalls and custom presentation depend on data not supplied. Keep one synthetic vehicle scenario and a transparent two-channel comparison; defer APIs unless required.
- **Duplicates:** VIN HTTP transport, retries, cache and replay are already covered by HttpConnector; only endpoint mapping would be new. Feature registration, generic output and downloads also exist. Do not build another valuation framework or report renderer.
- **Missing:** a precise cash-flow equation: resale price is distinct from resale proceeds after repairs/fees, and the bid ceiling must include the desired margin without subtracting costs twice. Define channel-specific costs, unknown mechanical damage, missing severity and comparable provenance. The example's “cracked/dent” wording supplies no severity level. Synthetic economics cannot substantiate a 3–5× value claim or a real channel recommendation.
- **Cut-down version (four tasks):**
  1. Scaffold a condition schema with nullable severity, exact evidence and a fake sample; attach one explicitly synthetic resale/repair/fee scenario.
  2. Implement two-channel net proceeds and an illustrative bid ceiling from explicit inputs; test arithmetic and withhold the ceiling when a material cost is unknown.
  3. Display the two outcomes, assumptions and risk flags using the existing shell/export; frame the novelty as making the channel tradeoff inspectable.
  4. Add three extraction eval cases and nested-damage rule tests, run tests/lint and an allowed real-model check, then verify offline output before freeze.

All plans: humans approve the feature contract and assign non-overlapping files before parallel work. Fake eval scores prove the harness, not model accuracy. During the final 90m, rehearse the selected feature and its cached/offline path, finish the pitch/submission, and disclose synthetic assumptions and template use. A public API is not automatically a sponsor API; confirm that requirement before choosing an integration.

## Humans: read these five lines first
- [ ] Confirm the assigned challenge, actual deadline, deliverables, judging criteria and API requirement.
- [ ] Choose one cut-down flow and approve its user, inputs, outputs and deferred scope in docs/spec.md.
- [ ] Confirm permitted data/model use and label every synthetic benchmark or unverified assumption.
- [ ] Fill docs/TASKS.md with the schema contract, owners, allowed files and dependencies; reserve 90m for freeze.
- [ ] Require passing tests/lint, honest eval results and a rehearsed offline feature demo before submission.
