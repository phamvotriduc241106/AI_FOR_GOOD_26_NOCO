# Giới thiệu sản phẩm: NOCO Scout (đội HELIX)

**Một câu:** gõ một địa chỉ ở Buffalo, sau vài giây có báo giá cách nhiệt tường cho toà nhà đó, tính bằng
chính công thức của NOCO, và mọi con số đều ghi rõ nguồn.

---

## 1. Vấn đề

Hiện nay, để báo giá nâng cấp năng lượng cho một toà nhà thương mại, nhân viên NOCO phải:

1. đến tận nơi khảo sát;
2. về văn phòng tra cứu thêm thông tin;
3. rồi mới lập báo giá.

Theo lời ban tổ chức, việc này **tốn nhiều thời gian**. Theo NOCO, mỗi báo giá cần 1 đến 2 chuyên gia về điện và hệ thống sưởi.
Một nhân viên không thể đến hết các toà nhà trong thành phố, nên **phần lớn toà nhà chưa bao giờ được báo giá**.

## 2. Giải pháp

NOCO Scout thay bước khảo sát ban đầu bằng **dữ liệu công khai**:

```
Địa chỉ ─► US Census Geocoder ─► OpenStreetMap (đường viền, số tầng) ─► Bảng định giá City of Buffalo (loại toà)
        ─► Máy tính cách nhiệt (tái tạo bảng tính của NOCO) ─► Báo giá + bản đồ 3D + báo cáo
```

Ba người dùng, ba lợi ích:

| Người dùng | Nhận được gì |
|---|---|
| **Nhân viên kinh doanh NOCO** | Báo giá trong vài giây từ một địa chỉ, chưa cần đến tận nơi |
| **Quản lý kinh doanh** | Bản đồ 3D Buffalo xếp hạng **khách hàng tiềm năng**, báo cáo nội bộ và file CSV |
| **Chủ toà nhà** | Báo cáo 1 trang dễ hiểu: tiết kiệm mỗi năm, ưu đãi, bước tiếp theo |

## 3. Điều gì làm sản phẩm khác biệt

1. **Dữ liệu GIS thay cho khảo sát.** Chu vi, diện tích đế, số tầng lấy từ bản đồ công khai thay vì đo tại chỗ.
2. **Mọi con số có nguồn.** Mỗi dữ kiện đi kèm nguồn và độ chắc chắn. Số nào là giả định thì ghi "assumed", số minh hoạ thì ghi "ILLUSTRATIVE".
3. **Đúng công thức của NOCO.** Đội đã đọc từng ô của bảng tính NOCO v5 và viết lại:
   - Ví dụ Buffalo của NOCO cho ra 9,047.6 kWh, $1,447.6 mỗi năm và ưu đãi $15,600, **khớp đúng bảng tính**.
   - Quy tắc ưu đãi National Grid: theo nhiên liệu, theo mức tăng R, thưởng cho cộng đồng thiệt thòi (DAC), trần $150,000 (điện) và $250,000 (gas).
4. **Từ một toà lên cả thành phố.** Cùng một máy tính chạy cho 300 toà ở 11 khu phố Buffalo, rồi xếp hạng khách hàng tiềm năng.
5. **Chạy offline.** Dữ liệu demo đã lưu sẵn, app vẫn chạy khi mất mạng.

## 4. Những gì đang có (đã kiểm thử)

- Trang **Address to Quote**: địa chỉ → dữ kiện có nguồn → ước tính tiết kiệm, ưu đãi, hoàn vốn → báo cáo cho khách.
- Trang **Prospect Map**: nút **Show potential customers**, bản đồ 3D, bộ lọc, panel chi tiết, báo cáo cho sếp và CSV.
- 300 toà nhà thật ở Buffalo, không lưu tên chủ hay địa chỉ gửi thư.
- AI chỉ đọc ghi chú hiện trường (văn bản mẫu) để trích dữ kiện; **AI không bao giờ quyết định con số**, mọi phép tính là code cố định có kiểm thử.

## 5. Giới hạn (nói thật với giám khảo)

| Giới hạn | Cách app xử lý |
|---|---|
| Chưa có chi phí lắp đặt từ NOCO | Không bịa số: hiện "Needs installed cost". Có thể nhập số minh hoạ |
| Biên lợi nhuận NOCO (30-40%) chỉ là lời nói, chưa rõ cơ sở | Doanh thu và lợi nhuận luôn ghi ILLUSTRATIVE |
| Không biết hệ thống sưởi thật của toà | Giả định sưởi điện trở và ghi rõ; nhân viên xác nhận với khách |
| Không biết nhà cung cấp năng lượng hiện tại | "Not in public data: ask the customer" |
| Toà phức tạp nhiều mảnh (ví dụ Toà thị chính) | Chưa dựng được, là việc tiếp theo |

## 6. Hướng phát triển

- Thêm biện pháp khác: cửa sổ, HVAC, chiếu sáng, điện mặt trời trên mái (NOCO trả lời: "all of them").
- Thêm ưu đãi: NYSERDA, National Fuel.
- Lớp bản đồ cộng đồng thiệt thòi (DAC) của NYSERDA, vì NOCO ưu tiên nhóm này.
- Dựng toà phức tạp từ các mảnh OSM, tải hoá đơn tiện ích, kết nối CRM của NOCO, mở rộng ra các thành phố NOCO phục vụ.

## 7. Đội HELIX

| Thành viên | Vai trò |
|---|---|
| Nguyen-Le-Tuan | Điều phối, kiểm tra và merge, QA, chạy demo |
| Anh-08 | Phát triển (Claude Code): dữ liệu GIS, báo cáo, giao diện |
| phamvotriduc241106 | Phát triển (Codex): máy tính NOCO, bản đồ, xếp hạng, AI trích xuất |
| NguyenQBao | Nghiên cứu, làm việc với NOCO, slide |
