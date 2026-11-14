# Tiêu Chuẩn Thiết Kế Giao Diện & Design System (Frontend Spec)
# Dự án: RotaNA — Vựa lúa Yên Thành

---

## 1. Triết Lý Thiết Kế: "Mô Hình Hóa Đồ Họa — Không Tường Chữ" (No Walls of Text)

Nông dân, cán bộ chỉ huy và người dùng chỉ có **15–30 giây** để nắm bắt tình hình. Vì vậy:
1. **Thay văn bản mô tả bằng Thẻ Trực Quan (Card-based UI)**:
   - Các lựa chọn mùa vụ, cơ cấu cây trồng, đợt canh tác phải được thể hiện bằng các Card bấm chọn có viền màu, đổ bóng nhẹ, icon lớn và số liệu ngắn gọn.
   - Không dùng radio button hoặc select box khô khan cho các lựa chọn quan trọng.
2. **Dải Thời Gian Đồ Họa (Visual Timeline & Gantt)**:
   - Thể hiện chu kỳ 12 tháng liền mạch.
   - Luôn tích hợp các dải màu cảnh báo thiên tai (Vùng đỏ Gió Lào $\ge 35^\circ\text{C}$ T5–T7, Vùng xanh tím Lũ bão T9).
3. **Thanh Đo Rủi Ro & Chỉ Số Sinh Thái (Gauge & Progress Bars)**:
   - Thay các dòng chữ nhận xét bằng thanh đo màu sắc (Xanh: An toàn $\le 35\%$, Vàng: Cân nhắc $35-55\%$, Đỏ: Cảnh báo $> 55\%$).
4. **Pill Tags cho Giống Cây Trồng**:
   - Dùng các thẻ nhãn gọn gàng: `[🌾 ST25]`, `[🌾 J02]`, `[🥜 Lạc L14]`, `[🌽 Ngô NK4300]`.

---

## 2. Bảng Màu Chuẩn (Color Palette - White Studio Theme)

| Tên màu | Mã Hex | Mục đích sử dụng |
| :--- | :--- | :--- |
| **Trắng tinh khôi** | `#FFFFFF` | Nền thẻ Card, Dashboard container, Popup |
| **Nền xám dịu** | `#F8FAFC` | Nền toàn trang, giúp các thẻ nổi bật rõ nét |
| **Viền cấu trúc** | `#E2E8F0` | Đường phân cách, border thẻ (1px solid) |
| **Chữ tiêu đề** | `#0F172A` | Font Be Vietnam Pro, độ đậm 750–800 |
| **Chữ phụ chú** | `#64748B` | Nhãn phụ, caption ngắn |
| **Xanh nông nghiệp** | `#16A34A` | Trạng thái An toàn, Nên trồng, Sinh khối NDVI khỏe |
| **Xanh dương thủy lợi** | `#0284C7` | Nguồn nước Ba Ra, Độ ẩm đất SMAP, Mưa GPM |
| **Vàng cam cảnh giác** | `#F59E0B` | Trạng thái Cân nhắc, chân ruộng vàn cao cần giữ ẩm |
| **Đỏ cảnh báo thiên tai**| `#DC2626` | Cảnh báo Gió Lào táp phấn $\ge 35^\circ\text{C}$, lũ lụt |

---

## 3. Quy Chuẩn Kích Thước & Responsive
* **Chiều cao Dashboard Tác chiến**: Vừa khít màn hình 1080p và laptop (không bắt buộc cuộn chuột dài).
* **Khối phân tích chuyên sâu 10 năm**: Luôn được xếp trong Expander hoặc tab chuyên sâu để trang không bị quá tải dữ liệu.
