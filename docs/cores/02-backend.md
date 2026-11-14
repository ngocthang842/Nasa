# Kiến Trúc Tính Toán & Backend Logic (Backend Spec)
# Dự án: RotaNA — Vựa lúa Yên Thành

---

## 1. Cấu Trúc Module Backend

* `engine.py`: Module trung tâm xử lý dữ liệu, chấm điểm rủi ro mùa vụ, thuật toán gợi ý luân canh và phân tích khí hậu lịch sử 11 năm.
* `rui_ro.py`: Ma trận tính toán rủi ro nông học theo từng giai đoạn sinh trưởng của cây lúa nước.
* `gio_lao.py`: Thuật toán phân tích tần suất và cường độ gió Lào (hiệu ứng Foehn) tại lòng chảo Yên Thành.
* `views/`: Tầng giao diện Streamlit chuyên trách theo từng phân hệ.

---

## 2. Thuật Toán Gợi Ý Luân Canh Tự Động (`goi_y_to_hop_toi_uu`)
Thuật toán phân tích chuỗi dữ liệu lịch sử trong khoảng tháng của từng đợt để tìm ra cây trồng có:
1. Điểm rủi ro thời tiết thấp nhất ($RuiRo < 35\%$).
2. Khả năng cải tạo kết cấu đất và cắt đứt chu kỳ sâu bệnh (ví dụ: gối vụ màu Lạc/Ngô sau 2 vụ lúa).
3. Đảm bảo vụ Chiêm Xuân luôn được ưu tiên giống lúa thuần chất lượng cao (ST25, J02).
