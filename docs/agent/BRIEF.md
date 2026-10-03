# BRIEF: AI for Good Hackathon (UB)

Sources (all in `docs/agent/transcript_snapshot.txt`):
- **DOC-1** = "AI_for_Good_Hackathon_Full_Text.txt" (written challenge statements, pages 1-5, converted from photos).
- **DOC-2** = "NOCO_Calculator_and_Judging_Rubric.txt" (spreadsheet screenshot + rubric, converted from photos).
- **LIVE** = "briefing_e0d07b9f.txt" (speech-to-text of the kickoff; timestamps `[mm:ss]` from recording start, not clock time).

Rule used: DOC for requirements, LIVE for announcements. Mark `[INFERRED]` = my inference, not stated.

## ASSIGNMENT
ASSIGNMENT: NOCO: AI + calculator for commercial building energy savings, incentives and payback; NOCO insulation spreadsheet example = reference test case; judged on the 5-category rubric (impact/feasibility, innovation, presentation, future potential, execution) (chosen by the human per the task instruction; the transcript does NOT record a team assignment, and the "reference test case" role is a team proposal, not a judging requirement).

Note: LIVE says teams ranked preferences via QR code and "This is not a guarantee" `[15:00]-[15:03]`; "no co on the end" of the room `[25:27]`. A NOCO packet is held by someone at the back: "if you are working on a no-co project, risky hunt in the back is has a packet for you" `[46:54]` (name garbled).

---

## 1. Challenge: NOCO

### 1A. NOCO (our challenge)
- **Partner:** NOCO (DOC-1 p.4 "NOCO / Challenge Question"). LIVE `[03:44]`: "no-co who is talking about AI power, energy savings, and customer ROI" (speech-to-text, wording garbled).
- **Problem (DOC-1 p.4):** "How can NOCO use AI, building data, and available incentive programs to quickly estimate energy savings, project economics, and customer ROI for commercial buildings?"
  - Current process (LIVE `[03:49]`-`[04:13]`): staff "go out to an area to collect all the information go back to the main office and do the research", then tell the customer they "could save X amount of money by switching to these style windows or upgrade your door and put this kind of insulation in. all of it takes time."
  - NOCO wants "essentially an energy-saving calculator" using AI, built-in data and systems, then "generate a overall estimate" (LIVE `[04:15]`-`[04:32]`, garbled).
- **Target users:** DOC-1 does not name them. LIVE: "their clients" / customer (`[03:49]`, `[04:02]`). [INFERRED] Primary user = NOCO sales/energy staff producing quotes; end reader = commercial-building customer (the report is "customer-facing").
- **Build scope (DOC-1 p.4-5; the lists below are "such as" examples, not mandatory scope):** AI-powered tool estimating energy and cost savings for commercial buildings.
  - Possible inputs: building address; square footage; building type (office, warehouse, school, retail, etc.); year built; existing heating/cooling systems; utility usage/bill info (if available).
  - Opportunities to evaluate: insulation and weatherization; windows; HVAC upgrades; natural gas; electric; solar; EV charging; lighting upgrades; energy monitoring and management; generators; battery storage; other NOCO energy solutions.
  - Per recommendation calculate: estimated annual energy savings; annual cost savings; project cost; available utility and government incentives; customer payback period; net customer investment after incentives.
  - Rank opportunities highest to lowest value.
  - Generate a simple customer-facing report: recommended project(s); estimated savings; available incentives; ROI and payback; recommended next steps.
- **Bonus points (DOC-1 p.5):** public property data; utility bill analysis; GIS mapping; AI-driven recommendations; automated incentive identification.
- **Data/APIs provided:**
  - No dataset or API is named in DOC-1 or LIVE. The only data artifact is the NOCO calculator screenshot (DOC-2, below).
  - LIVE `[01:19]` (answer to a data-set question from the room, unclear which challenge): "use chat GPT use cloud use the tool of your choice, give it the fields and say come up with a mock data set". Also `[00:49]`: "I will get an answer for you in a little bit" (answer not captured).
  - LIVE `[00:16]`-`[00:19]` (garbled): some teams "might offer you an opportunity to work on the project" / a data set "for you" if selected. Meaning unclear.
- **Constraints/rules:** none specific to NOCO beyond the above. "you do not need to have it fully fleshed out... five, six hours" (LIVE `[10:32]`-`[10:41]`).
- **Judging:** common 5-category rubric (section 2). LIVE `[10:48]` gives a NOCO-flavored example of a good demo: "no-cost energy calculator, where you can actually go in and look at your e-click down screen... here's the generation of function" (garbled; intent: clickable calculator that generates output).
- **Deliverables:** common (section 2): 4-minute pitch, PDF/PPT upload, prototype/visual.

#### NOCO reference test case: "NOCO Commercial Insulation Savings Sales Calculator" (DOC-2, Image 1)
Inputs as shown ("SALES INPUTS"): Location Buffalo, NY; profile Office/School/Daytime Commercial; 10,000 sq ft; incentive program "National Grid - Commercial Weatherization"; National Grid DAC? No; 1 floor; shape Very Long / Narrow; existing insulation R-11; proposed R-49 (last digit blurry); heating Electric Resistance, COP 1.00; cooling Packaged Rooftop Unit, COP 3.00; prices: gas $1.20/therm, electricity $0.16/kWh, propane $2.80/gal, fuel oil $3.40/gal, district energy $18.00/MMBtu.
Advanced overrides: Custom HDD 6,500 / CDD 700 (used only if Location = Custom); Custom load factor 1; area override 0; custom R-values 0; floor height override 0; window/door override 0%; exposed wall override 100%.
Outputs ("ESTIMATED ANNUAL SAVINGS"): heating 8,812 kWh/yr (hundreds digit uncertain); cooling 236 kWh/yr; total electric 9,048 kWh/yr; site energy 30.9 MMBtu/yr; cost savings $1,448/yr; incentive $15,600; simple 10-year energy value $14,476.
Calculation summary: eff. R 11.0 -> 49.0; U 0.091 -> 0.020, dU 0.071; HDD "6,xxx" (unreadable); CDD 600 or 650 (unclear); operating load factor 75%; footprint 10,000; est. perimeter 500 ft; floor height 12 ft; gross exposed wall 6,000 sq ft; window/door deduction 35%; insulated wall area 3,900 sq ft; incentive rate $4.00 (/sq ft per small note, rest unreadable).
Helper table: heating load saved 30,066,178 Btu/yr (middle digits uncertain); cooling load saved 2,412,718 Btu/yr; heating kWh 8,812; cooling kWh 235.7; heating $ 1,409.90; cooling $ 37.71; delta R 38; shape perimeter multiplier 1.0; net opaque wall factor 0.65; NG Gas Rate 1.9; NG Electric Rate 4.

**Approximate consistency check (arithmetic only, [INFERRED] reading; the screenshot probably uses unrounded internals, so small gaps are expected; do not alter source numbers to force a match):**
- Roughly consistent: perimeter 500 x 12 (wall area = perimeter x height, NOT floor area x height) = 6,000; x 0.65 = 3,900; 3,900 x $4 = $15,600; 1/11 = 0.091, 1/49 = 0.020, dU 0.071; 30,066,178 Btu / 3,412 = 8,812 kWh; 8,812 + 236 = 9,048; 8,812 x 0.16 = $1,409.92 (screen: 1,409.90) and 235.7 x 0.16 = $37.71, sum $1,447.6 = $1,448; 9,048 kWh x 3,412 = 30.9 MMBtu; 10 x $1,448 = $14,480 (screen: $14,476, so unrounded internals); 2,412,718 Btu / 3.0 COP / 3,412 = 235.7 kWh.
- Possibly wrong or unexplained (flag to NOCO): (a) "Estimated Perimeter 500 ft" with shape multiplier 1.0 for a "Very Long / Narrow" building; a square 10,000 sq ft footprint has a 400 ft perimeter, so the 500 base is unexplained. (b) "NG Gas Rate 1.9" and "NG Electric Rate 4" do not match the $1.20/therm gas price input; the 4 may be the incentive rate. (c) the 35% window/door deduction is used while the override input says 0%; unclear which wins. (d) HDD/CDD used are unreadable (custom inputs are 6,500/700 but Location = Buffalo, so they may differ). (e) the heating load looks like about 30.07M Btu; reproducing it needs the exact HDD, which is unreadable. (f) the screenshot gives an incentive ($15,600) but no project cost, cap or eligibility formula, so net investment and payback cannot be derived from it; a zero or negative payback is only a hypothetical needing partner rules. Project cost is required by DOC-1 p.5.
- Extra uncertainty: proposed R first digit, cooling-load middle digits, heating-dollar decimals, incentive unit ($4/sq ft is plausible, not verified). Conditions: custom load factor applies only when Profile = Custom; custom R-values and HDD/CDD only when selected; whether a 0 override means "use default" is undefined.

## 2. Judging and deliverables common to all challenges

**Rubric (DOC-2 Image 2; each category scored __/3, so max 15 [INFERRED]; LIVE confirms the five categories). "YOU will have access to a detailed copy of this rubric in UB Box."**
1. Impact and Feasibility: "clear and substantial impact on the problem statement and is highly feasible to implement". LIVE `[05:54]`-`[06:24]`: "Is it actually feasible?... does it actually do what the you say or so mock-ups. demonstrations".
2. Innovation and Creativity: "exceptional creativity and innovation in its approach, concept, and technology". LIVE `[06:32]`: "how innovative is this idea?"
3. Presentation and Communication: "exceptionally clear, engaging, and well-structured... including to non-technical judges". LIVE `[05:25]`: audience wants "understandability, how effective this would actually be"; `[05:15]`: "It's not just a purely technical challenge."
4. Potential for Future Development: "clear potential for future development and expansion". LIVE `[07:06]`-`[07:45]`.
5. Solution Execution: "high level of technical proficiency in design and user implementation with no mistakes". LIVE `[07:52]`-`[08:15]`: "mock-ups, wireframes, the home page... click on... this actually exists".

**Deliverables (LIVE):**
- "you're going to have a pitch in four minutes" `[10:21]`; also "you've got four minutes" `[08:40]`. Advice: "practice, practice, practice... four minutes goes by lightning quick" `[44:23]`-`[44:34]`.
- "a prototype, a visual that's shown how it works" `[10:28]`; "you do not need to have it fully fleshed out... five, six hours" `[10:32]`-`[10:41]`; a demo is encouraged `[10:41]`-`[11:01]`.
- Upload: "PowerPoint or PDF are the only two versions that we ask you to upload" `[09:01]`-`[09:04]`; "presentation should be a PDF or a PowerPoint format" `[11:02]`. Presenting: "you can plug your laptop in" `[08:41]`; screens available `[08:43]`.
- The balance: technical feasibility vs does it meet the client's need `[09:24]`-`[10:12]`.

**Prizes (LIVE `[11:19]`-`[13:42]`):** physical prizes (3D printer, hand scanner, mini drone, AI water bottles, Bluetooth speakers, power banks; some from NOCO are a surprise). "three tracks. two prizes per track. First place and a runner up" `[12:47]`-`[12:50]` (speaker first said "two tracks", then corrected). First place picks first from that challenge's prize pool `[12:34]`. Each organization has an undisclosed "experiential" prize (e.g. a NOCO tour or "lunch with their CEO" `[13:11]`-`[13:16]`). Possible internship/job: "could lead to an internship and a eventually a job offer" `[13:37]`.

---

## 3. Event logistics (clock times are as spoken; the recording has no wall-clock stamp)
| Fact | Quote (LIVE) |
|---|---|
| Date | Not stated in LIVE. [INFERRED] file names and "20261003" in DOC-1 suggest 2026-10-03. |
| Team submission deadline | "it is now 10-15. 10-30... by 1030, you should submit your team via this link here" `[27:19]`-`[27:22]` |
| Team size | "minimum team size is two people... Max is five. There is no flexibility" `[27:37]`-`[27:43]` |
| One submission per team | "One person. one team." `[28:11]`-`[28:13]` |
| Absent friends | "you need to account for them when you fill out the team formation link... you cannot add them later" `[29:37]`-`[29:45]` |
| Preference ranking | "scan the QR code... rank your preference... not a guarantee" `[14:50]`-`[15:03]` |
| Mentors | "between now and 3.30 when the final submission goes through. Mentors are going to be rotating", badges say "mentor" `[42:18]`-`[42:26]`; they "answer technical questions" `[42:44]`; company reps also present: "No code's already here" `[42:56]` |
| Submission method | "around 3 o'clock, I will post up. codes. for all of you to start submitting your presentations. So probably 2.45" `[45:07]`-`[45:19]` (garbled: "codes" likely submit link/QR [INFERRED]) |
| Final submission | "3.30 is the final submission date" `[45:07]` (see ambiguity in section 4) |
| Be in room | "All teams should be in this room no later than 3 p.m. today" `[45:39]` |
| Work location | "welcome to stay here... encourage you to stay in this room" `[45:25]`-`[45:27]` |
| Lunch | "should be around 1230. just outside where breakfast was. It was pizza" `[46:26]`-`[46:29]` |
| Work window | "five, six hours" `[10:41]` |
| Team-assignment info | Only "if you select it ... come over to this row" `[25:15]`; first-preference match announced `[25:10]`-`[25:14]` (names/assignments not in LIVE) |

---

## 4. Uncertain or missing (ask organizers / partners)
**Organizers**
1. Exact submission mechanism: where is the PDF/PPT uploaded (link, QR, Box)? Is the 2:45 posting the opening of submissions and 3:30 the hard deadline? Does the pitch happen after 3:30, and when?
2. Does "four minutes" include Q&A? A live demo is allowed (LIVE `[08:41]`, `[10:41]`: plug in a laptop / demo page; PDF/PPT is the uploaded copy). Confirm timing, video, slide limits.
3. Detailed rubric in UB Box: weights, and what "no mistakes" means for execution.
4. Event date and the wall-clock for the end, plus the "three tracks" prize pool for NOCO.
5. IP/ownership: LIVE `[00:05]` (garbled) "some of these companies have in the past kept taking within team ideas and then work, continue to work." Ask for the exact IP policy.
6. Answer to the dataset question promised at `[00:49]` (never captured). The only captured answer is to generate mock data with an LLM `[01:19]`.
7. Rules on cloud AI/APIs and keys: no policy stated; LIVE `[01:19]` only encourages ChatGPT/Claude to generate MOCK data, which is not permission to upload partner data. (Repo rule: no sensitive/partner data to cloud AI without permission; ask.)

**NOCO**
1. Is there a dataset, API, pricing table, or incentive list (National Grid, NYSERDA, federal) provided? None named. The NOCO packet at the back (`[46:54]`) may hold it; collect it.
2. Project cost: the screenshot shows no project cost, so how should payback be computed? What cost per sq ft per measure? Same for windows/HVAC/solar/EV/lighting/battery/generator.
3. The calculator formula questions in the consistency check above: perimeter 500 ft vs shape multiplier; gas rate 1.9 / "NG Electric Rate 4"; window/door 35% vs override 0%; HDD/CDD used; incentive rate unit ($4.00 per sq ft?) and the "$150/MMBtu" note (blurry). Which inputs are tweakable?
4. Blurry/unreadable digits to confirm from the original spreadsheet: proposed R-49; HDD used; CDD (600 or 650); heating savings hundreds digit; helper-table middle digits.
5. Are all opportunities (solar, EV, generators, batteries, gas, etc.) required, or is a working insulation slice plus ranking acceptable? Which is the "must-have" for the judges?
6. Who is the user: NOCO sales staff or the customer? Which cities/utilities (Buffalo / National Grid only)?
7. Is address -> public property data / GIS expected, or optional bonus only (DOC-1 p.5 says bonus)?

**Conversion/transcription cautions:** DOC-1 and DOC-2 carry Vietnamese converter notes saying text came from photos and some digits were blurry. No tables were lost in DOC-1; the DOC-2 spreadsheet is low resolution (480 x 853), so treat its digits as unverified. LIVE has long garbled stretches (e.g. `[00:00]`-`[01:47]`, `[04:15]`-`[04:48]`, `[47:52]` onward); no facts were taken from those beyond the quotes flagged above.

---

## Revision notes (Task 3)
CRITIQUE.md was available and its valid points were applied:
- Assignment: now stated as coming from the human's instruction, not the transcript; "reference test case" marked as a team proposal.
- Opportunity list reframed as examples ("such as"), not mandatory scope.
- Arithmetic fixed ($14,480; $1,409.92; wall area = perimeter x height) and labelled approximate; uncertain digits and conditional inputs added.
- Removed the implication that negative payback follows from the example; it needs partner rules.
- Cloud rules: mock-data encouragement noted; no upload permission implied.
- Live demo is allowed; only timing/Q&A remain open.
- Planning priorities from the critique: define the business problem first and split roles (technical / creative / presenting); use mentors and the NOCO rep early to settle formula and scope; the 3:30 deadline implies a 2:00 p.m. freeze under the repo rule (our calculation, not announced).
- Mishearings (critique): NOCO, "use cloud" = Claude (likely), "no-cost" = NOCO's (not a free-product requirement); 10:15/10:30; 3:30 p.m.; three tracks.
