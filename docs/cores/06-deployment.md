# Quy Trình Đóng Gói & Triển Khai (Deployment & Operations Guide)
# Dự án: RotaNA — Vựa lúa Yên Thành

---

## 1. Môi Trường Thực Thi
* **Ngôn ngữ**: Python 3.10 – 3.12.
* **Framework chính**: Streamlit, Plotly, Folium, Pandas, NumPy, Streamlit-Folium.
* **Cổng mặc định**: `8501`.

---

## 2. Các Phương Thức Triển Khai

### 2.1 Khởi chạy trên máy tính cục bộ (Local / Windows / macOS / Linux)
Sử dụng các kịch bản tiện ích đã tích hợp sẵn trong dự án:
```bash
# Trên Windows:
.\chay_web.bat
# hoặc PowerShell:
.\chay_web.ps1

# Trực tiếp bằng Python:
python -m streamlit run app.py --server.port 8501 --server.headless true
```

### 2.2 Triển khai trên Streamlit Community Cloud
1. Đẩy mã nguồn lên GitHub repository.
2. Kết nối repo tại [share.streamlit.io](https://share.streamlit.io).
3. Đặt Main file path là: `app.py`.
4. Điền cấu hình secrets nếu cần trong giao diện quản trị Cloud.

### 2.3 Triển khai bằng Docker (Containerized)
Sử dụng `Dockerfile` chuẩn cho Streamlit:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Lệnh đóng gói và chạy:
```bash
docker build -t rotana-yenthanh:latest .
docker run -p 8501:8501 rotana-yenthanh:latest
```

---

## 3. Giám Sát Hoạt Động (Healthcheck)
Kiểm tra tình trạng hoạt động của máy chủ qua endpoint:
```bash
curl -I http://localhost:8501/_stcore/health
# Kết quả hợp lệ: HTTP/1.1 200 OK
```
