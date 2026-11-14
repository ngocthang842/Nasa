# Phân Hệ: Giám Sát Thời Gian Thực Vụ Lúa Yên Thành (Feature Spec)
# Mã định danh: F01-RICE-MONITORING

---

## 1. Mục Tiêu Nghiệp Vụ
Cung cấp bức tranh toàn cảnh về sức khỏe sinh khối lúa nước, diễn biến thời tiết (Gió Lào nắng nóng, mưa bão, độ ẩm đất tầng rễ) và mệnh lệnh nông học kịp thời cho bà con nông dân Huyện Yên Thành.

---

## 2. Các Thành Phần Giao Diện
1. **Master Ribbon Timeline**: 12 tháng chu kỳ sinh thái lúa (Gieo mạ, đẻ nhánh, làm đòng, trỗ bông, thu hoạch, cày ải).
2. **5 Thẻ Hero KPI**:
   - $T_{\max}$: Nhiệt độ tối cao đo từ vệ tinh.
   - Lượng mưa: Đo đạc từ vệ tinh NASA GPM.
   - Nắng nóng $\ge 35^\circ\text{C}$: Đếm số ngày xuất hiện gió Lào.
   - Độ ẩm ruộng lúa: Đo đạc vi ba tầng rễ từ NASA SMAP.
   - Sinh khối NDVI: Đo độ xanh thực vật từ MODIS/Sentinel.
3. **Bản đồ Số hóa & Ảnh Vệ tinh**: Tích hợp công nghệ Pan/Zoom mượt mà và chuyển đổi lớp phủ viễn thám thực tế cho 4 cụm xã.
4. **3 Mệnh Lệnh Nông Vụ Khẩn Cấp**: Nhiệm vụ trọng tâm bà con cần làm ngay trong tháng.
