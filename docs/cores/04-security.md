# Đặc Tả Bảo Mật & An Toàn Dữ Liệu (Security & Data Integrity Spec)

# Dự án: RotaNA — Vựa lúa Yên Thành

---

## 1. Quản Lý Khóa Bí Mật & API Key

Hệ thống kết nối với dịch vụ viễn thám NASA (NASA POWER, Earthdata Login) và dịch vụ bản đồ vệ tinh:

* Toàn bộ khóa truy cập (API Keys / Credentials) được quản lý qua tệp `.env` hoặc cơ chế bảo mật của Streamlit (`.streamlit/secrets.toml`).
* Tuyệt đối không commit tệp chứa thông tin nhạy cảm lên Git repository (đã khai báo trong `.gitignore`).

---

## 2. Bảo Vệ Tính Toàn Vẹn Của Dữ Liệu Viễn Thám (Data Integrity)

* **Quyền đọc độc quyền cho tầng giao diện**: Toàn bộ dữ liệu tại `data/processed/` và `data/raw/` được tầng `views/` đọc dưới dạng Read-Only.
* **Cơ chế Smart Imputation & Fallback**: Khi dữ liệu đo đạc vệ tinh trong tháng có khoảng trống (do mây mù cản trở MODIS hoặc chu kỳ vệ tinh SMAP chưa phủ tới), `engine.py` tự động bù đắp bằng dữ liệu chuẩn 11 năm của Huyện Yên Thành, đảm bảo không bao giờ làm sập giao diện người dùng.

---

## 3. Cấu Hình An Toàn Cho Máy Chủ Web Streamlit

* `enableCORS = false`: Ngăn chặn các cuộc gọi trái phép từ các domain ngoài.
* `enableXsrfProtection = true`: Chống tấn công giả mạo yêu cầu chéo trang (Cross-Site Request Forgery).
* `headless = true`: Chạy ngầm an toàn trên máy chủ nội bộ hoặc Cloud.
