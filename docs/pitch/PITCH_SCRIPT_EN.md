# NOCO Scout: 4-minute pitch script (team HELIX)

Speaking pace: about 140 words per minute. Total spoken text below: about 540 words.
**P** = presenter. **D** = demo driver (Nguyen-Le-Tuan, at the MacBook).
Numbers come from our code on `main` (2026-10-03, 14:20, default assumptions).

## Before going on stage (checklist)

- [ ] MacBook plugged in, display mirrored, notifications off, sleep off.
- [ ] `make run` is already running. Two browser tabs are open: `/Address_to_Quote` and `/Prospect_Map`. The "hackkit" tab is closed.
- [ ] On `/Address_to_Quote`, the address box already contains `33 Franklin St`.
- [ ] On `/Prospect_Map`, "Show potential customers" is **not** clicked yet (the reveal is part of the demo).
- [ ] Backup video `docs/pitch/demo_backup.mp4` is open in a second window.
- [ ] Until bug T18 is fixed, **click** buildings on the Prospect Map. **Do not hover** there.

---

## 0:00 to 0:15: Hook (slide 1: title over the 3D Buffalo map)

**P:** "Today, before NOCO can quote an energy upgrade, someone drives to the building, walks around it,
goes back to the office and does research. We are team HELIX, and we built NOCO Scout. It turns
an address into a quote in seconds."

## 0:15 to 0:40: Problem (slide 2)

**P:** "Your team told us that quoting takes time and needs one or two experts per building.
A sales rep can only visit so many buildings, so most of Buffalo has never been quoted.
The data to start that quote already exists. It is just scattered."

## 0:40 to 1:05: How it works (slide 3: flow diagram)

**P:** "We combine three public sources: the US Census geocoder, OpenStreetMap building outlines,
and the City of Buffalo assessment roll. They give us the perimeter, the footprint, the floors and
the building type, which are the inputs your calculator needs. Then we run **NOCO's own calculator**,
rebuilt cell by cell from your spreadsheet. Every number keeps its source."

## 1:05 to 2:55: Live demo (110 seconds)

**P:** "Let me show you." *(switch to the browser)*

### D1: one address, one quote (40 s), tab `/Address_to_Quote`

| D does | P says |
|---|---|
| Click **Find building** (`33 Franklin St` is already typed) | "A rep types an address. That's all." |
| The map flies to it; an 11-floor block rises | "Public data found the building: its outline, eleven floors, office use." |
| Point at the **Facts and confidence** table | "Every fact shows where it came from and how confident we are." |
| Click **Estimate insulation upgrade** | "Upgrading the walls from R-11 to R-49 saves about **ten thousand dollars a year**, and National Grid pays about **a hundred and ten thousand** in incentives." |
| Point at "Needs installed cost" | "We do not invent the installation cost. Until NOCO enters it, the app says so." |

### D2: the whole city (50 s), tab `/Prospect_Map`

| D does | P says |
|---|---|
| Click **Show potential customers** | "Now the manager's view. The same calculator, for 300 buildings in 11 Buffalo neighborhoods." |
| The blocks turn blue → orange; the ranked table appears | "Orange means bigger savings. This is a call list, ranked." |
| Click the tallest orange tower (**#1, 1 Seneca St**) | "Number one is Seneca One, the tallest building in Buffalo: about **$235,000 a year** in savings. Its incentive stops at **$150,000**, exactly the National Grid cap in your spreadsheet." |
| Point at the **Building details** panel | "Each building has its facts and sources. The current supplier is not public, so the app says: ask the customer. We never guess." |
| Click a second orange building | "A rep can pick the next call in a few seconds." |

### D3: the reports (20 s)

| D does | P says |
|---|---|
| Click **Download manager report (HTML)** and open it for 3 s | "The manager gets a ranked report and a CSV, with every assumption labelled." |
| Click a building, click **Generate customer report**, open it for 5 s | "And the building owner gets a one-page report in plain English, with the NOCO logo, ready to send." |

**If the app fails at any point:** D switches to the backup video. P says: "Here is the same run, recorded this morning."

## 2:55 to 3:15: Trust (slide 4)

**Only if NOCO allowed us to show its numbers (question A6):**
**P:** "Why trust it? We rebuilt your spreadsheet and matched your Buffalo example exactly:
9,047.6 kilowatt-hours, $1,447.60 a year, and a $15,600 incentive. The fuel tiers, the
disadvantaged-community bonus and the caps all follow your workbook."

**If A6 was not answered (default):**
**P:** "Why trust it? The calculator is plain, tested code that reproduces NOCO's own example to the
cent. The fuel tiers, the disadvantaged-community bonus and the caps all follow NOCO's workbook.
The AI only reads notes. It never decides a number."

## 3:15 to 3:30: Impact (slide 5)

**P:** "One tool, three people. The rep gets a quote in seconds. The manager gets a ranked list of
prospects. The owner gets a clear reason to upgrade. And every quote that leads to a retrofit means
less energy wasted in Buffalo."

## 3:30 to 3:50: Innovation and future (slide 6)

**P:** "Insulation is the first measure. The same pipeline adds windows, HVAC and rooftop solar,
the NYSERDA and National Fuel incentives, and a map of disadvantaged communities, which NOCO told
us is a priority. Then it can go to every city NOCO serves."

## 3:50 to 4:00: Close (slide 7)

**P:** "Give us fifty Buffalo buildings and one week with your sales team. We will show you what a
quote from an address looks like. Thank you. We are HELIX."

---

## Expected questions: short, honest answers

| Question | Answer |
|---|---|
| Where do revenue and profit come from? | "They are illustrative. NOCO mentioned a 30 to 40 percent margin, but no installed cost yet, so the app labels them illustrative." |
| How accurate is it? | "On NOCO's example we match the spreadsheet exactly. For other buildings, the inputs come from public data and each one shows its confidence. A rep confirms them on the first call." |
| What heating system do you assume? | "Electric resistance, like NOCO's example, and the app flags it. For a gas-heated building the savings are lower; the calculator already supports gas." |
| What if the map data is wrong? | "Each number shows its source, so a rep sees what to check. Complex landmarks like City Hall, which OpenStreetMap splits into parts, are next on our list." |
| Do you know the customer's current supplier? | "No. That is not public, so the app says 'ask the customer'." |
| Privacy? | "Public records only. We never store owner names or mailing addresses." |
| Why only insulation? | "It is the measure NOCO gave us a calculator for. The pipeline is built to add more." |
| Does it need the internet? | "No. The demo data is saved, and the app runs fully offline." |
