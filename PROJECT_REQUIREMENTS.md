# Đặc Tả Yêu Cầu Phần Mềm (Software Requirements Specification - SRS)
# Dự Án: RotaNA — Hệ Thống Giám Sát & Hỗ Trợ Ra Quyết Định Nông Nghiệp Vựa Lúa Yên Thành (Nghệ An)

---

## 1. Giới thiệu (Introduction)

### 1.1 Mục đích (Purpose)
Tài liệu này đặc tả toàn bộ các yêu cầu nghiệp vụ, kiến trúc kỹ thuật và tiêu chuẩn giao diện người dùng cho hệ thống **RotaNA** (Rotational Agriculture Decision Support System for Nghe An) — chuyên sâu tại **Vựa lúa Huyện Yên Thành (Nghệ An)**. Hệ thống khai thác dữ liệu viễn thám vệ tinh NASA và khí tượng để hỗ trợ bà con nông dân, hợp tác xã và cán bộ khuyến nông ra quyết định mùa vụ thông minh, né tránh rủi ro thiên tai (nắng nóng gió Lào và ngập lụt tháng 9).

### 1.2 Phạm vi Sản phẩm (Product Scope)
* **Khu vực địa lý trọng điểm**: Huyện Yên Thành, tỉnh Nghệ An (Diện tích lúa ~26.500 ha, sản lượng >155.000 tấn/năm).
* **Đối tượng cây trồng**: Cây lúa nước là trung tâm (Vụ Chiêm Xuân & Vụ Hè Thu) kết hợp các mô hình luân canh cải tạo đất (Lạc, Ngô đông, Rau màu).
* **Nguồn dữ liệu vệ tinh & khí tượng NASA**:
  - NASA MODIS/Sentinel: Chỉ số sinh thái thực vật NDVI & EVI.
  - NASA SMAP: Độ ẩm đất tầng mặt và tầng rễ (Root Zone Soil Moisture).
  - NASA GPM: Lượng mưa vệ tinh tích lũy và lượng mưa ngày.
  - NASA POWER: Nhiệt độ không khí ($T_{\max}, T_{\min}$), độ ẩm tương đối, bức xạ mặt trời.
  - Dữ liệu thủy văn: Hệ thống đại thủy nông Ba Ra Đô Lương và Kênh Vách Bắc.

---

## 2. Tiêu Chuẩn Giao Diện & Thiết Kế Đồ Họa (UI/UX Principles)

### 2.1 Nguyên tắc "Mô hình hóa Số liệu & Thẻ Đồ họa" (No Walls of Text)
* **TUYỆT ĐỐI KHÔNG** sử dụng các đoạn văn bản giải thích dài dòng gây quá tải nhận thức cho người dùng.
* **Mọi dữ liệu phải được số hóa & trực quan hóa**:
  - Dùng **Infographic Badges** thay cho các câu chữ mô tả.
  - Dùng **Card-based Selection** (Thẻ tương tác có viền nổi, màu sắc, icon) thay cho Radio Button / Selectbox cổ điển.
  - Dùng **Visual Ribbon Timeline** tích hợp cảnh báo thiên tai (Vùng đỏ Gió Lào, Vùng xanh Lũ lụt) để người dùng nắm bắt chu kỳ vụ mùa trong 5 giây.
  - Dùng **Thanh đo rủi ro (Gauge Bars)** và **Pill Tags** để lựa chọn cơ cấu giống lúa và cây luân canh.
* **Chuẩn màu sắc (White Studio Theme)**:
  - Nền trang: `#F8FAFC`
  - Thẻ nội dung: `#FFFFFF` với viền `#E2E8F0` và đổ bóng nhẹ `rgba(0,0,0,0.03)`
  - Chữ chính: `#0F172A`, Chữ phụ: `#64748B`
  - Điểm nhấn Nông nghiệp: `#16A34A` (Xanh lá - An toàn), `#0284C7` (Xanh dương - Nước/SMAP), `#F59E0B` (Vàng cam - Cân nhắc), `#DC2626` (Đỏ - Cảnh báo thiên tai/Gió Lào).

---

## 3. Yêu Cầu Chức Năng (Functional Requirements)

### 3.1 Phân hệ Tổng quan Mùa vụ Lúa (Executive Command Center)
* `[US-DASH-01]`: Master Ribbon Timeline 12 tháng sinh trưởng của cây lúa Yên Thành, bấm chọn tháng trực quan.
* `[US-DASH-02]`: 5 Thẻ Hero KPI phản ánh thực trạng: Nhiệt độ $T_{\max}$, Lượng mưa GPM, Số ngày Gió Lào $\ge 35^\circ\text{C}$, Độ ẩm đất SMAP, Sinh khối NDVI.
* `[US-DASH-03]`: Bản đồ tác chiến số hóa phân chia 4 cụm xã Yên Thành (Bắc Đô Thành, Lòng chảo TT Yên Thành, Nam Bảo Thành, Tây Mỹ Thành) với cơ chế Pan/Zoom GIS và 1-click Preset Zoom.
* `[US-DASH-04]`: Tích hợp ảnh vệ tinh NASA độ phân giải cao (Folium) phủ dữ liệu viễn thám thực tế theo từng lớp chọn.
* `[US-DASH-05]`: Radar đo rủi ro nông học và **3 Mệnh Lệnh Nông Vụ Khẩn Cấp** trong tháng cho bà con nông dân.
* `[US-DASH-06]`: Khối Analytics Lab 3 biểu đồ chuỗi thời gian 10 năm được đóng gói thu gọn (Expander), đảm bảo trang vừa khít 1 màn hình máy tính.

### 3.2 Phân hệ Kế hoạch Mùa vụ & Luân canh (AgTech Crop Planner)
* `[US-PLAN-01]`: 3 Thẻ Mô hình Mùa vụ đồ họa tương tác (2 Vụ lúa thuần, 3 Đợt luân canh Lúa-Màu, Tự chọn chân ruộng).
* `[US-PLAN-02]`: Thanh tiến trình Timeline Gantt 12 tháng hiển thị các đợt canh tác kết hợp dải cảnh báo thiên tai NASA (Vùng nguy hiểm Gió Lào T5-T7 và Vùng bão lũ T9).
* `[US-PLAN-03]`: Thẻ đồ họa tác nghiệp từng đợt canh tác với thanh đo an toàn khí hậu, chọn nhanh giống cây trồng (ST25, J02, TBR225, Lạc, Ngô) và tỷ lệ % diện tích.
* `[US-PLAN-04]`: Thuật toán tự động gợi ý cơ cấu cây trồng tối ưu theo dữ liệu khí hậu lịch sử 11 năm.
* `[US-PLAN-05]`: Bảng điểm đánh giá an toàn cả năm và biểu đồ lịch mùa vụ Gantt Chart đa màu sắc.

### 3.3 Phân hệ Viễn thám Vệ tinh & Kho Dữ liệu NASA
* `[US-SAT-01]`: Phòng giám sát viễn thám vệ tinh toàn màn hình (Full-Width GIS), phủ các lớp dữ liệu NASA: NDVI, SMAP, GPM, Nhiệt & Gió Lào.
* `[US-SAT-02]`: 4 Trạm quan trắc số hóa AgTech Pinpoints với popup hiển thị số liệu đo đạc thời gian thực và mệnh lệnh điều tiết nước.
* `[US-SAT-03]`: Kho dữ liệu chuỗi thời gian và công cụ tải bảng số liệu CSV đã xử lý.

### 3.4 Phân hệ Hồ sơ Vựa lúa & Lịch sử Khí tượng
* `[US-HIST-01]`: So sánh chuỗi thời gian đối chiếu các năm (2024, 2025, 2026) và trung bình chuẩn 11 năm.
* `[US-PROFILE-01]`: Hồ sơ số hóa chi tiết 26.500 ha lúa Yên Thành, mạng lưới thủy nông Ba Ra Đô Lương, Kênh chính và Kênh Vách Bắc.

---

## 4. Yêu Cầu Kỹ Thuật & Hiệu Năng
* Thời gian tải và render trang trung bình $< 1.5$ giây.
* 100% code tuân thủ quy chuẩn: Mã nguồn Tiếng Anh, Chú thích Tiếng Việt ngắn gọn, Chu trình kiểm thử 4 bước đạt PASS 100%.
