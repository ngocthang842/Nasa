"""Cửa vào Dashboard RotaNA — Chuyên sâu Vựa lúa Yên Thành (Nghệ An).

Hệ thống hỗ trợ ra quyết định nông nghiệp tập trung vào cây lúa nước và các mô hình
luân canh lúa – màu (Lạc, Ngô, Rau màu vụ đông) tại huyện Yên Thành, Nghệ An.
Sidebar chỉ chứa logo và danh mục các trang chính, toàn bộ thông tin chi tiết được hiển thị trên trang web.
"""
import importlib
import streamlit as st

import engine as E
E = importlib.reload(E)

from views import chung
chung = importlib.reload(chung)
from views.chung import CSS

from views import ban_do, du_lieu, ho_so_yen_thanh, luan_canh, so_sanh, tong_quan, ve_tinh
ban_do = importlib.reload(ban_do)
ve_tinh = importlib.reload(ve_tinh)
du_lieu = importlib.reload(du_lieu)
luan_canh = importlib.reload(luan_canh)
so_sanh = importlib.reload(so_sanh)
tong_quan = importlib.reload(tong_quan)
ho_so_yen_thanh = importlib.reload(ho_so_yen_thanh)

st.set_page_config(page_title="RotaNA - Vựa lúa Yên Thành (Nghệ An)", page_icon="🌾", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

# DANH MỤC TRANG TRÊN SIDEBAR (TÁCH HỒ SƠ YÊN THÀNH THÀNH 1 TRANG RIÊNG)
TRANG = {
    "🌾  Tổng quan Mùa vụ Lúa": tong_quan.hien,
    "🔄  Kế hoạch Đợt vụ & Luân canh": luan_canh.hien,
    "📈  So sánh Lịch sử các năm": so_sanh.hien,
    "🏛️  Hồ sơ Vựa lúa Yên Thành": ho_so_yen_thanh.hien,
    "📁  Dữ liệu Vệ tinh NASA": du_lieu.hien,
}


@st.cache_data(show_spinner=False)
def tai():
    d = E.doc_thang()
    diem = E.bang_diem(d) if len(d) else d
    return d, diem, E.doc_nam(), E.doc_tb()


dl, diem, nam_df, tb_df = tai()
vung = "Yên Thành"
years = sorted(dl[dl.huyen == vung].year.unique()) if not dl.empty else [2024, 2025, 2026]

# Quản lý năm kế hoạch trong session_state
if "nam_ke_hoach" not in st.session_state:
    st.session_state["nam_ke_hoach"] = years[-1] if years else 2026

nam = st.session_state["nam_ke_hoach"]

with st.sidebar:
    # 1. HEADER BRANDING (THEME TRẮNG TINH TẾ)
    st.markdown(
        """
        <div style="padding: 4px 0 16px 0;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="background:#F1F5F9; border:1.5px solid #E2E8F0; border-radius:12px; padding:7px 11px; font-size:24px; box-shadow:0 2px 6px rgba(0,0,0,0.04);">🌾</div>
                <div>
                    <div style="font-size:22px; font-weight:800; color:#0F172A; letter-spacing:-0.5px; line-height:1.1;">RotaNA</div>
                    <div style="font-size:12px; color:#64748B; font-weight:500; margin-top:3px;">Vựa lúa Yên Thành · Nghệ An</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. MENU ĐIỀU HƯỚNG DẠNG THẺ (SIDEBAR CHỈ GIỮ MENU, ĐÃ XÓA KHỐI DƯ THỪA)
    trang = st.radio("Chọn trang", list(TRANG.keys()), label_visibility="collapsed")

    if dl.empty:
        st.error("Không tìm thấy dữ liệu trong data/processed.")
        st.stop()

# Mặc định tháng 4 nếu chưa chọn
thang_mac_dinh = 4
cur = dl[(dl.year == nam) & (dl.month == thang_mac_dinh) & (dl.huyen == vung)]
if cur.empty:
    cur = dl[(dl.year == nam) & (dl.huyen == vung)]
    if cur.empty:
        cur = dl[dl.huyen == vung]

ctx = dict(
    dl=dl,
    diem=diem,
    nam_df=nam_df,
    tb_df=tb_df,
    nam=nam,
    thang=thang_mac_dinh,
    vung=vung,
    years=years,
    huyens=["Yên Thành"],
    r=cur.iloc[0] if not cur.empty else None,
)

TRANG[trang](ctx)
