# Critique of BRIEF.md

All line citations refer to `docs/agent/transcript_snapshot.txt`: DOC-1 = lines 1–172; DOC-2 = 173–311; LIVE = 312 onward. Written-source uncertainties are conversion issues, not misheard speech. Most challenge requirements and logistics are accurately summarized.

## (a) Unsupported or overstated claims

- **“Chosen by the human” / “our challenge”:** no recorded team-specific decision establishes this. LIVE announces first-preference matches generally (811–819); it does not identify this team's preference. Preserve NOCO as external team context only if independently confirmed. Calling the spreadsheet a “reference test case” is also a team proposal, not a stated judging requirement (182–280).
- **Opportunity list sounds mandatory:** DOC-1 says “such as” (135–147), not that every listed technology must be implemented. BRIEF's “Required build” framing risks turning examples into scope obligations.
- **Arithmetic is not exact as written:** `10 × $1,448 = $14,480`, not $14,476; `8,812 × $0.16 = $1,409.92`, not $1,409.90. The screenshot may use unrounded internal values (202, 221–228, 259–266). Label these approximate consistency checks; do not alter source numbers to force agreement. “10,000 sq ft × 12 ft” is not wall area; the supported calculation is perimeter × height (241–246).
- **Calculator certainty exceeds the conversion:** BRIEF omits uncertainty on proposed effective R's first digit, cooling-load middle digits, and heating-dollar decimals (233, 257, 265). The incentive note gives alternative units with unreadable conditions (250–251); $4/sq ft is plausible from the displayed arithmetic, not a fully verified rule.
- **Negative investment/payback:** the screenshot gives an estimated incentive but no project cost, incentive cap, or eligibility formula (219–280). A cost below $15,600 does not establish an actual negative customer investment or meaningful negative payback. This is a hypothetical requiring partner rules, not an implication of the example.
- **Cloud rules wording is too absolute:** “not discussed” overlooks explicit encouragement to use ChatGPT and another tool for mock data (355–357). That supports synthetic-data generation only; it does not authorize uploading partner data or establish an API/key policy.

## (b) Important omissions or underemphasized details

- **Live demo permission is substantially answered:** organizers explicitly allow plugging in to connect to a “demo page”; PDF/PPT is the uploaded presentation copy (579–587). BRIEF mentions laptop access but still asks “live app … or slides only?” Confirm timing/Q&A or video details, rather than reopening basic live-demo permission.
- **Business problem and role allocation come first:** organizers explicitly say to envision the business problem before coding, give every team component equal importance, and decide who handles technical, creative, and presenting work (733–749, 1053–1095). This deserves an actionable planning priority, beyond the brief's general judging summary.
- **Model details omitted:** custom load factor applies only when Profile = Custom; both custom R-values are likewise conditional (209–214). Preserve these conditions when implementing. The helper table explicitly labels base perimeter as 500 ft (273–275); unexplained geometry is a clarification item, not proof the spreadsheet is wrong. A zero optional override may mean “use default,” but the source does not define that convention (212–217, 245).
- **On-site support:** mentors answer challenge questions as well as technical questions; representatives are available, and people working elsewhere must return to consult mentors (1033–1047, 1115–1127). Use that access to settle formula and scope questions early. The NOCO packet is already noted correctly (1171); its contents remain unknown.

## (c) Likely mishearings and conversion errors

- **High confidence, document-backed names:** “no-co,” “doko,” “No code” → **NOCO** (403, 415, 1043; compare 115).
- **Likely, not verified:** “use cloud” → **use Claude** (355); “built in data” → **building data** (415; compare 119); “no-cost energy calculator” → **NOCO's energy calculator** (633); “estimated engine savings” → **estimated energy savings** (965; compare 150). Do not infer a free-product requirement from “no-cost.”
- **Times/numbers:** “10-15,” “10-30,” “1030” mean **10:15 / 10:30** (841–843); “3.30 … date” means a **3:30 p.m. submission deadline** in context (1019, 1105–1127). Posting codes is tentatively **2:45–3:00 p.m.**, not a second deadline (1105–1111). “Two tracks” is explicitly corrected to **three**, with two prizes each (691–697).
- **Written conversion only:** R-49, heating 8,812, HDD 6,xxx, CDD 600/650, helper loads and incentive units remain uncertain (176, 196, 221, 233–238, 251–265). Arithmetic cannot recover the original text reliably. “HY-GRADE” is also expressly uncertain (184–185). The packet-holder name “risky hunt” cannot be responsibly reconstructed (1171).

## (d) Risks for this three-person team

- **Scope/time:** broad measures plus ranking, economics, and reporting (135–171) can overwhelm the stated five-to-six-hour window (625–635). Humans should approve one demonstrable slice and its omissions. The 3:30 deadline implies a **2:00 p.m. freeze under the repo's 90-minute rule**; that is a planning calculation, not an organizer announcement (1105).
- **False precision:** blurry inputs, unknown costs, and incomplete incentive conditions can produce convincing but unsupported ROI. Obtain the original calculator/partner explanation; label assumptions and estimates (149–155, 176, 237–251).
- **Data dependency/privacy:** no usable API or dataset access is established; the mock-data suggestion is the actionable fallback (347–357). Follow the repo's public/synthetic-data restriction; a packet handoff is not cloud-upload permission (1171).
- **Pitch and submission failure:** protect rehearsal time and prepare the required PDF/PPT; a polished app alone does not demonstrate client value (579–587, 593–615, 1083–1095). Return by 3 p.m. and submit by 3:30 (1105–1127).

Status: critique complete; BRIEF.md unchanged. Decisions remain with the humans.
