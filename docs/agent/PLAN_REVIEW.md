# Plan review: NOCO

Proposal for human decision; the chosen challenge remains NOCO. Sources: BRIEF.md, PLANS.md, CLAUDE.md, README.md and AGENTS.md. `docs/spec.md` and `docs/TASKS.md` still contain placeholders; humans must record the approved scope and ownership there.

## Over-scoped for five hours

- The first five tasks total **270 minutes**, before rehearsal or submission. A five-hour window with a 90-minute freeze permits only **210 minutes before freeze**. The proposed 45–90-minute tasks also exceed the repo’s roughly 30-minute task limit.
- Cut lighting, windows/HVAC, cross-measure ranking, NPV, multiple fuels/cities, bill parsing and optional APIs. Each adds inputs, assumptions and validation beyond the reference insulation case. A single-measure demo leaves opportunity ranking unmet: disclose that limitation and ask NOCO to accept the slice.
- Keep the assumption ledger; defer automatic “which missing input matters most” analysis and multi-variable sensitivity. Show one explicitly supplied project-cost range only if available; otherwise report payback as unavailable.
- Replace the promised “reproduces NOCO sheet” badge with a reference comparison showing confirmed, approximate and unresolved results. Blurry inputs cannot support a verified-reproduction claim.

## What hackkit already provides

- Reuse the scaffold, feature registry, Pydantic extraction/validation retry, providers and `Reviewable` flags. Only the NOCO schema, extraction instructions, samples and deterministic rules are new.
- Reuse the Streamlit shell, Markdown/JSON downloads, cache, fake provider and demo replay. A concise customer summary may need feature-specific formatting; a new reporting engine, PDF exporter or UI is unnecessary. The pitch PDF/PPT is a separate deliverable.
- Reuse the eval runner and, if later justified, `HttpConnector`. Write cases and calculation tests, not another evaluation or API framework. Field-level provenance and assumption explanations remain genuine feature work beyond generic review flags.

## Missing decisions and correctness checks

- **Formula contract:** the sketch refers to absent `area_basis` and omits perimeter, height, window share, exposure, HDD/CDD and load factor inputs or explicit constants. Confirm units, defaults and override precedence; apply shape adjustment once. Separate heating and cooling degree-days/COP calculations. Prefer a confirmed insulated-wall area for the first slice.
- **Reference truth:** obtain readable values and formula explanations locally from NOCO. Agree tolerances only for confirmed outputs; do not infer HDD to force agreement. Until then, test the legible arithmetic (including 3,900 × $4 = $15,600) separately from unresolved physical-model reproduction.
- **Economics:** require an explicit quote or labelled synthetic cost scenario. Define simple payback and any displayed ROI; ten-year energy value is not ROI. Missing cost or nonpositive savings must not yield a numeric payback. Incentive eligibility, caps and stacking are unknown; the screenshot’s rate is a reference assumption, not proof of a current entitlement. Flag incentives exceeding cost for review.
- **Extraction contract:** “no unit conversion” conflicts with expecting “40k sf” as 40,000; choose a documented normalization rule or remove that case. Nested electricity prices are outside the stated top-level eval scope; flatten the selected tariff or test nested values separately. Include per-case fake responses and test invalid R/COP, missing costs, zero savings and contradictory inputs.
- **Evidence and story:** “days researching” is unsupported by BRIEF; say “returns to the office to research.” Confirm the advisor persona. Use synthetic/public notes for cloud extraction; partner spreadsheet sharing needs permission. No sponsor API is specified, so none should block the demo.

## Recommended cut-down version: four tasks

1. **Humans, 30 min — lock the contract.** Confirm insulation-only, one Buffalo commercial example with electric heating/cooling, area/weather assumptions, incentive status and cost handling. Record approved fields, output definitions and nonoverlapping file ownership. If formulas remain unavailable, label the model illustrative and the sheet comparison partial.
2. **Claude Code, 30 min — build one vertical slice.** Scaffold `noco_savings`; add schema, instructions, synthetic sample/response and insulation/economics rules with focused tests. Output annual kWh/$ savings, conditional incentive, net investment and simple payback or a specific missing-input reason. Cut unsupported branches at the time limit.
3. **Codex, 30 min — independently check evidence.** After contract approval, prepare three synthetic extraction cases: complete, missing cost, contradictory input. Review calculator results against confirmed reference arithmetic; test unresolved assumptions explicitly. Run fake evals and one permitted real-model evaluation; distinguish extraction accuracy from arithmetic correctness.
4. **Humans with agents, 30 min — accept the demo.** Use existing UI/export to show the recommendation, evidence/assumptions and next steps. Run tests, lint and offline demo; verify replay and rehearse the complete input-to-report flow. Keep file edits within assigned ownership.

These are time-boxed proposals, with remaining pre-freeze time reserved for integration defects and partner answers. Freeze 90 minutes before the confirmed deadline (2:00 p.m. if 3:30 p.m. holds); reserve the final 90 minutes for PDF/PPT, submission and four-minute rehearsals. Address all five rubric categories: advisor value/feasibility; visible assumptions as innovation; a clear customer report; more measures/incentive integrations as future work; checked arithmetic and offline execution. Do not claim measured time savings without measurement.

## Humans: read this checklist first

- [ ] Approve insulation-only and record the scope, contract and owners.
- [ ] Confirm spreadsheet formulas; label unresolved comparisons honestly.
- [ ] Supply a cost scenario and verify incentives, or show them as unknown/illustrative.
- [ ] Require tested arithmetic, visible assumptions and a working offline demo.
- [ ] Confirm deadline, freeze 90 minutes early, and submit/rehearse the PDF/PPT pitch.
