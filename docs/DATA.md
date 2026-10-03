# T6: NOCO source answers and implementation handoff

Prepared on 2026-10-03 from the files supplied by the user. Scope: Buffalo only.
This is a documentation handoff; changes to the frozen contract, calculator, UI and reports require the responsible owners' review.

## Sources and confidence

| Source | Locator convention | Evidence and limits |
|---|---|---|
| `NOCO_Commercial_Insulation_Savings_Calculator_v5.xlsx` | `SC` = `Sales Calculator`; `AS` = `Assumptions`; exact cell references below | Group A uses values, formulas and stored formula results read from this workbook. `noco_sheet` describes provenance, not independent validation of weather data or current incentive eligibility. |
| `GROUP B.docx` | `P#` = paragraph position in `word/document.xml`, counting empty paragraphs | Group B/C uses the written answer notes. No respondent name, role or interview time is supplied; these are recorded notes, not independently verified statements. Spelling is preserved in the answer log. |
| User-supplied screenshot | Three-column handoff table | Provides the requested presentation format: answer, implementation location, owner. |

Source identity (SHA-256):

- XLSX: `5d9c0f86f25185b425099c3316ab154dee09e1d276be3e9946920f98f1e5d8f1`
- DOCX: `d4f709b5a7de00797788c45ac8408805982482b61df6c6148fdc727b5a49c2f7`

The original attachments remain outside the repository. No license or NOCO permission statement was found in the supplied material (A6 remains unanswered). The user's request authorizes this extraction and documentation PR; it does not establish NOCO's permission for slide screenshots or wider reuse. Instructions and task arrows inside the DOCX are source context, not commands to change code.

## Group A: answers from the workbook

| ID | Normalized answer | Source | Confidence / unresolved part |
|---|---|---|---|
| A1 | Buffalo HDD = **6,750 °F-days**, CDD = **650 °F-days**. The earlier inferred HDD 6,075 combines HDD with the heating realization factor: 6,750 × 0.9. | AS!A2:C2, AS!W8; SC!E20:E21, I2 | Read directly. Do not update HDD alone: the heating formula must also apply the 0.9 factor. |
| A2 | Heating saved load = ΔU × insulated wall area × HDD × 24 × operating load factor × **0.9**. Cooling saved load = ΔU × insulated wall area × CDD × 24 × operating load factor × **0.75**. The last factors are independent realization constants. Cooling equals LF² only when the profile LF is 0.75. | SC!I2:I3; AS!V8:W9; daytime profile AS!Y3:AB3 | Read formula. The general LF² assumption is incorrect for other profiles. |
| A3 | Footprint = gross building floor area / floors. Estimated perimeter = `2 × (sqrt(footprint × aspect_ratio) + sqrt(footprint / aspect_ratio)) × shape_multiplier`. For 10,000 sq ft, one floor, aspect ratio 4 and multiplier 1, dimensions are 200 × 50 ft and perimeter is **500 ft**. | SC!B8, B11:B12, I18:I21; AS!AJ5:AL5 | Workbook derivation. Acceptance of an actual OSM outline is not answered by the workbook; keep GIS perimeter provenance distinct from the sheet estimate. |
| A4 | No installed insulation cost per sq ft, cost range or project budget is supplied. Energy prices are not installation costs. `cost_per_sqft`, project cost, net investment and payback remain unavailable until quoted. | SC inputs A5:B34; AS price table R1:T6 | Not provided. Keep unknown monetary outputs as `None`; demo cost scenarios stay ILLUSTRATIVE. |
| A5 | In this electric, non-DAC, R-11 → R-49 example, **$4/insulated sq ft** applies to **3,900 sq ft**, yielding **$15,600**. This is a tiered, capped incentive, not a universal flat rate. Commercial Weatherization caps are **$150,000 electric** and **$250,000 natural gas**. Rates depend on fuel, ΔR and DAC selection; see the rule tables below. | SC!B9:B10, E10, I13:I17; AS!AD4:AH9 | Read formula. Full eligibility, DAC qualification and current program terms are not established by this workbook. |
| A6 | Permission to show screenshots/numbers in slides, or sponsor permission for AI processing, is not stated. | No permission statement in supplied workbook | Unanswered; do not turn silence into approval or refusal. |

### Formula and example reconciliation

The current repo's `hdd=6075` and heating formula reproduce this one sample because `6750 × 0.9 = 6075` (AS!B2, W8; SC!I2). The repo's LF² cooling formula also matches this sample because the daytime LF and cooling realization factor both equal 0.75 (AS!Z3, W9; SC!I3). Matching the sample does not prove general workbook equivalence.

| Example result | Workbook value (stored formula result) | Source |
|---|---:|---|
| Insulated wall area | 3,900 sq ft | SC!I13, E30 |
| ΔU | 0.0705009276437848 Btu/hr-ft²-°F | SC!E19 |
| Heating saved load | 30,066,178.107606683 Btu/yr | SC!I2 |
| Cooling saved load | 2,412,717.9962894255 Btu/yr | SC!I3 |
| Heating electricity | 8,811.89276307347 kWh/yr | SC!E5 |
| Cooling electricity | 235.70906567892004 kWh/yr | SC!E6 |
| Total electricity | 9,047.601828752391 kWh/yr | SC!E7 |
| Annual site energy | 30.87041743970316 MMBtu/yr | SC!E8 |
| Annual energy cost savings | $1,447.6162926003824/yr | SC!E9 |
| Incentive | $15,600 | SC!E10 |
| Simple ten-year energy value | $14,476.162926003824 | SC!E11 |

Other sample inputs: 12 ft floor height, 100% exposed wall, 35% window/door deduction, R-11 → R-49, heating COP 1, cooling COP 3 and electricity $0.16/kWh (SC!I22:I26, E15:E16, B16, B18, B20). B33 = 0 means no window override; SC!I25 therefore selects the 35% daytime preset. B29 = 0 means no actual insulated-area override (SC!I13). These stored results were checked against independent deterministic arithmetic; Excel was not recalculated or edited.

### National Grid Commercial Weatherization rules read from the sheet

All rates below are dollars per insulated wall sq ft. ΔR is `MAX(0, proposed_R - existing_R)` (SC!I15). DAC here means the workbook's `National Grid DAC?` selector (SC!A10:B10), not an inferred classification of an address.

| Natural gas ΔR range | Standard rate | DAC rate | Source |
|---|---:|---:|---|
| Below 4 or above 60 | 0 | 0 | SC!I16 |
| 4 ≤ ΔR < 11 | 0.15 | 1.15 | SC!I16; AS!AD4:AH4 |
| 11 ≤ ΔR < 21 | 1.50 | 2.50 | SC!I16; AS!AD5:AH5 |
| 21 ≤ ΔR < 31 | 1.75 | 2.75 | SC!I16; AS!AD6:AH6 |
| 31 ≤ ΔR < 41 | 1.90 | 2.90 | SC!I16; AS!AD7:AH7 |
| 41 ≤ ΔR ≤ 60 | 2.00 | 3.00 | SC!I16; AS!AD8:AH8 |

| Electric ΔR range | Standard rate | DAC rate | Source |
|---|---:|---:|---|
| Below 4 | 0 | 0 | SC!I17 |
| 4 ≤ ΔR < 11 | 2 | 3 | SC!I17; AS!AD9:AH9 |
| 11 ≤ ΔR < 21 | 3 | 4 | SC!I17; AS!AD9:AH9 |
| ΔR ≥ 21 | 4 | 5 | SC!I17; AS!AD9:AH9 |

SC!E10 applies `MIN(insulated_area × rate, cap)` for the two fuels and zero for other heating fuels under Commercial Weatherization. SC!I14 also lists NYSEG/RG&E C&I $0.80/sq ft and Small Business $1.25/sq ft, and National Grid Multifamily $150 per annual MMBtu saved (AS!AD2:AH3, AD10:AH10). Those entries are workbook references, not a claim that every Buffalo property qualifies; no current external program verification was performed.

## Groups B and C: answers from the DOCX

| ID | Recorded answer | Normalized meaning and remaining question | Source |
|---|---|---|---|
| B1 | `1-2 experts on specifics field like electricity, heating systems + all others building data to give out the best respopnses.` | Involve one or two relevant experts and building data. The slowest quote step and fraction of visits not ending in a sale are **not answered**; do not invent timing or conversion metrics. | DOCX P4 |
| B2 | `greens column` | Manager wants the green outputs. Likely refers to annual savings outputs SC!D5:F11, but this mapping is an interpretation, not an explicit column list from the interview. Confirm the intended fields. | DOCX P6; workbook SC!D5:F11 |
| B3 | `30-40% on margin.` | Recorded margin range **30–40%** (fraction 0.30–0.40). No project size, cost basis, gross/net definition or named confirmer. Do not pick a midpoint as a confirmed default; retain ILLUSTRATIVE project revenue/profit until both cost and margin basis are confirmed. | DOCX P8 |
| B4 | `based on the building -> then will find the most suitable providers for the utilities.` | Provider means a suitable utility/provider recommendation based on the building. This does not identify the current supplier or supply selection criteria; current supplier remains `Not in public data: ask the customer`. | DOCX P12 |
| B5 | `prioritized: disadvangetage commu.` / `goal: for any comercial` | Prioritize disadvantaged communities; overall target is commercial buildings. No Buffalo neighborhood names or classification dataset are supplied; do not infer DAC status or geographic boundaries. | DOCX P15:P16 |
| B6 | `in sheet` | Points to the supplied workbook for data/formulas. Does not establish an installed-cost table or license. | DOCX P18 |
| C1 | `all of them.` | Future roadmap includes the measures named in the question: windows, HVAC, lighting, solar and batteries. No priority order; insulation remains the current scope. | DOCX P20:P21 |
| C2 | `national fuel, NYSErDA` | Normalize names to **National Fuel** and **NYSERDA**. Specific programs, amounts, eligibility and applicable federal incentives remain unprovided. | DOCX P23 |
| C3 | `super easy to use + quick + pretty for internal + customers.` | Demo should be easy, fast and visually clear for internal users and customers. No numerical performance target. | DOCX P25 |
| C4 | `NOCO logo` | Use the NOCO logo; DOCX contains an embedded logo image inspected during extraction. No style guide, follow-up contact or explicit reuse license is supplied. | DOCX P26; `word/media/image1.png` |

All B/C rows have confidence **read from supplied notes**. Respondent/role and interview time are **not recorded**. The embedded logo's supplier tagline is branding evidence, not evidence of any building's current supplier.

## Implementation handoff (format requested in the screenshot)

These are proposed follow-up changes for the owners below. This PR implements the documentation only. Owners follow `docs/TASKS.md`; contract changes need human-A approval.

| Câu trả lời | Sửa ở đâu | Ai làm |
|---|---|---|
| A1: HDD 6,750; CDD 650; heating realization 0.9 | `Assumptions.hdd` and provenance in `contract.py`, sample HDD in `fixtures.py`, and Golden tests. Coordinate with A2 so the heating result remains unchanged. `docs/TASKS.md` contract remains frozen pending approval. | Anh-08 / human-A approve contract; phamvotriduc241106 updates T2 tests |
| A2: Cooling LF × 0.75, heating LF × 0.9 | `estimate_insulation` in `calc.py`, source labels, and tests with a non-daytime LF to distinguish constant realization from LF². Decide representation of realization constants with human-A before any contract change. | phamvotriduc241106 (T2); human-A for contract decision |
| A3: Shape formula explains 500 ft; GIS acceptance unanswered | Document sheet estimate versus actual OSM polygon in T3/T2 provenance. Request NOCO acceptance; do not replace GIS geometry with the sheet estimate silently. | Anh-08 (T3), phamvotriduc241106 (T2), NguyenQBao follow-up |
| A4: No installed cost; B3: recorded margin 30–40% | `cost_per_sqft` stays `None`; margin range is a sourced scenario pending clarification. Cost/payback in calculator and revenue/profit in `prospect.py`, tooltips and reports keep required uncertainty labels. | Anh-08 (contract/report); phamvotriduc241106 (T2/T5); NguyenQBao confirms basis |
| A5: Tiered incentive; electric/gas caps and DAC selection | Incentive logic in `calc.py`, Golden/boundary tests and report text. Fuel, ΔR, DAC and cap representation may require a contract decision; never infer DAC qualification from B5. | phamvotriduc241106 (T2); Anh-08 (T10); human-A approves contract changes |
| A6: Permission not recorded | Pitch slide containing the NOCO screenshot/numbers remains pending permission confirmation. A missing answer is neither refusal nor approval. | NguyenQBao (T6/T8) |
| B1: Expert involvement; no time/conversion metrics | `docs/PITCH.md` story can reflect the need for expertise; quantitative bottleneck claims require follow-up evidence. | NguyenQBao (T8) |
| B2: Green outputs; exact columns unclear | Confirm manager columns for `render_manager_report` / `prospects_to_csv`; provisional savings fields come from SC!D5:F11. | Anh-08 (T10), NguyenQBao confirms |
| B4: Recommend suitable utility providers | `Opportunity` in `prospect.py` and map tooltip/panel text. Preserve current-supplier unknown text; provider recommendations require criteria and verified territory data. | phamvotriduc241106 / Codex (T5/T4); human-A for new fields |
| B5: Disadvantaged communities; any commercial building | T7 prospect area/filters require an explicit public classification source and Buffalo boundary. No neighborhood or DAC inference from these notes alone. | Anh-08 (T7); NguyenQBao supplies criteria |
| B6: Data/formulas are in sheet | This source register and A answers; no additional price table assumed. | NguyenQBao (T6) |
| C1: All listed future measures | Future roadmap in `docs/PITCH.md`; no new calculator measures in this PR. | NguyenQBao (T8) |
| C2: National Fuel and NYSERDA | Future incentive roadmap; verify program details before adding rates to calculator/report. | NguyenQBao (T6/T8) |
| C3: Easy, quick, attractive | Existing demo flow and UI presentation, with customer and internal views. | phamvotriduc241106 (T4), NguyenQBao (T8/T9) |
| C4: NOCO logo, no contact | Customer report branding and pitch after rights confirmation; follow up for contact/style guide. | Anh-08 (T10), NguyenQBao (T8) |

## Five-line handoff: differences and gaps

1. A1/A2: HDD is 6,750 with heating realization 0.9; general cooling is LF × 0.75, so the old formulas only explain the sample.
2. A3: The 500 ft perimeter is a 4:1 shape estimate; approval to substitute real GIS geometry is still missing.
3. A4/B3: No installed cost; margin notes give 30–40% without basis, so payback stays unknown and opportunity amounts stay ILLUSTRATIVE.
4. A5/A6: Incentives are tiered and capped; full eligibility and permission to reuse NOCO material remain unresolved.
5. B2/B4/B5: Green report columns need clarification; provider is a suitability recommendation, and disadvantaged communities need explicit targeting criteria.

---

## Addendum (Nguyen-Le-Tuan's assistant, merged after Bao's PR): impact, reference tables and verified public sources

> Bao's sections above are the base (cell-level evidence). This addendum adds what they do not contain. An independent reading of the same workbook reached the same five findings.

### Tóm tắt 5 dòng cho người điều phối (tiếng Việt)
1. **HDD thật 6.750**, nhân hệ số 0,9 (hiệu dụng 6.075). CDD 650 đúng.
2. **Làm mát = LF × 0,75**, không phải LF². Sai lệch tối đa khoảng ±$17/năm mỗi toà, nhỏ về tiền nhưng sai về công thức.
3. **Ưu đãi phụ thuộc nhiên liệu, ΔR, DAC và có trần** ($150.000 điện, $250.000 gas). Toà dùng gas chỉ được $1,90/sq ft: mô hình cũ cao hơn 111%. **Lệch lớn nhất.**
4. **Chu vi 500 ft là công thức theo tỷ lệ cạnh**; ô ghi đè diện tích cách nhiệt có sẵn, nên chu vi GIS là thay thế hợp lệ (NOCO chưa xác nhận bằng lời).
5. **Nhóm B/C:** biên lợi nhuận 30 đến 40% (chưa rõ cơ sở), ưu tiên cộng đồng thiệt thòi, National Fuel và NYSERDA, logo NOCO. **"Greens column" rất có thể là các ô đầu ra màu xanh `SC!D5:F11`** (diễn giải của Bao, hợp lý hơn đoán ban đầu là cột lợi nhuận).
   Chưa có: chi phí lắp đặt (A4), cho phép dùng số của NOCO (A6), câu trả lời của ban tổ chức (O1 đến O4).

### Impact of the old model versus the real workbook (computed)
| Difference | Size |
|---|---|
| Cooling uses LF squared instead of LF x 0.75 | 0% at LF 0.75; +13.3% at 0.85; -13.3% at 0.65; +33.3% at 1.0; -33.3% at 0.5 of the cooling load (about +/- $17 per year per building at most) |
| Flat $4/sq ft incentive | Gas building, dR 31-40, non-DAC: real $1.90/sq ft (flat rate is 111% too high). Electric building with 40,000 sq ft of wall: flat gives $160,000, the sheet caps at $150,000 |
| Default heating = electric resistance (COP 1.0) | Same load costs roughly 3x more on $0.16/kWh than on $1.20/therm gas at 0.8 efficiency, so electric defaults inflate savings for gas-heated Buffalo buildings. T12 must make the heating system explicit and labelled as an assumption |
| One operating profile for every building | Warehouse profile is 20 ft floors and 8% windows (Office is 12 ft and 35%): wall area differs by about 2.4x. The demo set contains warehouses, 33 apartments and 10 common-wall row buildings |

### Reference tables from the workbook (sheet `Assumptions`)
- **Operating profiles** (load factor, floor height ft, window/door %): 24/7 Multifamily/Hospitality 1.0 / 10 / 25%; **Office/School/Daytime 0.75 / 12 / 35%**; Retail/Restaurant extended hours 0.85 / 14 / 30%; Warehouse/Light Industrial 0.65 / 20 / 8%; Intermittent/Seasonal 0.5 / 12 / 20%; Custom 1.0 / 12 / 20%.
- **Building shape** (aspect ratio / perimeter multiplier): Square 1/1; Typical Rectangle 1.5/1; Long Rectangle 2.5/1; **Very Long/Narrow 4/1**; L-Shaped 1.5/1.15; U/C 1.5/1.3; Courtyard 1.5/1.45; Irregular 1.5/1.5.
- **Heating systems** (default efficiency/COP): gas furnace 0.8 (high eff. 0.95); gas boiler 0.82 (condensing 0.94); propane 0.85; fuel oil 0.82; **electric resistance 1.0**; air-source heat pump 3.0; ground-source 4.0; district 0.9.
- **Cooling** (COP): rooftop 3.0; split/DX 3.2; air-cooled chiller 3.5; water-cooled chiller 5.5; heat pump 3.5. **Degree days** (HDD/CDD): Buffalo 6750/650; Rochester 6500/700; Syracuse 6650/700; Binghamton 6800/600; Watertown 7200/500; Albany 6500/850; Plattsburgh 7600/450.
- Constants: 3,412 Btu/kWh; 100,000 Btu/therm; heating realization 0.9; cooling realization 0.75. "Opaque Wall Factor 0.8" exists in the sheet but is not used by the formulas read.

### Manager report columns (B2, adopted interpretation)
Use the workbook's output block `SC!D5:F11` as the manager columns: heating energy savings, cooling energy savings, total electric savings, annual site energy savings (MMBtu), annual energy cost savings, estimated incentive, simple 10-year energy value, plus address, neighborhood, use class, floors and join confidence. NOCO revenue/profit stays an extra column labelled ILLUSTRATIVE. Never show NOCO revenue, profit or margin in the CUSTOMER report.

### Public data sources and licences (verified today)
| Source | Use | Note |
|---|---|---|
| US Census Geocoder | address to coordinates | public, no key |
| OpenStreetMap via Overpass | footprints, levels, type | ODbL: show "(c) OpenStreetMap contributors"; needs a User-Agent header |
| City of Buffalo Final Assessment Roll (Socrata `4t8s-9yih`) | use class, story height, address, neighborhood | only `address`, `zip_code_5_digit`, `neighborhood`, `prop_class_description`, `story_height`; never `owner*`, `mail*` |
| **NYSERDA Final Disadvantaged Communities (DAC)** | per-tract DAC flag (B5) | VERIFIED queryable: `https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYSERDA_Final_Disadvantaged_Communities/FeatureServer/0`, fields `GEOID`, `DAC_Desig`; three Buffalo points returned "Designated as DAC". The sheet also has a `National Grid DAC?` selector that raises the incentive (electric $5 instead of $4, gas $2.90 instead of $1.90) |

**Not built (only data-feasibility proven):** a DAC flag per building, a map badge and filter, and the higher incentive. It fits B5 and the AI for Good theme. Do it only if T10 and T12 finish early; otherwise show it on the "future" slide.
