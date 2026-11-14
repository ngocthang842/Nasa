# Quy Chuẩn Kiểm Thử Tự Động (Testing Spec)
# Dự án: RotaNA — Vựa lúa Yên Thành

---

## 1. Mục Tiêu Kiểm Thử
Tất cả các thay đổi về mã nguồn phải thỏa mãn 2 điều kiện tiên quyết trước khi đẩy code (Push):
1. **Kiểm thử biên dịch & import 100% không lỗi**:
   ```bash
   python -c "import engine as E; from views import tong_quan, ban_do, ve_tinh, luan_canh, so_sanh, ho_so_yen_thanh, du_lieu; print('TEST PASS 100%')"
   ```
2. **Kiểm thử máy chủ Web Streamlit**:
   Endpoint `http://localhost:8501/_stcore/health` phải phản hồi mã trạng thái `HTTP 200 OK`.
