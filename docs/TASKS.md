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
| T1 | [MUST] Khung hợp đồng: `contract.py`, `fixtures.py` (ví dụ NOCO + 5 tòa nhà giả có đa giác), `__init__.py` đăng ký feature `noco_scout`. Mở PR trong ~15 phút | claude | `src/features/noco_scout/contract.py`, `src/features/noco_scout/fixtures.py`, `src/features/noco_scout/__init__.py` | - | merged |
| T2 | [MUST] Máy tính: `estimate_insulation`, `inputs_from_facts`; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ) | codex | `src/features/noco_scout/calc.py`, `tests/test_noco_calc.py` | T1~ | merged |
| T3 | [MUST] Bộ nối dữ liệu GIS: `geocode`, `fetch_footprint`, `fetch_property`, `build_facts`, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi | claude | `src/features/noco_scout/geo.py`, `tests/test_noco_geo.py`, `tests/fixtures/noco/`, `.gitignore` (chỉ thêm đúng một dòng `data/public/cache/`, đã duyệt) | T1~ | merged |
| T4 | [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên `fixtures.py` trước, nối T2/T3/T5/T7 khi chúng merge | codex | `src/features/noco_scout/mapdata.py`, `app/pages/`, `tests/test_noco_mapdata.py` | T1~ | merged |
| T5 | [SHOULD] Khách tiềm năng: `build_opportunity` (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và `rank_prospects` | codex | `src/features/noco_scout/prospect.py`, `tests/test_noco_prospect.py` | T2 | merged |
| T6 | [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào `docs/DATA.md` | researcher | `docs/DATA.md`, `docs/T6_NOCO_questions.txt` | - | merged |
| T7 | [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào `data/public/demo_buildings.json`, script chạy lại được | claude | `scripts/prefetch_noco_data.py`, `data/public/`, `tests/test_noco_demo_data.py` (ngoại lệ đã duyệt) | T3 | merged |
| T8 | [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng; cập nhật theo `docs/DATA.md` (biên 30 đến 40% là lời nói, ưu tiên cộng đồng thiệt thòi, "đẹp, nhanh, dễ dùng"); slide 4 chỉ khi A6 được đồng ý | human-C | `docs/PITCH.md`, `docs/pitch/`, `README.md` | - | todo |
| T10 | [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: `render_customer_report`, `render_manager_report`, `prospects_to_csv` (HTML in được, không thêm thư viện). Nhúng logo NOCO `docs/pitch/assets/noco_logo.png` (NOCO yêu cầu, C4) dạng base64; báo cáo sếp: cột "greens" = các ô đầu ra màu xanh của bảng tính NOCO (`SC!D5:F11`: tiết kiệm điện sưởi, làm mát, tổng điện, MMBtu, tiền/năm, ưu đãi, giá trị 10 năm) + địa chỉ, khu, loại, tầng, độ chắc chắn của phép nối; doanh thu/lợi nhuận NOCO chỉ là cột thêm ILLUSTRATIVE; báo cáo cho KHÁCH tuyệt đối không có doanh thu/lợi nhuận/biên của NOCO; không viết cứng "$4/sq ft" hay "R-11 lên R-49", lấy từ `inputs`/`result` vì T12 sẽ đổi cách tính; dùng số trong `docs/DATA.md` | claude | `src/features/noco_scout/report.py`, `tests/test_noco_report.py` | T2 | merged |
| T11 | [COULD, chỉ sau T12] AI trích xuất ghi chú hiện trường/hóa đơn giả thành `SiteNote`, 3 ca eval với `fake_response` | codex | `src/features/noco_scout/__init__.py`, `evals/cases/noco_scout.jsonl`, `data/synthetic/site_notes/`, `tests/test_noco_extract.py` | T12 | merged |
| T12 | [SHOULD] Chỉnh máy tính theo công thức THẬT của NOCO (xem `docs/DATA.md`: mục "Group A", "Formula and example reconciliation", "National Grid Commercial Weatherization rules" và phần Addendum với các bảng tham chiếu): (1) quy tắc ưu đãi theo nhiên liệu sưởi, ΔR và DAC, có trần $150.000 điện / $250.000 gas (ưu tiên cao nhất); (2) HDD 6.750 nhân hệ số sưởi 0,9 và làm mát = LF × 0,75 thay vì LF²; (3) hồ sơ vận hành theo loại toà (LF, chiều cao tầng, % cửa) khi bảng Buffalo không có chiều cao; (4) chu vi dự phòng theo tỷ lệ cạnh. Hệ thống sưởi mặc định phải rõ ràng và gắn nhãn giả định. Test Golden hiện có VẪN phải qua; thêm 3 ca mới (gas, DAC, trần) | codex | `src/features/noco_scout/calc.py`, `src/features/noco_scout/contract.py` (chỉ lớp `Assumptions` và `CalcInputs`, chỉ thêm trường tùy chọn; ngoại lệ đã duyệt), `tests/test_noco_calc.py` | T2 | merged |
| T14 | [MUST] Sửa tìm địa chỉ offline (lỗi thật, tìm thấy ở QA): trang "Address to Quote" dùng `find_building` chỉ khớp chính xác hoặc chứa chuỗi con, nên "110 Franklin St" bị từ chối và "33 Franklin St" trả NHẦM toà "333 FRANKLIN ST" (không có cảnh báo). Cách sửa: bỏ khớp chuỗi con; `find_building` gọi `geo.build_facts(address, offline=True)` (chuẩn hoá của T3 đã đúng) và bắt `ValueError`; số nhà phải khớp CHÍNH XÁC; thêm xử lý chuỗi không dấu phẩy ("110 franklin st buffalo ny") và "Street/Avenue". Test: "33 Franklin St" KHÔNG được ra "333"; "110 Franklin St", "110 Franklin Street", "110 FRANKLIN, BUFFALO" đều ra đúng toà | claude | `app/pages/noco_shared/__init__.py` (chỉ hàm `find_building`), `src/features/noco_scout/geo.py` (chỉ phần chuẩn hoá và tra cứu offline), `tests/test_noco_geo.py`, `tests/test_noco_mapdata.py` (ngoại lệ đã duyệt) | T10 | merged |
| T9 | [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, `make test && make lint` | human-B | `app/` (chỉ khi có lỗi, hỏi trước) | T4, T5, T7, T10, T14, T12~ | doing |
| R1 | Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa | claude | | T2 | merged |
| T15 | [SHOULD] Làm đẹp giao diện, CHỈ giao diện (không đổi logic, tên nút, hợp đồng, không thêm dependency): (1) giao diện tối, một màu nhấn, đồng bộ nền bản đồ pydeck tối (`.streamlit/config.toml`); (2) CSS nhỏ qua `st.markdown(unsafe_allow_html=True)`: giảm lề trang, bỏ khoảng trắng thừa, bo góc thẻ, cỡ chữ; (3) bản đồ chiếm toàn chiều ngang, cao khoảng 600-700 px, panel chi tiết cạnh bản đồ; (4) tooltip và bảng "What we found" cùng nền tối. Giữ dòng © OpenStreetMap contributors. Test AppTest hiện có VẪN phải qua. Hạn 14:15 để còn QA; quá hạn mà chưa xong thì bỏ, không để vỡ demo | claude | .streamlit/config.toml, app/pages/1_Address_to_Quote.py, app/pages/2_Prospect_Map.py, app/pages/noco_shared/__init__.py (chỉ phần style/bố cục) | T14 | merged |
| T16 | [MUST] Sửa bảng giả định và câu "Data limits" trong báo cáo sếp (phát hiện R1 số 2): lấy bảng giả định từ `result.assumptions` (KHÔNG sửa contract.py), HDD 6.750 [noco_sheet] x hệ số 0,9, bỏ câu nói HDD/CDD chưa được NOCO xác nhận (bảng tính đã xác nhận). Thêm test | claude | src/features/noco_scout/report.py, tests/test_noco_report.py (ngoại lệ đã duyệt) | T10, T12 | merged |
| T17 | [SHOULD] Sửa gán hồ sơ vận hành (phát hiện R1 số 3): "AUTO BODY AND TIRE SHOP" vào nhóm Warehouse / Light Industrial, không phải retail (chứa chữ "SHOP"). Thêm test. Chỉ sửa chỗ gán hồ sơ | claude | src/features/noco_scout/calc.py (chỉ phần gán operating_profile), tests/test_noco_calc.py (ngoại lệ đã duyệt) | T12 | merged |
| T18 | [MUST, sửa lỗi demo + dữ liệu minh hoạ] Hai PR. PR1 (hạn 14:40): (1) tooltip Prospect Map bay ra khỏi màn hình: rút còn tối đa 6 dòng ngắn, rộng tối đa khoảng 300 px, tự kiểm tra trong trình duyệt ở mép trên/giữa/dưới; (2) bỏ câu lỗi thời "inferred HDD/CDD remain unconfirmed". PR2 (hạn 14:55, quá hạn thì KHÔNG merge): giá trị DEMO thay cho chỗ trống "needs cost/margin": DEMO_COST_PER_SQFT=8.0 (đội HELIX chọn, không phải giá NOCO), DEMO_MARGIN_PCT=0.35 (giữa khoảng 30-40% NOCO nói miệng), định nghĩa MỘT chỗ ở tầng app, toggle bật sẵn, tắt được; KHÔNG đổi giá trị mặc định trong contract.py. Mọi giá trị DEMO (chi phí lắp đặt, chi phí dự án/doanh thu, hoàn vốn, biên, lợi nhuận) tô ĐỎ (#EF4444) có chú thích ở giao diện web và trong 2 báo cáo HTML; báo cáo khách vẫn KHÔNG có doanh thu/lợi nhuận/biên NOCO | codex | src/features/noco_scout/mapdata.py, src/features/noco_scout/report.py, app/pages/1_Address_to_Quote.py, app/pages/2_Prospect_Map.py, app/pages/noco_shared/__init__.py, tests/test_noco_mapdata.py, tests/test_noco_report.py (ngoại lệ đã duyệt) | T15 | todo |

Thứ tự: T1 (≤15 phút) → T2, T3, T4, T6, T8 song song → T5, T7, T10, R1, T11 → T9. Gate: **12:00** hợp đồng merge; **13:15 MUST xong**
(máy tính + địa chỉ → thông tin + bản đồ Buffalo có tooltip nguồn + báo cáo cho khách + offline); **13:40 SHOULD**; **13:50 COULD**; **14:30 đóng băng**
(hạn nộp 15:30). Chưa xong MUST lúc 13:15 thì bỏ SHOULD và COULD (xem `docs/spec.md`).

## Requests (an agent needs a change in a file it does not own)
- 2026-10-03 T3 (claude, Anh-08) -> `.gitignore`: thêm một dòng `data/public/cache/` (bộ nhớ đệm HTTP là thô, lớn, gắn với máy). **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**, ngoại lệ chỉ cho PR của T3, không sửa gì khác trong `.gitignore`. `data/public/demo_buildings.json` (T7) vẫn được commit; demo offline tra file đó trước, rồi mới tới bộ nhớ đệm.
- 2026-10-03 T7 (claude, Anh-08) -> (a) truy vấn bảng Buffalo chỉ thêm 3 cột của chính toà nhà: `address`, `zip_code_5_digit`, `neighborhood` (KHÔNG BAO GIỜ cột `owner*`, `mail*`, `mail_zipcode*`; script phải `assert` tên cột không chứa "owner" hay "mail"). (b) thêm `tests/test_noco_demo_data.py`: chỉ đọc `data/public/demo_buildings.json`, không gọi mạng; kiểm tra >= 40 toà, có đa giác/tầng/địa chỉ/nguồn, không có chuỗi owner/mail, toạ độ trong khung Buffalo, `estimate_insulation` chạy được trên tất cả. **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**.
- 2026-10-03 T7 chỉ dẫn đã duyệt: ghi file sau mỗi ô và mở PR ngay khi đạt >= 40 toà (MUST), mở rộng 150-300 ở PR sau; chọn có hạn mức theo khu phố (>= 3 khu); Census chỉ geocode ~30 toà nổi bật; toà `ROW TYPE (W/COMMON WALL)` ghi chú trong sources và hạ ưu tiên (tường chung không lộ ra ngoài).

- 2026-10-03 T12 (codex, phamvotriduc241106) -> `src/features/noco_scout/contract.py`: chỉ được thêm trường TÙY CHỌN vào `Assumptions` và `CalcInputs` (ví dụ hệ số thực hiện sưởi 0,9 và làm mát 0,75, cờ DAC, hồ sơ vận hành); KHÔNG đổi tên hay kiểu trường đang có, KHÔNG đổi `BuildingFacts`, `CalcResult`, `Opportunity`, `Prospect`. Lý do: bảng tính thật của NOCO (`docs/DATA.md`). **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)** (đề xuất, xác nhận khi giao việc).
- 2026-10-03 T14 (claude, Anh-08) -> `app/pages/noco_shared/__init__.py` (file của T4) và `geo.py` (file của T3): chỉ sửa tìm địa chỉ offline, theo mô tả của dòng T14. Lý do: QA phát hiện "33 Franklin St" trả nhầm "333 FRANKLIN ST" và "110 Franklin St" bị từ chối. **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**; phamvotriduc241106 đang làm T12 nên không bị ảnh hưởng.
- 2026-10-03 T15 (claude, Anh-08) -> `app/pages/*.py`, `app/pages/noco_shared/__init__.py` (file của T4) và `.streamlit/config.toml`: chỉ sửa giao diện (CSS, bố cục, theme), không đổi logic hay tên nút. **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**.
- 2026-10-03 T16, T17 (claude, Anh-08) -> `report.py` (file của T10), `calc.py` (file của T2/T12) và test tương ứng: chỉ sửa theo mô tả dòng T16/T17 (phát hiện R1). Phát hiện R1 số 1, 4, 5 để sau (slide "tương lai"). **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**.
- 2026-10-03 T18 (codex, phamvotriduc241106) -> `mapdata.py` (file của T4), `report.py` (file của T10), các trang app và test tương ứng: chỉ theo dòng T18 (tooltip, câu chú thích, giá trị DEMO tô đỏ). KHÔNG sửa contract.py, calc.py, prospect.py. Làm sau đóng băng 14:30 theo quyết định của human-A; PR2 quá 14:55 thì không merge. **ĐÃ DUYỆT bởi human-A (Nguyen-Le-Tuan)**.

## Merge log (human appends after each merge)
- (none yet)
