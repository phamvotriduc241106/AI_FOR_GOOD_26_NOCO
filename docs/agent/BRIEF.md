# BRIEF

Source: `docs/agent/transcript_snapshot.txt` only. Note: the file is NOT a kickoff transcript. It is a
typed copy (with a Vietnamese header note) of 6 photos of the printed "AI for Good Hackathon Design
Challenge Statements" (3 challenges). It has no spoken content, so logistics, judging and team
assignment are absent. Marked [INFERRED] = my reading, not stated.

## 1. Challenges

### A. ACV (with Copart): "Reimagining the Future of Automotive Commerce with AI"
- **Partner:** ACV Auctions, together with Copart. Quote: "ACV Auctions and Copart bring together complementary strengths in digital automotive marketplaces, vehicle intelligence, inspections, logistics, physical infrastructure, and global buyer networks."
- **Problem as understood:** Open-ended. Quote: "How might we leverage AI to unlock 3–5× greater value from the combined capabilities of ACV Auctions and Copart, reimagining how vehicles are bought, sold, valued, and managed..."
- **Target users:** Not stated. Text mentions "customers" and "the broader automotive ecosystem". [INFERRED] buyers, sellers, and the two companies' operations.
- **Data / APIs provided:** None stated.
- **Constraints / rules:** "There is no prescribed technology, product, or business function that participants must focus on but demonstrate a clear connection to the value they aim to create." "Your solution does not need to fit within an existing ACV or Copart product."
- **Judging criteria:** None stated. Hints only (Key Takeaways): think big; use the combined ecosystem; create meaningful value (growth, outcomes, efficiency); use AI creatively. [INFERRED] these may reflect what is rewarded.
- **Deliverables:** None stated. Parameters say "develop creative AI-powered solutions", "meaningful and scalable impact".

### B. Against All Oddz Animal Alliance (AAO): "Intelligent Animal Rescue & Organizational Knowledge System"
- **Partner:** Against All Oddz Animal Alliance, a small nonprofit ("a small nonprofit with limited staff").
- **Problem as understood:** Requests to surrender or place animals arrive via "email, social media, phone calls, text messages, and referrals" and are "incomplete or fragmented". Animal and admin records are scattered across "Shelterluv, veterinary records, emails, text messages, spreadsheets, training notes, calendars, and paper files". Staff lose time gathering context before they can decide how to help.
- **Target users:** AAO staff ("authorized staff"). Requesters (surrendering owners, shelters, families) send the inputs; staff-only interaction is our proposed scope, not a source rule.
- **Data / APIs provided:** None stated. Named source systems only: Shelterluv, vet records, training notes, emails, spreadsheets, calendars, surrender records. No access, sample data or API terms given.
- **Constraints / rules:** "secure" system; "approved organizational sources"; "authorized staff"; responses drafted "for staff review"; flag concerns "requiring human review"; show "where an answer came from".
- **Judging criteria:** None stated. Context: "dozens" of daily requests, incl. financial/housing crises and attempts to avoid behavioral euthanasia, so compassionate handling matters; staff also check whether an animal had prior AAO contact, and the aim is helping more animals without losing individualized care. Stated goal: "reduce administrative burden, preserve institutional knowledge, allow staff to respond more quickly".
- **Deliverables:** "Design a secure AI-powered rescue intake and organizational knowledge system". "The system should" support an animal's journey from first contact through intake, evaluation, foster/sanctuary placement, vet and behavioral care, adoption or other resolution. "The system could" do the following (suggestions; minimum expected scope unconfirmed):
  1. Standardize multi-channel requests, find missing info, generate follow-up questions.
  2. Separate routine from urgent; flag medical, behavioral, bite-history, legal, safety concerns.
  3. Suggest pathway: adoption, foster, behavior modification, specialized rescue, sanctuary, other.
  4. Compare an animal's needs with AAO capacity, staffing, foster availability, finances, facilities.
  5. Keep full history of communications, decisions, actions per animal or case.
  6. Connect approved sources.
  7. Answer staff questions (e.g. "Does this dog have a bite history?").
  8. Flag conflicting, incomplete, outdated info with sources.
  9. Suggest alternatives when AAO cannot accept (trainers, behaviorists, breed rescues, retention programs, financial aid).
  10. Draft compassionate replies for staff review.
  11. Spot trends across cases.

### C. NOCO: energy savings and ROI for commercial buildings
- **Partner:** NOCO.
- **Problem as understood:** Quote: "How can NOCO use AI, building data, and available incentive programs to quickly estimate energy savings, project economics, and customer ROI for commercial buildings?"
- **Target users:** Not named. [INFERRED] NOCO sales/energy staff, and commercial building customers (the report is "customer-facing").
- **Data / APIs provided:** None stated. Bonus items hint at "Public property data", "Utility bill analysis", "GIS mapping", "Automated incentive identification", but no source is given.
- **Inputs (suggested):** building address, square footage, building type (office, warehouse, school, retail, etc.), year built, existing heating/cooling systems, utility usage or bills "(if available)".
- **Opportunities to evaluate:** insulation/weatherization, windows, HVAC upgrades, natural gas, electric, solar, EV charging, lighting, energy monitoring and management, generators, battery storage, "Other NOCO energy solutions".
- **Per recommendation, calculate:** annual energy savings; annual cost savings; project cost; "Available utility and government incentives"; customer payback period; net customer investment after incentives.
- **Constraints / rules:** None beyond the above. Rank "from highest to lowest value".
- **Judging criteria:** Full rubric and weights absent; bonus categories stated. "Bonus points for teams that incorporate: Public property data; Utility bill analysis; GIS mapping; AI-driven recommendations; Automated incentive identification".
- **Deliverables:** "Build an AI-powered tool", plus "a simple customer-facing report" with recommended projects, estimated savings, available incentives, ROI and payback, recommended next steps.

## 2. Event logistics
No logistics in the source. Nothing said about start/end time, deadline, demo freeze, submission method, presentation format, team size, or prizes. Only related text is the header "AI FOR GOOD / University at Buffalo / Startup and Innovation Collaboratory / Student Life" and footer logos (UB School of Management; UB School of Engineering and Applied Sciences; UB Institute for Artificial Intelligence and Data Science; ACV; Against All Oddz Animal Alliance; NOCO). The file name timestamps (20261003) hint the photos were taken 2026-10-03 [INFERRED]; this is not an event date or deadline. Six photos = five distinct pages (one duplicate).

## 3. Our team assignment
ASSIGNMENT: UNKNOWN

## 4. Uncertain or missing (ask organizers or partners)
Organizers:
- Which challenge is our team assigned, or do we choose? Can teams switch?
- Event schedule: start, demo freeze, submission deadline, presentation slot and length.
- Submission method (repo, slides, video, live demo?) and what must be handed in.
- Judging criteria and weights; who judges; prizes.
- Rules on AI tools and cloud LLMs, team size, and use of partner data.

ACV / Copart:
- Any data, APIs, or sample datasets? Or fully concept-level?
- Is a working prototype expected, or a concept/pitch? Which "customer" do they care about most?
- How is "3–5× greater value" measured?

AAO:
- Any sample or synthetic data (Shelterluv export, surrender forms, vet records)? Can it go to cloud AI (Claude/Groq) or only local models?
- Shelterluv API access, or file exports only?
- What is "current capacity" and where is it kept? Which of the 11 "could" items matter most?
- Privacy or security requirements for "secure".

NOCO:
- Data sources: utility rates, incentive databases (DSIRE etc. are not named; do not assume), building data, GIS layers. Any API keys or datasets?
- Cost and savings benchmarks per measure, and NOCO's product catalog and pricing (needed for project cost).
- Which region/utility territory (affects incentives)? Which building types first?
- Are bonus items scored extras or required for a strong entry?

## Revision notes
Revised after `CRITIQUE.md` (available) and a re-check against the transcript snapshot:
- AAO: staff-only use marked as proposed scope; added the explicit "should" journey requirement, crisis/scale context, prior-contact check, and broader knowledge-query examples; the "could" list is labeled as suggestions with unconfirmed minimum scope.
- NOCO: judging now reads "full rubric absent; bonus categories stated".
- Photo-date inference clarified as not a schedule fact. No transcription corrections (typed copy; nothing to verify against).
- Unchanged: assignment UNKNOWN, no logistics, no data or APIs supplied. Treat ACV's "3-5x" and all NOCO savings figures as undefined until partners confirm.
