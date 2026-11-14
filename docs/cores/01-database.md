# Kiến Trúc Dữ Liệu & Chuỗi Thời Gian (Database & Time-Series Spec)
# Dự án: RotaNA — Vựa lúa Yên Thành

---

## 1. Nguồn Dữ Liệu & Cấu Trúc File

Hệ thống RotaNA hoạt động dựa trên chuỗi thời gian khí tượng - viễn thám cấp huyện (Yên Thành, Nghệ An):
* **GeoJSON Ranh giới**: `data/raw/ranh_gioi_huyen.geojson` (Lọc thuộc tính `ADM2_NAME == 'Yen Thanh'`).
* **Chuỗi thời gian tháng**: `data/processed/thang_chi_tiet.csv` (Chuỗi 2024–2026).
* **Chuỗi lịch sử chuẩn**: `data/processed/chuoi_chuan.csv` (11 năm khí hậu NASA POWER).
* **Chuỗi nắng nóng gió Lào**: `data/processed/nam_nong.csv` (Số ngày $\ge 35^\circ\text{C}$).

---

## 2. Các Chỉ Số Nông Học & Viễn Thám Cốt Lõi

| Cột dữ liệu | Ý nghĩa | Đơn vị | Nguồn viễn thám |
| :--- | :--- | :--- | :--- |
| `tmax` | Nhiệt độ cao nhất trong tháng | $^\circ\text{C}$ | NASA POWER |
| `mua_mm` | Lượng mưa tích lũy tháng | mm | NASA GPM |
| `nong35` | Số ngày nắng nóng gió Lào $\ge 35^\circ\text{C}$ | ngày | NASA POWER |
| `sm_rootzone` | Độ ẩm đất tầng rễ (0–100 cm) | % (0.0–1.0) | NASA SMAP |
| `sm_surface` | Độ ẩm đất tầng mặt (0–5 cm) | % (0.0–1.0) | NASA SMAP |
| `ndvi` | Chỉ số sinh thái thực vật chuẩn hóa | (0.0–1.0) | MODIS / Sentinel-2 |
| `nuoc_con_lai_mm` | Cán cân ẩm (Mưa trừ bốc thoát hơi nước) | mm | GPM - MOD16 ET |
