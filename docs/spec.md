# Spec: NOCO "Address-to-Quote" (BẢN NHÁP CHỜ DUYỆT)

> **Ghi chú (15:05):** đây là bản nháp kế hoạch buổi sáng, giữ lại làm lịch sử. Một số chỗ đã lỗi thời (ví dụ LF², HDD 6.075, "cần chi phí"). Công thức hiện hành: `src/features/noco_scout/calc.py` và `docs/DATA.md`; mô tả sản phẩm: `README.md`.

> **Trạng thái:** DRAFT để cả đội review trước khi khóa. Challenge **NOCO** đã chốt.
> **Quy ước nhãn:** *[đã kiểm chứng]* = tôi đã gọi API hoặc tính thật trong buổi sáng nay. *[suy luận]* = hợp lý nhưng
> NOCO chưa xác nhận. *[giả thuyết]* = ý kiến chưa có bằng chứng, cần hỏi người của NOCO.
> **Phạm vi địa lý: CHỈ thành phố Buffalo** (không mở rộng ra bang hay cả nước; thay vào đó làm bản đồ Buffalo thật ấn tượng).
> **Ngôn ngữ sản phẩm:** giao diện, báo cáo cho khách và slide viết bằng **tiếng Anh** (giám khảo và NOCO là người Mỹ).

## Problem and user

**Vấn đề.** Ban tổ chức nói (bản ghi `[03:49]`–`[04:13]`) rằng nhân viên NOCO hiện phải "đi thu thập thông tin ở hiện trường,
về văn phòng nghiên cứu, rồi mới nói với khách hàng họ có thể tiết kiệm bao nhiêu... tất cả đều tốn thời gian". NOCO muốn
"một máy tính tiết kiệm năng lượng" dùng AI. Bảng tính NOCO phát cho đội cần hơn 10 đầu vào (chu vi tòa nhà, số tầng, chiều cao
tầng, diện tích, R hiện tại, HDD/CDD...). Đó chính là phần phải đi đo ngoài hiện trường.

**Người dùng chính:** một nhân viên kinh doanh/năng lượng của NOCO đang chuẩn bị báo giá cho một tòa nhà thương mại.
**Người dùng thứ hai:** quản lý kinh doanh ("sếp") của NOCO, cần danh sách khách tiềm năng và cơ hội doanh thu.
**Người đọc báo cáo:** chủ hoặc người quản lý tòa nhà (báo cáo "dành cho khách hàng" là yêu cầu của đề) và quản lý của NOCO (báo cáo nội bộ).

**Vì sao NOCO cần xây việc này** *[giả thuyết, cần kiểm chứng với người của NOCO tại hội trường]*:
1. Tốc độ: rút thời gian từ "đi hiện trường rồi nghiên cứu" xuống còn vài giây từ một địa chỉ.
2. Quy mô: nhân viên không thể đến từng tòa nhà; công cụ cho phép **chủ động tìm khách** trên cả khu vực.
3. Độ tin cậy: mỗi con số có nguồn và độ chắc chắn; công thức trùng với bảng tính của chính NOCO.
4. Bán chéo: cùng một mô hình mở rộng sang các giải pháp khác của NOCO (điện mặt trời, sạc xe điện, pin lưu trữ...).
   *Câu hỏi kiểm chứng:* "Bước nào trong một lần báo giá tốn nhiều thời gian nhất? Bao nhiêu lượt đi hiện trường không đi đến đâu?"

**Lợi thế của đội ("moat")** *[giả thuyết]*: phần lớn đội khác sẽ làm "máy tính + chatbot". Chúng ta khác ở ba điểm:
1. **Từ địa chỉ ra báo giá:** dữ liệu công khai + GIS tự điền các đầu vào mà bảng tính NOCO đang đòi (chu vi, diện tích đáy, số tầng,
   loại tòa nhà). Đây đúng là phần đang tốn thời gian của họ.
2. **Bản đồ khách tiềm năng của Buffalo, tương tác:** rê chuột tới đâu hiện thông tin tới đó, có trích nguồn; bấm nút "Show potential customers" để xếp hạng cả khu
   phố theo mức tiết kiệm và cơ hội cho NOCO. Đây là cảnh gây ấn tượng thị giác.
3. **Đáng tin:** tái tạo đúng bảng tính của NOCO (khớp **0,000%** trên ví dụ của họ, xem mục Calculator), và mọi số đều ghi nguồn.

## Demo script (what the judges see, step by step)

Pitch dài 4 phút (`[10:21]`), được demo trực tiếp (`[10:41]`). Giám khảo có người không chuyên kỹ thuật.

| Cảnh | Thời lượng | Người xem thấy | Dữ liệu |
|---|---|---|---|
| 0. Câu chuyện | 25 giây | "Hôm nay một báo giá mất nhiều ngày vì phải đi đo. Chúng tôi làm trong 10 giây từ một địa chỉ." | |
| 1. Gõ địa chỉ | 35 giây | Bản đồ Buffalo bay tới địa chỉ, **khối nhà nổi 3D** theo số tầng, bảng "Điều chúng tôi tìm được từ dữ liệu công khai": diện tích đáy, chu vi, số tầng, loại tòa nhà, mỗi dòng có nhãn nguồn và độ chắc chắn | Geocoder, OSM, bảng đánh giá Buffalo |
| 2. Ước tính | 35 giây | Bấm "Estimate insulation upgrade": kWh và USD tiết kiệm mỗi năm, ưu đãi, vốn ròng, hoàn vốn (hoặc "cần chi phí lắp đặt"); huy hiệu "Reproduces NOCO's own calculator" | Công thức NOCO |
| 3. **Show potential customers** | 55 giây | Bấm nút: hàng trăm tòa nhà của Buffalo **bật lên theo màu và độ cao** theo cơ hội; **rê chuột tới đâu hiện thẻ thông tin tới đó** (địa chỉ, loại, tầng, diện tích, tiết kiệm, ưu đãi, hoàn vốn, cơ hội cho NOCO, nguồn); bấm một tòa để mở bảng chi tiết bên cạnh | Bộ dữ liệu Buffalo lưu sẵn |
| 4. Xuất báo cáo | 25 giây | Hai nút: **báo cáo cho sếp** (danh sách khách tiềm năng xếp hạng + cơ hội, in được/CSV) và **báo cáo cho khách** (một trang thuyết phục nâng cấp) | Mã tính |
| 5. AI (nếu kịp) | 25 giây | Dán một ghi chú hiện trường hoặc đoạn hóa đơn giả: AI trích xuất (hệ thống sưởi, hóa đơn) và ước tính cập nhật. Số vẫn do mã tính | LLM + quy tắc |
| 6. Tương lai | 20 giây | Thêm biện pháp (cửa sổ, HVAC, mặt trời), thêm ưu đãi và nguồn dữ liệu, mở rộng khu vực | |

Demo phải **chạy được không cần mạng** (dùng bộ dữ liệu đã lưu) và có phương án dự phòng bằng video.

## Data we use (public or synthetic only) and where it comes from

Mọi nguồn dưới đây đã được tôi gọi thử hôm nay *[đã kiểm chứng]*:

| Nguồn | Cho gì | Giới hạn | Cách dùng |
|---|---|---|---|
| **US Census Geocoder** (`geocoding.geo.census.gov`, miễn phí, không cần khóa) | Địa chỉ → kinh độ, vĩ độ (thử: 65 Niagara Sq → -78.8788, 42.8866) | Chỉ địa chỉ Mỹ | Bước đầu của mọi truy vấn |
| **OpenStreetMap qua Overpass** (`overpass-api.de`) | Đa giác tòa nhà, loại (`office`...), **số tầng** `building:levels` (thử: 3 tòa quanh 110 Franklin: 5.473 / 1.867 / 2.571 sq ft, chu vi 347 / 215 / 206 ft) | Độ phủ không đều; có giới hạn tốc độ. **Bắt buộc ghi nguồn "© OpenStreetMap contributors" (ODbL)** | Diện tích đáy, chu vi, số tầng |
| **City of Buffalo Final Assessment Roll** (Socrata `data.buffalony.gov`, bộ `4t8s-9yih`, 77 cột) | Loại tài sản (`prop_class_description`, ví dụ "OFFICE BUILDING"), `story_height`, kích thước lô | **Với tài sản thương mại, `total_living_area`, `first_story_area`, `of_stories` đều bằng 0**, nên KHÔNG lấy diện tích và số tầng từ đây. Bảng có tên chủ sở hữu và địa chỉ gửi thư | Chỉ lấy loại tài sản và chiều cao tầng. **KHÔNG lưu và KHÔNG hiển thị `owner1`, `mail3`, `mail4`...** |
| *Quy mô thật trong khung Downtown–Allentown–Elmwood* (42,870–42,905 N, −78,900 – −78,850 W) *[đã kiểm chứng]* | **1.992** bản ghi thương mại (mã 4xx, gồm cả bãi đỗ xe và đất trống) trong bảng Buffalo; **197** tòa nhà OSM gắn nhãn thương mại/công cộng (commercial, office, retail, industrial, warehouse, school...) | Nhiều tòa OSM chỉ gắn `building=yes` (không rõ loại): dùng bảng Buffalo để xác định loại và nối theo vị trí (độ chắc chắn thấp hơn, phải hiển thị) | Bộ demo 150 đến 300 tòa |
| NYS Tax Parcels (ArcGIS) | | Truy vấn tại Buffalo trả về **0 thửa** | **Không dùng** |
| Bảng tính mẫu của NOCO (ảnh) | Hằng số HDD, CDD, hệ số vận hành, giá điện, ưu đãi $4,00/sq ft | Ảnh độ phân giải thấp, vài chữ số mờ | Công thức và kiểm thử |
| Dữ liệu giả | Ghi chú hiện trường, đoạn hóa đơn, kịch bản chi phí | Phải ghi nhãn "synthetic/illustrative" | Phần AI trích xuất và hoàn vốn |

**Bộ dữ liệu demo:** một script lấy trước **ít nhất 40 (MUST), mục tiêu 150 đến 300 (SHOULD)** tòa nhà thương mại trong khung trên (địa chỉ, đa giác, số tầng,
loại tài sản) và lưu vào `data/public/` để demo chạy offline. Bản đồ dùng đúng bộ này, không gọi mạng lúc trình diễn. Lưu ý quy định của đội: **không gửi dữ liệu thật của đối tác sang dịch vụ AI** khi chưa được phép;
AI chỉ nhận văn bản giả hoặc văn bản công khai.

## Bản đồ Buffalo (cảnh gây ấn tượng; phạm vi: chỉ Buffalo)

*[đã kiểm chứng]* Streamlit 1.65 + pydeck 0.9 hỗ trợ **tooltip khi rê chuột** và **chọn đối tượng khi bấm** (`on_select`), nên làm được mà không thêm thư viện.

- **Lớp bản đồ:** khối nhà 3D (độ cao theo số tầng, màu theo mức tiết kiệm hoặc điểm khách), nền sáng, viền nổi khi rê chuột, chú giải màu.
- **Thẻ khi rê chuột (tooltip), thứ tự cố định:** địa chỉ · loại tài sản · số tầng · diện tích đáy · tiết kiệm/năm · ưu đãi · hoàn vốn (hoặc "needs cost") ·
  cơ hội cho NOCO (doanh thu dự án, lợi nhuận; *minh họa*) · utility và chương trình ưu đãi · **dòng nguồn**, ví dụ
  `OSM way 259799780 (0.9) · Buffalo assessment roll (0.7) · Census geocoder`.
- **Bấm vào một tòa:** bảng chi tiết bên cạnh, mỗi con số kèm nguồn và độ chắc chắn, nút "Generate customer report".
- **Nút "Show potential customers":** bật lớp xếp hạng cả khu (top N theo điểm), kèm danh sách và bộ lọc theo loại tòa nhà và mức tiết kiệm tối thiểu.
- **Offline:** mọi dữ liệu từ `data/public/demo_buildings.json`. Nền bản đồ cần mạng; nếu mất mạng thì chỉ vẽ các khối nhà không nền. Có video dự phòng.

## Khách tiềm năng, "provider" và lợi nhuận (trung thực về dữ liệu)

| Điều muốn hiển thị | Có trong dữ liệu công khai? | Cách xử lý |
|---|---|---|
| Utility phục vụ khu vực và chương trình ưu đãi | Bảng tính NOCO ghi "National Grid - Commercial Weatherization" cho Buffalo *[suy luận, cần xác nhận]* | Hiển thị, gắn nhãn `noco_sheet` |
| **Nhà cung cấp năng lượng hiện tại của từng tòa nhà** | **Không** | Hiển thị "Not in public data: ask the customer". Không đoán |
| Doanh thu và lợi nhuận NOCO từ khách đó | Không có biên lợi nhuận và chi phí thật | Doanh thu dự án = chi phí giả định/sq ft × diện tích tường; lợi nhuận = doanh thu × biên lợi nhuận. **Cả hai mặc định không có số**; chế độ demo dùng thanh trượt gắn nhãn **ILLUSTRATIVE**. Chưa có số thì hiện "needs NOCO margin" |
| Chi tiêu năng lượng hằng năm của khách | Không trực tiếp | COULD: ước tính theo cường độ năng lượng công khai (EIA CBECS); T6 xác minh nguồn |

## Xuất báo cáo (hai loại)

| Báo cáo | Người đọc | Nội dung | Định dạng |
|---|---|---|---|
| **Cho khách** (một trang) | Chủ tòa nhà | Tòa nhà, đề xuất cách nhiệt (R-11 lên R-49), tiết kiệm/năm, ưu đãi, vốn ròng, hoàn vốn (hoặc "cần báo giá"), bước tiếp theo, giả định và nguồn, "© OpenStreetMap contributors". Thuyết phục nhưng không thổi phồng; mọi số do mã tính | HTML tự chứa, in ra PDF từ trình duyệt |
| **Cho sếp** | Quản lý kinh doanh NOCO | Danh sách khách tiềm năng xếp hạng, tổng tiết kiệm tiềm năng, cơ hội doanh thu và lợi nhuận (minh họa), giả định, nguồn, giới hạn dữ liệu | HTML in được + **CSV** |

Xuất **PDF gốc** cần thêm thư viện (ví dụ `fpdf2`); chưa có. **Quyết định của human-A:** dùng "in ra PDF từ trình duyệt" (không phụ thuộc, đáng tin cậy) hay duyệt thêm một thư viện.

## Calculator: công thức (suy ngược từ ví dụ của NOCO)

Tôi suy ngược từ ví dụ Buffalo trong bảng tính (10.000 sq ft, R-11 lên R-49, sưởi điện trở COP 1,0, làm mát COP 3,0) *[đã kiểm chứng bằng tính toán]*:

```
tường_cách_nhiệt = chu_vi × chiều_cao_tầng × số_tầng × %tường_lộ × (1 − %cửa)      # 500×12×1×1×0,65 = 3.900
ΔU               = 1/R_hiện_tại − 1/R_đề_xuất                                        # 0,0705
tải_sưởi (Btu)   = ΔU × tường_cách_nhiệt × HDD × 24 × LF                             # LF = hệ số vận hành 0,75
tải_làm_mát (Btu)= ΔU × tường_cách_nhiệt × CDD × 24 × LF²                            # LF² là suy luận
kWh_sưởi         = tải_sưởi / 3412 / COP_sưởi        kWh_làm_mát = tải_làm_mát / 3412 / COP_làm_mát
tiền_tiết_kiệm   = (kWh_sưởi + kWh_làm_mát) × giá_điện
ưu_đãi           = đơn_giá_ưu_đãi($/sq ft) × tường_cách_nhiệt                         # National Grid: $4,00 theo bảng tính
giá_trị_10_năm   = 10 × tiền_tiết_kiệm_năm                                            # đơn giản, không chiết khấu
hoàn_vốn         = (chi_phí_dự_án − ưu_đãi) / tiền_tiết_kiệm_năm   nếu có chi phí và tiền tiết kiệm > 0, ngược lại KHÔNG có số
```

**Kết quả đối chiếu với ví dụ của NOCO** (hằng số suy ra: **HDD = 6.075,0** chính xác, **CDD = 650** thay vì "600 hoặc 650" không đọc rõ):

| Đại lượng | Công thức của ta | Bảng tính NOCO |
|---|---|---|
| Tường cách nhiệt | 3.900 sq ft | 3.900 |
| Tải sưởi | 30.066.178 Btu | 30.066.178 (chữ số giữa mờ) |
| Tải làm mát (CDD 650, LF²) | **2.412.718 Btu, lệch 0,000%** | 2.412.718 |
| kWh sưởi / làm mát | 8.811,9 / 235,7 | 8.812 / 235,7 |
| Tổng điện, tiền/năm | 9.047,6 kWh, $1.447,6 | 9.048 kWh, $1.448 |
| Ưu đãi, giá trị 10 năm | $15.600, $14.476 | $15.600, $14.476 |

**Chưa xác nhận (cần NOCO):** các hằng số HDD/CDD và hệ số làm mát LF² là suy luận; công thức chu vi "500 ft" của bảng tính cho tòa nhà "dài hẹp"
(hình vuông 10.000 sq ft chỉ có chu vi 400 ft, nên 500 chưa giải thích được); ô "NG Gas Rate 1.9 / NG Electric Rate 4"; khấu trừ cửa 35% so với ô ghi đè 0%; đơn vị ưu đãi;
và **bảng không có chi phí dự án**, nên hoàn vốn và vốn ròng cần kịch bản chi phí *ghi nhãn minh họa* cho đến khi NOCO cung cấp số thật.

## Phạm vi theo mức ưu tiên (còn khoảng 2 giờ 50 phút trước mốc đóng băng 14:30)

| Mức | Nội dung | Hạn |
|---|---|---|
| **MUST** (không có thì không demo) | Máy tính cách nhiệt đúng với ví dụ NOCO (có test) + địa chỉ → thông tin tòa nhà (Census + OSM) + **bản đồ Buffalo 3D có tooltip nguồn** trên bộ dữ liệu lưu sẵn (≥ 40 tòa) + **báo cáo cho khách** + chạy offline | 13:15 |
| **SHOULD** (tạo "wow") | Nút **Show potential customers** (xếp hạng, danh sách, bộ lọc) + mô hình cơ hội cho NOCO (doanh thu/lợi nhuận minh họa, utility) + **báo cáo cho sếp và CSV** + mở rộng bộ dữ liệu lên 150 đến 300 tòa + nối bảng Buffalo (loại tài sản) | 13:40 |
| **COULD** (làm nếu dư giờ) | AI trích xuất ghi chú/hóa đơn giả (điểm cộng "utility bill analysis") + ước tính chi tiêu năng lượng (CBECS) + khung nhiều biện pháp | 13:50 |
| **Để sau** | Cửa sổ, HVAC, đèn, pin, máy phát; tra ưu đãi tự động ngoài tham chiếu National Grid; mở rộng ngoài Buffalo | Slide "tương lai" |

**Quy tắc cắt:** đến 13:15 mà MUST chưa xong thì bỏ hết SHOULD và COULD. Đóng băng 14:30 (đã chốt, từ hạn nộp 15:30), sau đó chỉ sửa lỗi và tập pitch.

## Ánh xạ rubric (5 mục, mỗi mục 3 điểm)

| Mục | Điều chúng ta cho giám khảo thấy |
|---|---|
| Impact and Feasibility | Giải đúng nút thắt của NOCO (đi hiện trường); dùng dữ liệu công khai có thật; chạy được ngay |
| Innovation and Creativity | Địa chỉ → báo giá bằng GIS; bản đồ Buffalo tương tác tìm khách, rê chuột ra thông tin có nguồn; nhãn nguồn trên từng số |
| Presentation and Communication | Câu chuyện bản đồ, demo trực quan, báo cáo một trang cho khách không chuyên kỹ thuật |
| Potential for Future Development | Lộ trình thêm biện pháp, ưu đãi, nguồn dữ liệu, tích hợp CRM của NOCO |
| Solution Execution ("không có lỗi") | Công thức khớp 0,000% với bảng tính NOCO, test tự động, demo offline |

Điểm cộng của đề: **dữ liệu tài sản công khai** ✔, **GIS** ✔, nhận diện ưu đãi tự động (tham chiếu, chưa đầy đủ), AI đề xuất, phân tích hóa đơn (COULD).

## Sponsor API calls

NOCO **không cung cấp** API hay bộ dữ liệu nào. Chỉ dùng các nguồn công khai ở trên. Quy tắc: không gọi mạng trong test; mọi kết quả
gọi thật đều lưu vào bộ nhớ đệm; có giãn cách khi gọi Overpass; demo dùng dữ liệu đã lưu.

## Out of scope

- Mọi khu vực ngoài thành phố Buffalo (không bang, không cả nước).
- Đoán nhà cung cấp năng lượng hiện tại của từng tòa nhà (không có dữ liệu công khai).
- Mọi biện pháp ngoài cách nhiệt tường (cửa sổ, HVAC, đèn, mặt trời, EV, pin, máy phát), trừ khung mở rộng.
- Tra cứu ưu đãi tự động đầy đủ; chiết khấu và NPV.
- Số tầng và diện tích từ bảng đánh giá Buffalo (không có cho tài sản thương mại).
- Hiển thị hay lưu tên chủ sở hữu, địa chỉ gửi thư.
- Bất kỳ tuyên bố nào "đã xác minh" khi NOCO chưa xác nhận hằng số.

## Open questions for the partner

Hỏi người của NOCO ngay tại hội trường (và lấy gói tài liệu NOCO ở cuối phòng, `[46:54]`):
1. Bước nào của một lần báo giá tốn thời gian nhất? Bao nhiêu lượt đi hiện trường không bán được?
2. Xác nhận hằng số: HDD Buffalo 6.075? CDD 650? Cooling dùng hệ số vận hành bình phương?
3. Chu vi ước tính "500 ft" cho tòa nhà "Very Long / Narrow" tính thế nào? Có dùng hình học thật được không?
4. Chi phí lắp đặt cách nhiệt trên mỗi sq ft (khoảng để làm kịch bản)? Ưu đãi National Grid $4,00/sq ft áp dụng theo diện tích nào, có trần không?
5. Có bộ dữ liệu, bảng giá hoặc danh sách ưu đãi nào được phát không (gói ở cuối phòng)?
6. Chúng tôi có được dùng ảnh bảng tính của NOCO làm ca kiểm thử và đưa vào slide không? Có được gửi sang dịch vụ AI không?
7. Bạn muốn thấy điều gì nhất trong demo: báo giá nhanh hay danh sách khách tiềm năng?
8. Biên lợi nhuận và chi phí lắp đặt thực tế để tính "cơ hội cho NOCO"? Sếp của NOCO muốn thấy cột nào trong báo cáo nội bộ?
9. "Provider" mà đội muốn hiển thị là gì với NOCO: utility, nhà cung cấp nhiên liệu hiện tại, hay chương trình ưu đãi?

## Rủi ro và cách giảm

| Rủi ro | Cách giảm |
|---|---|
| OSM thiếu số tầng hoặc đa giác cho một tòa | Giá trị mặc định có nhãn `assumed`, cho phép ghi đè, cờ cảnh báo; bộ demo chỉ chọn tòa có dữ liệu đủ |
| Overpass chậm hoặc giới hạn tốc độ | Lấy trước và lưu; test dùng phản hồi đã ghi; demo offline |
| Bản đồ cần mạng để tải nền | Có chế độ chỉ vẽ đa giác không nền; có video dự phòng |
| Hằng số suy luận sai | Hiển thị là "reference model", hỏi NOCO, không tuyên bố đã xác minh |
| Không có chi phí dự án | Kịch bản chi phí ghi "illustrative"; không bịa số hoàn vốn khi không có chi phí |
| Ba agent viết code song song gây xung đột | Hợp đồng đóng băng ở T1, file tách biệt (xem `docs/TASKS.md`) |
| Nối OSM với bảng Buffalo sai (nhầm tòa nhà) | Hiển thị độ chắc chắn của phép nối; bộ demo chọn tòa có địa chỉ khớp; tooltip ghi rõ nguồn |
| Nền bản đồ cần mạng | Chế độ chỉ vẽ khối nhà; video dự phòng |
| Làm quá nhiều | Quy tắc cắt lúc 13:15 |
