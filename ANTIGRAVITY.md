# Hướng Dẫn Phát Triển Cho AI Agent — Dự Án RotaNA (Yên Thành, Nghệ An)

## Triết lý Cốt lõi
- **Yêu cầu là số 1**: Luôn đối chiếu với [PROJECT_REQUIREMENTS.md](file:///PROJECT_REQUIREMENTS.md) để đảm bảo đi đúng định hướng Vựa lúa Huyện Yên Thành.
- **Tiêu chuẩn UI/UX Đồ Họa Cao Cấp**: **TUYỆT ĐỐI NÓI KHÔNG VỚI TƯỜNG CHỮ (NO WALLS OF TEXT)**. Toàn bộ thông tin phải được trực quan hóa thành Infographics, Card-based UI, Visual Timeline, Gauge Bars, và Interactive GIS Maps.
- **Code sạch & Kiến trúc Modular**: Tách biệt rõ ràng giữa tầng dữ liệu/thuật toán tính toán (`engine.py`) và tầng hiển thị giao diện (`views/`).

## Quy tắc & Tiêu chuẩn Dự án
- **Chú thích (Comment)**: Viết bằng **tiếng Việt**, ngắn gọn, giải thích rõ lý do kỹ thuật hoặc mục đích nông học.
- **Mã nguồn (Code)**: Đặt tên biến, hàm, module bằng tiếng Anh hoặc tiếng Việt không dấu chuẩn hóa, cấu trúc chuẩn PEP 8.
- **Quy tắc Agent**: Luôn tuân thủ các quy tắc trong `.antigravity/rules/comment.md`.

## Chu Trình Phát Triển 4 Bước (Generate - Review - Test - Push)
1. **Bước 1: Generate (Tạo/Sửa mã nguồn)**:
   - Đọc kỹ `PROJECT_REQUIREMENTS.md` và `docs/cores/03-frontend.md`.
   - Triển khai code hoàn chỉnh, không dùng placeholder TODO hay code giả.
2. **Bước 2: Review (Tự rà soát chất lượng)**:
   - Tự kiểm tra xem có đoạn văn bản nào thừa thãi, có radio/selectbox nào khô khan cần chuyển thành Card đồ họa không.
   - Dọn dẹp câu lệnh debug dư thừa.
3. **Bước 3: Test (Kiểm thử tự động)**:
   - Chạy lệnh kiểm tra import và biên dịch toàn bộ các module trong `views/` và `engine.py`.
   - Kiểm tra endpoint sức khỏe của Streamlit (`/_stcore/health`) trả về `200 OK`.
4. **Bước 4: Push (Đẩy code & Báo cáo)**:
   - Commit với thông điệp rõ ràng theo định dạng Conventional Commits.
   - Báo cáo kết quả trực quan đến người dùng.
