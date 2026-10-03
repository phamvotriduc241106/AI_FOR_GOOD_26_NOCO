# DATA.md: nguồn dữ liệu, hằng số thật của NOCO và câu trả lời (T6)

> Người làm: NguyenQBao (partner-qa, researcher). Phần này do Nguyen-Le-Tuan và trợ lý điền thay Bảo từ hai file Bảo gửi:
> `docs/NOCO_Commercial_Insulation_Savings_Calculator_v5.xlsx` (bảng tính **thật** của NOCO, đã đọc từng ô và công thức) và
> `docs/GROUP B.docx` (ghi chép khi hỏi; chỉ có nhóm B và C). Hai file gốc chưa commit (là tài liệu của đối tác).
> Nhãn độ tin cậy: **sheet** = đọc trực tiếp từ bảng tính NOCO; **said** = người của NOCO nói (Bảo ghi lại, chưa rõ chức vụ); **open** = chưa có câu trả lời.

## 1. Năm dòng: điều khác với giả định của chúng ta

1. **HDD của Buffalo là 6.750, không phải 6.075.** Bảng tính còn nhân "Heating realization factor" **0,9** (6.750 × 0,9 = 6.075), nên kết quả ví dụ không đổi.
   CDD = 650 đúng như suy luận.
2. **Hệ số làm mát KHÔNG phải LF².** Công thức thật là `LF × Cooling realization factor (0,75)`, hằng số riêng. Hai cách trùng nhau chỉ vì hồ sơ "Office" có LF = 0,75.
   Với hồ sơ khác, mô hình hiện tại lệch tải làm mát 13% đến 33% (khoảng ±$17/năm mỗi toà, không đáng kể về tiền nhưng sai về công thức).
3. **Ưu đãi không phải $4,00/sq ft cố định.** Nó phụ thuộc nhiên liệu sưởi, ΔR, cờ DAC, và có **trần $150.000 (điện) / $250.000 (gas)**. Ví dụ ra $4,00 vì điện + ΔR = 38 (≥ 21) + không DAC.
   Với toà dùng **gas**, đúng là **$1,90/sq ft** (ΔR 31 đến 40): mô hình hiện tại cao hơn 111%. **Đây là chỗ lệch lớn nhất.**
4. **Chu vi "500 ft" tính bằng công thức**: `2 × (√(A × AR) + √(A / AR)) × hệ số hình dạng`, AR = 4 cho "Very Long / Narrow" (2 × (200 + 50) = 500). Bảng tính có ô ghi đè diện tích cách nhiệt, nên chu vi lấy từ GIS của ta là thay thế hợp lệ.
5. **Câu trả lời nhóm B/C:** biên lợi nhuận 30 đến 40% (said); ưu tiên cộng đồng thiệt thòi (said); ưu đãi khác cần có: National Fuel, NYSERDA (said); NOCO muốn dùng logo của họ trong báo cáo (said).
   **Chưa có (open):** chi phí lắp đặt (A4), cho phép dùng số của NOCO trong slide (A6), câu trả lời của ban tổ chức (O1 đến O4), khác biệt "greens column" (B2) cần Bảo làm rõ.

## 2. Hằng số trong bảng tính NOCO (sheet `Assumptions`)

| Hằng số | Giá trị | Ghi chú |
|---|---|---|
| Btu mỗi kWh | 3.412 | |
| Btu mỗi therm | 100.000 | gas |
| Btu mỗi gallon propane / dầu | 91.500 / 138.500 | |
| Btu mỗi MMBtu | 1.000.000 | |
| **Heating realization factor** | **0,9** | nhân vào tải sưởi |
| **Cooling realization factor** | **0,75** | nhân vào tải làm mát (đây là hệ số "thứ hai", không phải LF) |
| Opaque Wall Factor | 0,8 | có trong bảng nhưng **không được dùng** trong công thức đã đọc |
| HDD / CDD, Buffalo | 6.750 / 650 | Rochester 6.500/700, Syracuse 6.650/700, Binghamton 6.800/600, Watertown 7.200/500, Albany 6.500/850, Plattsburgh 7.600/450 |

**Hồ sơ vận hành** (LF, chiều cao tầng, % cửa): 24/7 hoặc nhà ở 1,0 / 10 ft / 25%; **Office/School/Daytime 0,75 / 12 ft / 35%**; Retail/Restaurant 0,85 / 14 ft / 30%;
Warehouse/Light Industrial 0,65 / 20 ft / 8%; Gián đoạn/Theo mùa 0,5 / 12 ft / 20%; Custom 1,0 / 12 ft / 20%.
**Hình dạng** (tỷ lệ cạnh, hệ số chu vi): Square 1 / 1; Typical Rectangle 1,5 / 1; Long Rectangle 2,5 / 1; **Very Long/Narrow 4 / 1**; L-Shaped 1,5 / 1,15; U/C 1,5 / 1,3; Courtyard 1,5 / 1,45; Irregular 1,5 / 1,5.
**Hệ thống sưởi** (COP/hiệu suất mặc định): Gas furnace chuẩn 0,8; cao cấp 0,95; Gas boiler chuẩn 0,82; ngưng tụ 0,94; Propane 0,85; Dầu 0,82; **Điện trở 1,0**; Bơm nhiệt khí 3,0; Bơm nhiệt đất 4,0; Hơi/nước nóng khu vực 0,9.
**Làm mát** (COP): Rooftop 3,0; Split/DX 3,2; Chiller khí 3,5; Chiller nước 5,5; Bơm nhiệt 3,5. **R-value**: R-11 = 11 ... R-49 = 49, R-60 = 60 (và các mức thấp hơn).

## 3. Công thức chính xác (đọc từ ô của bảng tính)

```text
chu_vi (ft)        = 2 × (√(diện_tích_sàn × AR) + √(diện_tích_sàn / AR)) × hệ_số_hình_dạng      # I19, I21
tường_gộp          = chu_vi × chiều_cao_tầng × số_tầng × %tường_lộ                                # I24
tường_cách_nhiệt   = diện_tích_ghi_đè  nếu > 0,  ngược lại  tường_gộp × (1 − %cửa)               # I13 (ghi đè = ô B29)
ΔU                 = max(0, 1/R_hiện_tại − 1/R_đề_xuất)                                           # E19
tải_sưởi (Btu)     = ΔU × tường_cách_nhiệt × HDD × 24 × LF × 0,9                                   # I2
tải_làm_mát (Btu)  = ΔU × tường_cách_nhiệt × CDD × 24 × LF × 0,75                                  # I3
kWh_sưởi (điện)    = tải_sưởi / (3.412 × COP_sưởi)         therms (gas) = (tải_sưởi / hiệu_suất) / 100.000   # I5, I6
kWh_làm_mát        = tải_làm_mát / (3.412 × COP_làm_mát)   (bằng 0 nếu "No Cooling")                # I10
tiền/năm           = kWh_sưởi × giá_điện + kWh_làm_mát × giá_điện   (gas: therms × giá_gas)        # I11, I12, E9
giá_trị_10_năm     = 10 × tiền/năm                                                                  # E11
```
Ví dụ Buffalo của NOCO (10.000 sq ft, R-11 → R-49, điện trở): **khớp từng con số** với bảng tính (tải sưởi 30.066.178 Btu, tải làm mát 2.412.718 Btu, 9.047,6 kWh, $1.447,6/năm, ưu đãi $15.600).

## 4. Quy tắc ưu đãi "National Grid - Commercial Weatherization" (ô E10, I14, I16, I17)

| Nhiên liệu sưởi | ΔR < 4 | ΔR 4 đến 10 | ΔR 11 đến 20 | ΔR 21 đến 30 | ΔR 31 đến 40 | ΔR > 40 | Trần |
|---|---|---|---|---|---|---|---|
| **Điện**, $/sq ft, không DAC (DAC) | 0 | 2 (3) | 3 (4) | **4 (5)** | **4 (5)** | **4 (5)** | $150.000 |
| **Gas**, $/sq ft, không DAC (DAC) | 0 | 0,15 (1,15) | 1,5 (2,5) | 1,75 (2,75) | **1,9 (2,9)** | 2 (3) | $250.000 |

Gas còn bị loại (bằng 0) nếu ΔR < 4 hoặc ΔR > 60. Chương trình khác trong bảng: NYSEG/RG&E C&I $0,80/sq ft; NYSEG/RG&E Small Business $1,25/sq ft; National Grid Multifamily $150 mỗi MMBtu tiết kiệm hằng năm.
Số tiền = đơn giá × `tường_cách_nhiệt`, rồi áp trần.

## 5. Câu trả lời của người NOCO

| # | Câu hỏi (rút gọn) | Câu trả lời | Nguồn | Ảnh hưởng đến sản phẩm |
|---|---|---|---|---|
| A1 | HDD/CDD Buffalo | HDD **6.750**, CDD **650**; thêm hệ số 0,9 cho sưởi | sheet | `Assumptions.hdd`: đặt 6.750 và thêm hệ số 0,9 (T12) |
| A2 | Hệ số làm mát | `LF × 0,75`, **không phải LF²** | sheet | `calc.py` dòng làm mát (T12) |
| A3 | Chu vi | Công thức theo tỷ lệ cạnh (mục 3); có ô ghi đè diện tích cách nhiệt | sheet | giữ chu vi GIS; dùng công thức làm dự phòng (T12) |
| A4 | Chi phí lắp đặt/sq ft | **chưa có** (bảng tính không có chi phí dự án) | open | giữ "needs cost", nhãn ILLUSTRATIVE |
| A5 | Ưu đãi | Bảng ở mục 4 (điện $4 khi ΔR ≥ 21, không DAC; trần $150k điện, $250k gas) | sheet | quy tắc ưu đãi (T12) |
| A6 | Được dùng số của NOCO trong slide/demo? | **chưa hỏi/chưa có**; NOCO đã đưa bảng tính cho đội làm đề | open | slide 4 chỉ dùng khi được đồng ý rõ |
| B1 | Bước nào tốn thời gian nhất? | "1 đến 2 chuyên gia về điện và hệ thống sưởi + dữ liệu toà nhà để trả lời tốt nhất" (số chuyến không bán được: chưa có) | said | câu chuyện pitch: báo giá cần chuyên gia + dữ liệu toà nhà |
| B2 | Báo cáo sếp cần cột nào? | "**greens column**" (chưa rõ nghĩa; có thể là cột tiền/lợi nhuận) | said, chưa rõ | Bảo cần làm rõ trước khi chốt báo cáo sếp (T10) |
| B3 | Biên lợi nhuận | **30 đến 40%** (quy mô dự án trung bình: chưa có) | said | `margin_pct` 0,30 đến 0,40; lợi nhuận vẫn ILLUSTRATIVE vì thiếu chi phí |
| B4 | "Provider" là gì? | "Dựa trên toà nhà, rồi tìm **nhà cung cấp phù hợp nhất cho các dịch vụ tiện ích**" | said | `Opportunity`: hiển thị "nhà cung cấp gợi ý", không phải nhà cung cấp hiện tại |
| B5 | Ưu tiên toà/khu nào? | **Cộng đồng thiệt thòi**; mục tiêu: mọi toà thương mại | said | lớp DAC (mục 7), bộ lọc ưu tiên |
| B6 | Gói tài liệu ở cuối phòng | "nằm trong bảng tính" (chính là file `.xlsx`) | said | xong |
| C1 | Biện pháp tiếp theo | "tất cả" (cửa sổ, HVAC, đèn, mặt trời, pin) | said | slide tương lai |
| C2 | Ưu đãi khác ở Buffalo | **National Fuel, NYSERDA** | said | tương lai; slide |
| C3 | Điều gây "wow" | "siêu dễ dùng + nhanh + **đẹp** cho nội bộ và cho khách" | said | tiêu chí demo và báo cáo |
| C4 | Logo/phong cách báo cáo | **logo NOCO** ("Official Natural Gas and Electric Supplier"), đã lưu ở `docs/pitch/assets/noco_logo.png` | said | báo cáo cho khách (T10) |
| O1 đến O4 | Câu hỏi cho ban tổ chức | **chưa có** | open | Bảo hỏi tiếp (giờ nộp, 4 phút có hỏi đáp không, Wi-Fi) |

## 6. Điểm mở và rủi ro còn lại
- **Chi phí lắp đặt** và quy mô dự án trung bình: chưa có, nên doanh thu và lợi nhuận NOCO luôn ghi ILLUSTRATIVE (biên 30 đến 40% đã có nhưng chưa nhân được với chi phí thật).
- **Nhiên liệu sưởi mặc định:** mô hình hiện đặt điện trở (COP 1,0), cho tiết kiệm cao gần gấp 3 so với gas. Phần lớn toà thương mại ở Buffalo dùng gas, nên cần chọn hệ thống sưởi rõ ràng trong giao diện và nhãn giả định (T12).
- **Hồ sơ vận hành theo loại toà** (kho: 20 ft và 8% cửa, khác văn phòng 12 ft và 35%): hiện dùng một mặc định cho tất cả.
- Toà "ROW TYPE (W/COMMON WALL)" và "APARTMENT" có trong bộ dữ liệu (10 và 33 toà): tường chung không lộ ra ngoài; nhà ở có hồ sơ 24/7.

## 7. Nguồn dữ liệu công khai và giấy phép
| Nguồn | Dùng để | Giấy phép / ghi chú |
|---|---|---|
| US Census Geocoder | địa chỉ → toạ độ | công khai, không cần khóa |
| OpenStreetMap (Overpass) | đa giác, tầng, loại | ODbL: **"© OpenStreetMap contributors"** bắt buộc; cần User-Agent |
| Bảng đánh giá Buffalo (Socrata `4t8s-9yih`) | loại tài sản, chiều cao tầng, địa chỉ, khu phố | chỉ các cột `address`, `zip_code_5_digit`, `neighborhood`, `prop_class_description`, `story_height`; **không bao giờ** `owner*`, `mail*` |
| **NYSERDA Final Disadvantaged Communities (DAC)** | cờ cộng đồng thiệt thòi theo vùng điều tra (**đã kiểm chứng**) | `https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYSERDA_Final_Disadvantaged_Communities/FeatureServer/0`; trường `GEOID`, `DAC_Desig`; thử 3 điểm ở Buffalo đều trả về "Designated as DAC" |
| Bảng tính NOCO v5 | hằng số, công thức, ưu đãi | tài liệu của đối tác đưa cho đội; **chưa có xác nhận cho phép đưa số vào slide (A6)** |

**Ý tưởng chưa làm (đã kiểm chứng khả thi về dữ liệu):** gắn cờ DAC cho từng toà (truy vấn theo điểm, có bộ nhớ đệm), huy hiệu và bộ lọc "ưu tiên cộng đồng thiệt thòi" trên bản đồ, và ưu đãi cao hơn theo bảng tính (điện $5 thay vì $4; gas $2,9 thay vì $1,9).
Khớp với B5 (NOCO ưu tiên cộng đồng thiệt thòi) và chủ đề AI for Good. Chỉ làm nếu còn giờ sau T10 và T12, nếu không ghi vào slide "tương lai".

## 8. Kịch bản chi phí (ILLUSTRATIVE)
Chưa có số thật từ NOCO. Giao diện cho nhập chi phí lắp đặt/sq ft bằng thanh trượt gắn nhãn ILLUSTRATIVE; mặc định không có số, hoàn vốn hiện "needs cost".
Biên lợi nhuận NOCO: 0,30 đến 0,40 (said); lợi nhuận = doanh thu dự án × biên, và chỉ có khi có chi phí.
