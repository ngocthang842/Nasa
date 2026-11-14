# 🌾 RotaNA - Hệ thống Hỗ trợ Ra quyết định Luân canh Nông nghiệp (Nghệ An)

**RotaNA** là một Hệ thống Hỗ trợ Ra quyết định (Decision Support System - DSS) được phát triển trong khuôn khổ cuộc thi **NASA Space Apps Challenge 2026**. 

Dự án tích hợp dữ liệu viễn thám từ vệ tinh NASA để phân tích rủi ro khí hậu (Nắng nóng, Xói mòn, Úng ngập) và đưa ra các kịch bản luân canh cây trồng tối ưu cho 3 vùng sinh thái tại tỉnh Nghệ An: Yên Thành (Đồng bằng), Nghi Lộc (Ven biển) và Con Cuông (Đồi núi).

---

## 🚀 1. Tính năng chính của Dashboard
- **Kế hoạch Luân canh theo Đợt Canh tác:** Chia chu kỳ cả năm thành các đợt gieo trồng (Vụ Xuân, Vụ Hè Thu, Vụ Thu Đông/Đông hoặc tùy chỉnh). Nông hộ có thể linh hoạt bố trí số lượng cây trồng khác nhau cho từng đợt (chuyên canh 1 cây, đa canh 2-3 cây, hoặc để ải đất).
- **Hỗ trợ Ra quyết định dựa trên Dữ liệu Lịch sử Đa năm:** Hệ thống phân tích chuỗi dữ liệu vệ tinh (MODIS, SMAP, GPM) và khí tượng NASA POWER của các năm trước (2024, 2025...) kết hợp chuẩn 11 năm để chấm điểm an toàn, nhận diện cửa sổ rủi ro lịch sử và xếp hạng các cây trồng phù hợp nhất cho từng đợt.
- **Biểu đồ Timeline Luân canh Cả năm:** Trực quan hóa kế hoạch phân bổ cây trồng qua 12 tháng, chấm điểm an toàn khí hậu, tiết kiệm nước tưới, phục hồi độ phì đất và hiệu quả kinh tế.
- **Bản đồ khu vực & Vệ tinh tương tác:** Hiển thị ranh giới 3 huyện, bản đồ toàn quốc (gồm Hoàng Sa, Trường Sa) và bản đồ vệ tinh Folium phóng sát cánh đồng.
- **Đèn giao thông rủi ro & Thẻ KPI:** Cảnh báo tức thời theo tháng về Nắng nóng, Lượng mưa, Độ ẩm đất và NDVI kèm đường xu hướng sparkline.

---

## 📊 2. Quy trình Xử lý Dữ liệu (Data Pipeline)

Dữ liệu được xử lý qua 3 giai đoạn: **Thu thập (GEE) → Xử lý (Python) → Trực quan hóa (Streamlit)**.

### 2.1. Dữ liệu lấy từ đâu? (Thư mục `data/raw`)
Dữ liệu gốc được trích xuất từ Google Earth Engine (GEE) và NASA POWER, chia làm 3 nhóm chính:
1. **Nhóm Cây trồng (MODIS):** `ndvi`, `evi`, `lai` (Đã lọc mây) - Đánh giá sức khỏe thảm thực vật.
2. **Nhóm Thời tiết & Nước:** `mua` (GPM), `lst` (Nhiệt độ), `smap` (Độ ẩm đất), `et`, `pet` (Bốc thoát hơi nước).
3. **Nhóm Địa hình & Đất:** `dem_slope` (Độ dốc), `landcover` (Lớp phủ), `dat` (Tính chất đất).
4. **Dữ liệu lịch sử (NASA POWER):** 3 file `power_...csv` chứa dữ liệu khí tượng **11 năm (2015-2025)**.

> 💡 **Tại sao lại lấy dữ liệu 11 năm?**
> Dữ liệu 11 năm đóng vai trò là "mức trung bình lịch sử" (Baseline). Nhờ có nó, hệ thống mới so sánh được năm 2025 đang nắng nóng bất thường hay bình thường để đưa ra cảnh báo chính xác.

### 2.2. Máy tính đã xử lý những gì? (Các file Python)
- `lay_power.py`: Kết nối API NASA POWER để tải dữ liệu khí tượng 11 năm.
- `gop_du_lieu.py`: Gộp dữ liệu từ ngày thành tháng. Tính toán các chỉ số: **ESI** (Căng thẳng nước), **Cân bằng nước** (Mưa - Bốc hơi), và đếm số ngày nắng nóng >35°C.
- `rui_ro.py`: Áp dụng logic nghiệp vụ (Độ dốc + Lượng mưa) để gắn nhãn rủi ro "Xói mòn" hoặc "Úng ngập".
- *Kết quả đầu ra:* File `data/processed/bang_huyen_thang.csv` và `rui_ro_huyen_thang.csv` chứa dữ liệu sạch đã được tính toán.

---

## 📁 3. Cấu trúc Thư mục Dự án
`	ext
Nasa/
│
├── .streamlit/             # Cấu hình giao diện Streamlit (Theme sáng)
├── data/                   # Thư mục chứa dữ liệu
│   ├── raw/                # Dữ liệu gốc tải từ vệ tinh NASA (CSV, GeoJSON)
│   └── processed/          # Dữ liệu đã qua xử lý (bảng gộp, rủi ro, gió Lào)
│
├── views/                  # Các phân hệ giao diện Dashboard
│   ├── tong_quan.py        # Phân hệ Tổng quan (KPI, bản đồ, rủi ro tháng)
│   ├── cay_vung.py         # Phân hệ Cây theo vùng & Thổ nhưỡng
│   ├── luan_canh.py        # Phân hệ Kế hoạch Luân canh theo Đợt
│   ├── so_sanh.py          # Phân hệ So sánh chuỗi thời gian các năm
│   ├── du_lieu.py          # Phân hệ Bảng số liệu chi tiết
│   ├── ban_do.py           # Bản đồ Plotly đa lớp & ranh giới
│   ├── ve_tinh.py          # Bản đồ vệ tinh Folium phóng sát cánh đồng
│   └── chung.py            # CSS, thẻ KPI sparkline, thẻ đánh giá
│
├── app.py                  # File chính khởi chạy giao diện Web Dashboard
├── engine.py               # Lõi xử lý nghiệp vụ, lịch mùa vụ & thuật toán chấm điểm
├── gio_lao.py              # Script phân tích đặc điểm gió Lào lịch sử
├── gop_du_lieu.py          # Script gộp và tính toán dữ liệu từ data/raw
├── rui_ro.py               # Script phân tích logic rủi ro nông học
├── lay_power.py            # Script lấy dữ liệu NASA POWER
├── requirements.txt        # Danh sách các thư viện cần thiết
└── README.md               # Tài liệu hướng dẫn này
`
