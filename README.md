1. Dữ liệu lấy từ đâu? (Các file trong data/raw)
"Chúng ta có 9 file dữ liệu gốc lấy trực tiếp từ vệ tinh của NASA. Mình chia thành 3 nhóm chính:

Nhóm Cây trồng: Các file ndvi, evi, lai. Giúp biết cây đang xanh tốt hay úa vàng (đã lọc bỏ mây).

Nhóm Thời tiết & Nước: Các file mua, lst, smap, et, pet. Cho biết mưa bao nhiêu, đất khô hay ẩm, nắng nóng cỡ nào.

Nhóm Địa hình: File dem_slope, landcover, dat. Cho biết vùng nào dốc (dễ xói mòn), vùng nào trồng lúa.
(Chúng ta có 3 file power_... lấy từ NASA POWER - mình sẽ giải thích ngay sau đây)."

2. Tại sao lại có dữ liệu 11 năm? (Giải thích cái bạn thắc mắc)
"Có một điểm quan trọng mình cần làm rõ: Tại sao chúng ta lấy dữ liệu năm 2025 mà lại có file 11 năm?

Dữ liệu năm 2025: Là tình hình thực tế ĐANG DIỄN RA năm nay (ví dụ: tháng 4 có 10 ngày nắng).

Dữ liệu 11 năm (2015-2025): Là mức trung bình lịch sử.

Ví dụ dễ hiểu: Bác sĩ bảo huyết áp của bạn là 140. Bạn không biết đó là cao hay thấp cho đến khi so với mức bình thường (120). Dữ liệu 11 năm chính là "mức bình thường". Nhờ nó, hệ thống mới biết được năm 2025 này nắng nóng là bất thường hay bình thường để đưa ra cảnh báo."

3. Máy tính đã xử lý những gì? (File gop_du_lieu.py và rui_ro.py)
"Đưa 9 file thô đó lên Dashboard thì nông dân sẽ không đọc được. Nên chúng ta có các file code Python (như gop_du_lieu.py) làm nhiệm vụ:

Gộp dữ liệu từng ngày lại thành từng tháng.

Tính toán công thức (Quan trọng): Tính chỉ số ESI (căng thẳng nước của cây), Cân bằng nước (Mưa - Bốc hơi), và Đếm số ngày nắng nóng >35°C.

Từ đó, nó tự động gắn nhãn: Tháng nào là "Nắng nóng", tháng nào là "Mưa lớn gây xói mòn" (dựa vào độ dốc).

4. Giao diện Web hiển thị cho nông dân xem cái gì? (File app.py)
"Mở trình duyệt lên, nông dân sẽ thấy 4 phần rất dễ hiểu:

Bản đồ: Chọn huyện Yên Thành, Nghi Lộc hay Con Cuông.

3 Thẻ Đèn Giao Thông: Báo ngay tháng này Nắng nóng thế nào? Mưa bao nhiêu? Đất đủ ẩm không? (Màu xanh là an toàn, đỏ là nguy hiểm).

Lịch rủi ro 12 tháng: Nhìn vào cái lưới vuông, nông dân biết ngay tháng 4, 5 là tháng Gió Lào (ô đỏ), tháng 9, 10 là tháng mưa lũ (ô đỏ) để tránh gieo hạt.

Thanh trượt Kịch bản: Đây là phần "chọn luân canh". Nếu nông dân muốn ưu tiên "Giữ đất" (vì đất đang bạc màu), họ kéo thanh trượt. Hệ thống sẽ tự động tính điểm và gợi ý trồng Đậu xanh. Nếu ưu tiên "Kinh tế", nó gợi ý trồng Ngô/Đậu đen."