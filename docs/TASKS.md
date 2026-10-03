# Tasks (humans edit this file on `main` only; agents read it)

**DRAFT chờ duyệt.** Plan: NOCO "Address-to-Quote" cho Buffalo (xem `docs/spec.md`). Sau khi duyệt, chạy `make lanes`: nó dựng khối
"luồng việc hiện tại" trong `docs/DAY_OF.md` (ai làm gì, việc nào song song, ai chờ ai, lệnh copy–paste).
Mỗi việc nhỏ (agent thường cần 5-15 phút; PR, CI và merge tốn thêm ~5 phút). Hai việc chạy song song CHỈ khi cột "Files" không trùng.

## Team (đội hình: `make lanes` đọc bảng này, giữ ba cột)
| Role | Person | Tool |
|------|--------|------|
| claude | Anh-08 | Claude Code |
| codex | phamvotriduc241106 | Codex |
| human-A | Nguyen-Le-Tuan (tôi) | |
| human-B | NguyenQBao | |
| human-C | NguyenQBao | |
| partner-qa | NguyenQBao | |
| researcher | NguyenQBao | |
| backup-integrator | NguyenQBao | |

Vai trò: **claude** = Anh-08 chạy Claude Code. **codex** = phamvotriduc241106 chạy Codex, là **coder chính**. **human-A** = Nguyen-Le-Tuan: chủ sản phẩm,
kiểm tra PR, merge vào `main`, kiểm soát luồng việc, chạy `make test && make lint` và `make lanes`. **human-B** = QA và người chạy demo. **human-C** = slide và pitch
(NguyenQBao làm slide). **partner-qa** = hỏi người của NOCO và ban tổ chức. **researcher** = tìm và xác nhận dữ liệu công khai, ưu đãi, chi phí.
**backup-integrator** = merge PR xanh khi human-A bận, không merge PR của chính mình. NguyenQBao giữ các vai trò không code (human-B, human-C, partner-qa, researcher,
backup-integrator) để hai coder không bị gián đoạn.

**Hai agent viết code song song**, trên các nhóm file tách biệt và hợp đồng bên dưới được đóng băng ở T1. Mỗi người chạy tuần tự việc của mình theo thứ tự:
**Anh-08 (Claude):** T1 → T3 → T7 → T10 → R1. **phamvotriduc241106 (Codex):** T2 → T4 → T5 → T11 (COULD).
**Khối lượng:** phamvotriduc241106 nặng nhất (bản đồ T4 là việc lớn nhất). Quy tắc: nếu 13:15 các việc MUST chưa xong thì bỏ T5, T11 và phần SHOULD của T10.
Review chéo bằng agent chỉ còn R1 (kiểm tra máy tính với con số Golden); phần quy tắc dữ liệu do human-A kiểm tra bằng danh sách khi review PR (xem `docs/DAY_OF.md`, mục 6).

## Contract (đóng băng sau khi T1 merge; không ai đổi nếu human-A chưa đồng ý)

```text
Feature key: noco_scout        Package: src/features/noco_scout/        Địa lý: CHỈ thành phố Buffalo
Không thêm thư viện mới. Có sẵn: streamlit 1.65, pydeck 0.9, pandas, pydantic, httpx. KHÔNG có: shapely, pyproj, geopandas, reportlab -> hình học viết bằng Python thuần.
Tiền và số đo là float (như bản in); mọi hằng số công thức phải có nhãn nguồn (noco_sheet / assumed).

contract.py  (T1)
  Source = Literal["geocoder", "osm", "assessor", "user", "assumed", "noco_sheet"]
  FieldSource(source: Source, confidence: float [0..1], note: str = "")
  BuildingFacts:
      address: str; lat: float; lon: float; osm_id: int | None; neighborhood: str | None
      footprint_geojson: dict | None            # GeoJSON Polygon, thứ tự [lon, lat]
      footprint_sqft: float | None; perimeter_ft: float | None; floors: int | None; floor_height_ft: float | None
      use_class: str | None                     # ví dụ "OFFICE BUILDING" (bảng đánh giá). KHÔNG BAO GIỜ có owner/mail
      sources: dict[str, FieldSource]           # khóa = tên các trường ở trên; thêm khóa "join" cho độ chắc chắn của phép nối OSM <-> bảng Buffalo
  Prices: electricity_per_kwh=0.16, gas_per_therm=1.20, propane_per_gal=2.80, oil_per_gal=3.40, district_per_mmbtu=18.0
  Assumptions: floor_height_ft=12.0, window_door_pct=0.35, exposed_wall_pct=1.0, existing_r=11.0, proposed_r=49.0,
      hdd=6075.0, cdd=650.0, operating_load_factor=0.75, heating_fuel: "electric"|"natural_gas" = "electric",
      heating_efficiency=1.0, cooling_cop=3.0, prices: Prices, incentive_per_sqft=4.0,
      cost_per_sqft: float | None = None, margin_pct: float | None = None     # None => không bịa: hoàn vốn / lợi nhuận là None
  CalcInputs: perimeter_ft, floors, floor_height_ft, exposed_wall_pct, window_door_pct, existing_r, proposed_r, hdd, cdd,
      operating_load_factor, heating_fuel, heating_efficiency, cooling_cop, prices, incentive_per_sqft, cost_per_sqft | None
  CalcResult: insulated_wall_area_sqft, delta_u, heating_load_btu, cooling_load_btu, heating_kwh, heating_therms, cooling_kwh,
      total_kwh, site_mmbtu, annual_cost_savings, incentive, project_cost | None, net_investment | None,
      simple_payback_years | None, ten_year_energy_value, flags: list[str], assumptions: list[str]
  Opportunity: utility: str ("National Grid", nhãn noco_sheet); incentive_program: str | None;
      current_supplier: str = "Not in public data: ask the customer"      # KHÔNG đoán nhà cung cấp hiện tại
      project_revenue: float | None; estimated_profit: float | None; margin_pct: float | None; illustrative: bool; notes: list[str]
  Prospect: facts: BuildingFacts; inputs: CalcInputs; result: CalcResult; opportunity: Opportunity; score: float; rank: int

fixtures.py  (T1)  NOCO_EXAMPLE_INPUTS, NOCO_EXAMPLE_EXPECTED (bảng "Golden" dưới đây), SAMPLE_BUILDINGS (5 tòa nhà giả ở Buffalo, có đa giác và số tầng)

calc.py      (T2)  estimate_insulation(i: CalcInputs) -> CalcResult            # hàm thuần: không I/O, không mạng
                   inputs_from_facts(f: BuildingFacts, a: Assumptions) -> CalcInputs
                       # thiếu chu vi/số tầng -> dùng giá trị assumed + thêm cờ; không bao giờ ném lỗi
geo.py       (T3)  geocode(address: str) -> tuple[float, float, str] | None     # US Census; (lat, lon, địa chỉ khớp)
                   fetch_footprint(lat, lon, radius_m=25) -> dict | None         # OSM: osm_id, geojson, footprint_sqft, perimeter_ft, floors|None, building_type
                   fetch_property(lat, lon) -> dict | None                       # bảng Buffalo: CHỈ hai khóa {use_class, story_height_ft}
                   build_facts(address: str, *, offline: bool = False) -> BuildingFacts
                   load_demo_buildings() -> list[BuildingFacts]                  # đọc data/public/demo_buildings.json
                   Mọi lời gọi mạng qua MỘT hàm _http_get_json(url, params) có bộ nhớ đệm đĩa ở data/public/cache/ và giãn cách >= 1 giây với Overpass.
                   Test KHÔNG BAO GIỜ dùng mạng: chỉ dùng phản hồi đã ghi trong tests/fixtures/noco/.
prospect.py  (T5)  build_opportunity(f: BuildingFacts, r: CalcResult, a: Assumptions) -> Opportunity
                   rank_prospects(items: list[BuildingFacts], a: Assumptions, top: int = 25) -> list[Prospect]   # score = annual_cost_savings; hòa thì hoàn vốn ngắn hơn
mapdata.py   (T4)  prospects_to_deck_rows(prospects: list[Prospect]) -> list[dict]    # mỗi dòng: polygon, elevation, color, tooltip_html
                   prospect_tooltip_html(p: Prospect) -> str                          # thứ tự cố định trong docs/spec.md; luôn có dòng nguồn
report.py    (T10) render_customer_report(facts, inputs, result, opportunity=None) -> str   # HTML tự chứa, in được, "© OpenStreetMap contributors", danh sách giả định
                   render_manager_report(prospects: list[Prospect], a: Assumptions) -> str  # HTML tự chứa, in được
                   prospects_to_csv(prospects: list[Prospect]) -> str
app/pages/   (T4)  "Address to Quote" (bản đồ 3D + bảng nguồn + ước tính + nút báo cáo cho khách) và "Prospect Map" (bản đồ Buffalo xếp hạng,
                   nút "Show potential customers", rê chuột = tooltip, bấm = bảng chi tiết, nút báo cáo cho sếp và CSV).
                   Chế độ NOCO_OFFLINE=1 dùng load_demo_buildings(); không có mạng thì vẽ khối nhà không nền.
__init__.py  (T1 tạo khung, T11 hoàn thiện, COULD)  Feature "noco_scout" cho shell chung: schema SiteNote(Reviewable) cho văn bản ghi chú/hóa đơn giả.
      Trường cấp cao (eval chỉ chấm cấp cao): address, building_use, floors, year_built, heating_system, existing_insulation_r, monthly_bill_usd, evidence.

Quy tắc dữ liệu: không lưu, không hiển thị owner1/mail3/mail4 hay bất kỳ trường chủ sở hữu nào; bản đồ và báo cáo ghi "© OpenStreetMap contributors";
văn bản đưa cho LLM chỉ là dữ liệu giả hoặc công khai; giao diện và báo cáo bằng tiếng Anh; số "lợi nhuận/doanh thu của NOCO" luôn gắn nhãn ILLUSTRATIVE
cho đến khi NOCO cung cấp biên lợi nhuận và chi phí thật.
```

**Golden (kiểm thử T2, dung sai 0,1%, lấy từ ví dụ Buffalo của NOCO; hằng số HDD 6.075 và CDD 650 là suy ra, chưa được NOCO xác nhận):**
chu vi 500 ft, 1 tầng, cao 12 ft, tường lộ 100%, cửa 35%, R-11 lên R-49, sưởi điện trở COP 1,0, làm mát COP 3,0, LF 0,75, điện $0,16, ưu đãi $4,00/sq ft ⇒
tường cách nhiệt **3.900**; tải sưởi **30.066.178 Btu**; tải làm mát **2.412.718 Btu**; kWh sưởi **8.811,9**; kWh làm mát **235,7**; tổng **9.047,6 kWh**;
tiền/năm **$1.447,6**; ưu đãi **$15.600**; giá trị 10 năm **$14.476**. Không có chi phí ⇒ `simple_payback_years` phải là `None` (không bịa số).

## Tasks
Cột dùng cho `make lanes`: **Owner** bắt đầu bằng một vai trò trong bảng Team. **Depends on**: `T1` = phụ thuộc cứng; `T1~` = phụ thuộc mềm (bắt đầu ngay được, chỉ hoàn tất sau khi T1 merge).
**Status**: `todo` | `doing` | `review` | `merged` | `blocked`. Nhãn **[MUST]**, **[SHOULD]**, **[COULD]** theo `docs/spec.md`.

| ID | Task | Owner | Files it may touch | Depends on | Status |
|----|------|-------|--------------------|------------|--------|
| T1 | [MUST] Khung hợp đồng: `contract.py`, `fixtures.py` (ví dụ NOCO + 5 tòa nhà giả có đa giác), `__init__.py` đăng ký feature `noco_scout`. Mở PR trong ~15 phút | claude | `src/features/noco_scout/contract.py`, `src/features/noco_scout/fixtures.py`, `src/features/noco_scout/__init__.py` | - | todo |
| T2 | [MUST] Máy tính: `estimate_insulation`, `inputs_from_facts`; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ) | codex | `src/features/noco_scout/calc.py`, `tests/test_noco_calc.py` | T1~ | todo |
| T3 | [MUST] Bộ nối dữ liệu GIS: `geocode`, `fetch_footprint`, `fetch_property`, `build_facts`, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi | claude | `src/features/noco_scout/geo.py`, `tests/test_noco_geo.py`, `tests/fixtures/noco/`, `.gitignore` (chỉ thêm đúng một dòng `data/public/cache/`, đã duyệt) | T1~ | todo |
| T4 | [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên `fixtures.py` trước, nối T2/T3/T5/T7 khi chúng merge | codex | `src/features/noco_scout/mapdata.py`, `app/pages/`, `tests/test_noco_mapdata.py` | T1~ | todo |
| T5 | [SHOULD] Khách tiềm năng: `build_opportunity` (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và `rank_prospects` | codex | `src/features/noco_scout/prospect.py`, `tests/test_noco_prospect.py` | T2 | todo |
| T6 | [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào `docs/DATA.md` | researcher | `docs/DATA.md`, `docs/T6_NOCO_questions.txt` | - | todo |
| T7 | [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào `data/public/demo_buildings.json`, script chạy lại được | claude | `scripts/prefetch_noco_data.py`, `data/public/` | T3 | todo |
| T8 | [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng | human-C | `docs/PITCH.md`, `docs/pitch/`, `README.md` | - | todo |
| T10 | [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: `render_customer_report`, `render_manager_report`, `prospects_to_csv` (HTML in được, không thêm thư viện) | claude | `src/features/noco_scout/report.py`, `tests/test_noco_report.py` | T2 | todo |
| T11 | [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành `SiteNote`, 3 ca eval với `fake_response` | codex | `src/features/noco_scout/__init__.py`, `evals/cases/noco_scout.jsonl`, `data/synthetic/site_notes/`, `tests/test_noco_extract.py` | T2 | todo |
| T9 | [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, `make test && make lint` | human-B | `app/` (chỉ khi có lỗi, hỏi trước) | T4, T5, T7, T10 | todo |
| R1 | Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa | claude | | T2 | todo |

Thứ tự: T1 (≤15 phút) → T2, T3, T4, T6, T8 song song → T5, T7, T10, R1, T11 → T9. Gate: **12:00** hợp đồng merge; **13:15 MUST xong**
(máy tính + địa chỉ → thông tin + bản đồ Buffalo có tooltip nguồn + báo cáo cho khách + offline); **13:40 SHOULD**; **13:50 COULD**; **14:00 đóng băng**
(hạn nộp 15:30). Chưa xong MUST lúc 13:15 thì bỏ SHOULD và COULD (xem `docs/spec.md`).

## Requests (an agent needs a change in a file it does not own)
- 2026-10-03 T3 (claude, Anh-08) -> `.gitignore`: thêm một dòng `data/public/cache/` (bộ nhớ đệm HTTP là thô, lớn, gắn với máy). **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**, ngoại lệ chỉ cho PR của T3, không sửa gì khác trong `.gitignore`. `data/public/demo_buildings.json` (T7) vẫn được commit; demo offline tra file đó trước, rồi mới tới bộ nhớ đệm.

## Merge log (human appends after each merge)
- (none yet)
