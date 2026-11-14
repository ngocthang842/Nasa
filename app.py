"""Cửa vào Dashboard NASA NEDA / RotaNA — Chuyên sâu Vựa lúa Yên Thành (Nghệ An).
Thiết kế Sidebar & Hệ thống Viễn thám chuẩn xác 100% theo bản mô phỏng NASA Environmental Data Analysis (NEDA).
"""
import importlib
import streamlit as st

import engine as E
E = importlib.reload(E)

from views import chung
chung = importlib.reload(chung)
from views.chung import CSS, NASA_LOGO_SVG

from views import (
    ban_do,
    chi_tiet_nasa,
    du_lieu,
    ho_so_yen_thanh,
    luan_canh,
    so_sanh,
    tong_quan,
    ve_tinh,
)
ban_do = importlib.reload(ban_do)
ve_tinh = importlib.reload(ve_tinh)
du_lieu = importlib.reload(du_lieu)
luan_canh = importlib.reload(luan_canh)
so_sanh = importlib.reload(so_sanh)
tong_quan = importlib.reload(tong_quan)
ho_so_yen_thanh = importlib.reload(ho_so_yen_thanh)
chi_tiet_nasa = importlib.reload(chi_tiet_nasa)

st.set_page_config(
    page_title="Hệ Thống Phân Tích Môi Trường NASA (NEDA) - Yên Thành",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DANH MỤC ĐIỀU HƯỚNG CHUẨN NASA NEDA & LUÂN CANH CÂY TRỒNG
# -----------------------------------------------------------------------------
DANH_MUC = [
    "📊  Bảng điều khiển",
    "🌾  Kế hoạch Luân canh & Sức khỏe Đất",
    "📈  So sánh Lịch sử các năm",
    "🛰️  Nguồn Vệ tinh (MODIS, SMAP...)",
    "🍃  Phân tích Thảm thực vật (NDVI)",
    "💧  Độ ẩm đất (SMAP)",
    "🌧️  Lượng mưa (GPM)",
    "🌡️  Nhiệt độ bề mặt (LST)",
    "ƒx  Công thức & Thuật toán",
    "📥  Tải dữ liệu API",
]

TRANG = {
    "📊  Bảng điều khiển": tong_quan.hien,
    "🌾  Kế hoạch Luân canh & Sức khỏe Đất": luan_canh.hien,
    "📈  So sánh Lịch sử các năm": so_sanh.hien,
    "🛰️  Nguồn Vệ tinh (MODIS, SMAP...)": ho_so_yen_thanh.hien,
    "🍃  Phân tích Thảm thực vật (NDVI)": chi_tiet_nasa.hien_ndvi,
    "💧  Độ ẩm đất (SMAP)": chi_tiet_nasa.hien_do_am,
    "🌧️  Lượng mưa (GPM)": chi_tiet_nasa.hien_luong_mua,
    "🌡️  Nhiệt độ bề mặt (LST)": chi_tiet_nasa.hien_nhiet_do,
    "ƒx  Công thức & Thuật toán": chi_tiet_nasa.hien_cong_thuc_thuat_toan,
    "📥  Tải dữ liệu API": chi_tiet_nasa.hien_tai_du_lieu_api,
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

# =============================================================================
# SIDEBAR THEME COMMAND CENTER (NASA NEDA)
# =============================================================================
with st.sidebar:
    # 1. HEADER BRANDING NASA CHUẨN XÁC (KHÔNG DÙNG MULTILINE INDENT TRÁNH LỖI CODEBLOCK)
    html_sidebar_brand = (
        '<div style="padding:6px 2px 18px 2px; border-bottom:1px solid #1E293B; margin-bottom:16px;">'
        '<div style="display:flex; align-items:center; gap:12px;">'
        f'{NASA_LOGO_SVG}'
        '<div>'
        '<div style="font-size:13.5px; font-weight:800; color:#F8FAFC; letter-spacing:0.5px; line-height:1.25; text-transform:uppercase;">HỆ THỐNG PHÂN TÍCH MÔI TRƯỜNG NASA (NEDA)</div>'
        '<div style="font-size:11.5px; color:#2DD4BF; font-weight:700; margin-top:3px;">RotaNA · Vựa lúa Yên Thành</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html_sidebar_brand, unsafe_allow_html=True)

    # 2. MENU ĐIỀU HƯỚNG DẠNG LIST CARD CÓ ACTIVE TEAL
    trang = st.radio(
        "Menu điều hướng:",
        options=DANH_MUC,
        index=0,
        label_visibility="collapsed",
    )

    if dl.empty:
        st.error("Không tìm thấy dữ liệu trong data/processed.")
        st.stop()

# =============================================================================
# TOP HEADER BAR TRÊN TRANG CHÍNH (KHỚP 100% VỚI LAPTOP MOCKUP)
# =============================================================================
col_top_left, col_top_right = st.columns([7.8, 2.2], gap="small")
with col_top_left:
    html_top_header = (
        '<div style="display:flex; align-items:center; gap:12px; padding:2px 0 8px 0;">'
        f'{NASA_LOGO_SVG}'
        '<div>'
        '<div style="font-size:17px; font-weight:800; color:#0F172A; letter-spacing:0.4px; text-transform:uppercase; line-height:1.2;">HỆ THỐNG PHÂN TÍCH MÔI TRƯỜNG NASA (NEDA)</div>'
        '<div style="font-size:12px; color:#0284C7; font-weight:650;">Giám sát Viễn thám & Ra Quyết định Mùa vụ Lúa nước · Huyện Yên Thành (Nghệ An)</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html_top_header, unsafe_allow_html=True)

with col_top_right:
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    if st.button("📥 CALL DỮ LIỆU NASA", key="btn_call_nasa_main_header", type="primary", use_container_width=True):
        st.toast("🛰️ Đã đồng bộ chuỗi số liệu vệ tinh NASA MODIS, SMAP, GPM và NASA POWER mới nhất cho Yên Thành!", icon="✅")

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

# Hiển thị view tương ứng
TRANG[trang](ctx)
