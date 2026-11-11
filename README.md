# 🌾 RotaNA - Hệ thống Hỗ trợ Ra quyết định Luân canh Nông nghiệp (Nghệ An)

**RotaNA** là một Hệ thống Hỗ trợ Ra quyết định (Decision Support System - DSS) được phát triển trong khuôn khổ cuộc thi **NASA Space Apps Challenge 2026**. 

Dự án tích hợp dữ liệu viễn thám từ vệ tinh NASA để phân tích rủi ro khí hậu (Nắng nóng, Xói mòn, Úng ngập) và đưa ra các kịch bản luân canh cây trồng tối ưu cho 3 vùng sinh thái tại tỉnh Nghệ An: Yên Thành (Đồng bằng), Nghi Lộc (Ven biển) và Con Cuông (Đồi núi).

---

## 🚀 1. Tính năng chính của Dashboard
- **Bản đồ khu vực:** Hiển thị ranh giới 3 huyện trực quan.
- **Đèn giao thông rủi ro:** Cảnh báo tức thời theo tháng về tình trạng Nắng nóng, Lượng mưa và Độ ẩm đất.
- **Lịch rủi ro 12 tháng:** Nhận diện trực quan các "cửa sổ rủi ro" (Gió Lào mùa hè, Mưa lũ mùa thu) để nông dân tránh gieo hạt.
- **Bộ lọc kịch bản luân canh:** Nông dân tự điều chỉnh thanh trượt (Ưu tiên Nước / Đất / Kinh tế), hệ thống sẽ tự động chấm điểm và gợi ý kịch bản tối ưu nhất.

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
```text
Nasa/
│
├── .streamlit/             # Cấu hình giao diện Streamlit (Theme sáng)
├── data/                   # Thư mục chứa dữ liệu
│   ├── raw/                # Dữ liệu gốc tải từ vệ tinh NASA (CSV, GeoJSON)
│   └── processed/          # Dữ liệu đã qua xử lý (bảng gộp, tính điểm rủi ro)
│
├── src/                    # (Tùy chọn) Chứa các module phụ trợ
├── app.py                  # File chính khởi chạy giao diện Web Dashboard
├── gio_lao.py              # Script phân tích đặc điểm gió Lào (nếu có)
├── gop_du_lieu.py          # Script gộp và tính toán dữ liệu từ data/raw
├── rui_ro.py               # Script phân tích logic rủi ro nông học
├── lay_power.py            # Script lấy dữ liệu NASA POWER
├── requirements.txt        # Danh sách các thư viện cần thiết
└── README.md               # Tài liệu hướng dẫn này
