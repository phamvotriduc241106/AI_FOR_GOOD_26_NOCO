# Hướng dẫn sử dụng NOCO Scout (cho cả đội, đọc trong 5 phút)

Số liệu trong tài liệu này được tính bằng code trên `main` lúc 14:20 ngày 2026-10-03 (300 toà, giả định mặc định).
Lệch vài đô la là bình thường. Demo trên **MacBook có mạng** (có nền bản đồ). Laptop Linux không dùng.

---

## 1. Mở app trên MacBook

```bash
cd AI_FOR_GOOD                     # thư mục repo trên Mac
git checkout main && git pull --rebase origin main
source .venv/bin/activate
make run                           # có mạng: có nền bản đồ đường phố tối
# Mất mạng: Ctrl+C rồi chạy  NOCO_OFFLINE=1 make run  (vẫn có khối 3D, chỉ mất nền)
```

Trình duyệt mở `http://localhost:8501`.

> **QUAN TRỌNG: trang đầu tiên ("hackkit") KHÔNG phải sản phẩm.** Đó là khung chung của bộ công cụ.
> Bỏ qua nó. Ở **thanh bên trái**, bấm **Address to Quote** hoặc **Prospect Map**.
> Hoặc mở thẳng địa chỉ:
> - `http://localhost:8501/Address_to_Quote`
> - `http://localhost:8501/Prospect_Map`
>
> Trước khi lên sân khấu: mở sẵn 2 tab trình duyệt, mỗi tab một trang, và đóng tab "hackkit".

---

## 2. Trang "Address to Quote": từ một địa chỉ ra báo giá

Dùng khi: nhân viên NOCO có **một** toà nhà cụ thể và muốn báo giá ngay.

| Bước | Làm gì | Thấy gì |
|---|---|---|
| 1 | Ô **Buffalo building address**: xoá chữ cũ, gõ `33 Franklin St` | |
| 2 | Bấm **Find building** (nút màu xanh) | Bản đồ bay tới toà nhà, khối 3D 11 tầng hiện lên |
| 3 | Đọc bảng **Facts and confidence** bên phải | Mỗi dòng (loại toà, diện tích đế, chu vi, số tầng, chiều cao tầng) có cột **Source** (nguồn) và **Confidence** (độ chắc chắn) |
| 4 | Bấm **Estimate insulation upgrade** | 3 ô số: **Annual savings** khoảng **$10,223/năm**, **Incentive** khoảng **$110,167**, **Payback**: "Needs installed cost" |
| 5 | (Tuỳ chọn) bật **Enter an ILLUSTRATIVE installed cost**, giữ $8 | Payback khoảng **10.8 năm** (con số MINH HOẠ, NOCO chưa cho chi phí thật) |
| 6 | Bấm **Generate customer report** | Tải file `noco-customer-report.html`: báo cáo 1 trang cho chủ toà, có logo NOCO |

Các ô vàng bên dưới kết quả là **giả định**, không phải lỗi:
- "Heating system is assumed electric resistance": hệ thống sưởi giả định là điện trở, cần khách xác nhận.
- "DAC status is unknown": chưa biết toà có thuộc cộng đồng thiệt thòi không, nên chưa cộng thưởng.

Địa chỉ đã kiểm tra là chạy được: `33 Franklin St`, `110 Franklin St`, `1 Seneca St`, `532 Main St`, `107 Delaware Ave`.
**Không dùng** `65 Niagara Square` (Toà thị chính): không có trong bộ dữ liệu, OSM tách toà này thành nhiều mảnh nên app ra sai hình dạng và không có số tầng.

---

## 3. Trang "Prospect Map": tìm khách hàng tiềm năng cho sếp

Dùng khi: quản lý muốn biết **nên gọi cho toà nào trước** trong cả Buffalo.

| Bước | Làm gì | Thấy gì |
|---|---|---|
| 1 | Mở trang | Bản đồ 3D Buffalo với các toà trong bộ dữ liệu |
| 2 | Bấm **Show potential customers** | Toà đổi màu **xanh → cam** (cam = tiết kiệm cao). Bảng **Ranked prospects** hiện bên dưới |
| 3 | Xem top 3 | **#1 1 Seneca St** (Seneca One, toà cao nhất Buffalo, 40 tầng) khoảng **$235,406/năm**, ưu đãi **$150,000** (chạm trần của National Grid). #2 532 Main St. #3 107 Delaware Ave |
| 4 | **Bấm** (click) vào một toà trên bản đồ, hoặc chọn trong **Select a building** | Panel **Building details** bên phải đổi theo toà đó: dữ kiện + nguồn, tiết kiệm, ưu đãi, nhà cung cấp hiện tại ("Not in public data: ask the customer") |
| 5 | Bộ lọc phía trên: **Building use**, **Minimum annual savings**, **Top buildings** | Lọc theo loại toà, mức tiết kiệm tối thiểu, số toà hiển thị (mặc định 25) |
| 6 | (Tuỳ chọn) mở **ILLUSTRATIVE NOCO cost and margin inputs**, bật cost $8 và margin 0.20 | Hiện doanh thu và lợi nhuận NOCO, luôn có nhãn ILLUSTRATIVE |
| 7 | **Download manager report (HTML)** và **Download prospect CSV** | Báo cáo cho sếp (xếp hạng, các cột "xanh" của bảng tính NOCO, bảng giả định có nguồn) và file CSV |

> **Lỗi đang sửa (T18): rê chuột (hover) ở trang này làm khung thông tin bay ra khỏi màn hình.**
> Cho tới khi sửa xong: **đừng rê chuột để giới thiệu**. Hãy **bấm** vào toà, rồi chỉ vào panel **Building details** bên phải.

---

## 4. Các con số đến từ đâu (để trả lời giám khảo)

| Thông tin | Nguồn |
|---|---|
| Địa chỉ → toạ độ | US Census Geocoder |
| Đường viền toà, diện tích đế, chu vi, số tầng | OpenStreetMap (© OpenStreetMap contributors) |
| Loại toà, chiều cao tầng | Bảng định giá tài sản của City of Buffalo (open data) |
| Công thức tiết kiệm, ưu đãi, trần ưu đãi | Bảng tính NOCO Commercial Insulation Savings Calculator v5 (NOCO cung cấp) |
| Chi phí lắp đặt, biên lợi nhuận | **Chưa có từ NOCO** → chỉ là số minh hoạ (ILLUSTRATIVE) |
| Nhà cung cấp năng lượng hiện tại của khách | **Không có trong dữ liệu công khai** → "ask the customer" |

Quyền riêng tư: app **không bao giờ** lưu hay hiện tên chủ sở hữu hay địa chỉ gửi thư từ bảng thuế.

---

## 5. Nếu có sự cố khi đang demo

| Sự cố | Làm ngay |
|---|---|
| Mất mạng, bản đồ không có nền | Không sao: khối 3D vẫn chạy. Nói "we also run fully offline" và đi tiếp |
| Trang báo lỗi đỏ | Bấm F5. Vẫn lỗi → chuyển sang video dự phòng `docs/pitch/demo_backup.mp4` |
| Địa chỉ báo "not found" | Gõ lại đúng `33 Franklin St` |
| Khung hover bay ra ngoài | Bấm vào toà thay vì rê chuột |
| App treo | Ctrl+C trong terminal, chạy lại `make run` (khoảng 10 giây) |
