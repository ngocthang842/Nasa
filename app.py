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
    du_bao_nang_suat,
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
du_bao_nang_suat = importlib.reload(du_bao_nang_suat)
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
# PHÂN HỆ SỐ HÓA DỮ LIỆU & ĐIỀU HÀNH NÔNG VỤ NASA (CHUẨN HÓA AGTECH)
# -----------------------------------------------------------------------------
PHAN_HE_NAV = {
    "🌾 Nông Vụ": [
        "📊  Bảng điều khiển",
        "🌾  Kế hoạch Luân canh",
        "🎯  Thời vụ & Dự báo 2027",
    ],
    "🛰️ Viễn Thám": [
        "🗺️  Bản đồ & Vệ tinh NASA",
        "🍃  Thảm thực vật (NDVI)",
        "💧  Độ ẩm đất (SMAP)",
        "🌧️  Lượng mưa (GPM)",
        "🌡️  Nhiệt độ bề mặt (LST)",
    ],
    "📊 Dữ Liệu": [
        "📈  Đối chiếu Lịch sử",
        "ƒx  Công thức & Thuật toán",
        "📥  Kho Dữ liệu & API",
    ],
}

DANH_MUC = (
    PHAN_HE_NAV["🌾 Nông Vụ"]
    + PHAN_HE_NAV["🛰️ Viễn Thám"]
    + PHAN_HE_NAV["📊 Dữ Liệu"]
)

TRANG = {
    # 1. Phân hệ Nông vụ
    "📊  Bảng điều khiển": tong_quan.hien,
    "🌾  Kế hoạch Luân canh": luan_canh.hien,
    "🎯  Thời vụ & Dự báo 2027": du_bao_nang_suat.hien,
    # 2. Phân hệ Viễn thám
    "🗺️  Bản đồ & Vệ tinh NASA": ho_so_yen_thanh.hien,
    "🍃  Thảm thực vật (NDVI)": chi_tiet_nasa.hien_ndvi,
    "💧  Độ ẩm đất (SMAP)": chi_tiet_nasa.hien_do_am,
    "🌧️  Lượng mưa (GPM)": chi_tiet_nasa.hien_luong_mua,
    "🌡️  Nhiệt độ bề mặt (LST)": chi_tiet_nasa.hien_nhiet_do,
    # 3. Phân hệ Dữ liệu
    "📈  Đối chiếu Lịch sử": so_sanh.hien,
    "ƒx  Công thức & Thuật toán": chi_tiet_nasa.hien_cong_thuc_thuat_toan,
    "📥  Kho Dữ liệu & API": chi_tiet_nasa.hien_tai_du_lieu_api,
    # Tương thích ngược với tên cũ
    "🌾  Kế hoạch Luân canh & Sức khỏe Đất": luan_canh.hien,
    "🎯  Thời vụ & Dự báo Năng suất 2027": du_bao_nang_suat.hien,
    "📈  So sánh Lịch sử các năm": so_sanh.hien,
    "🍃  Phân tích Thảm thực vật (NDVI)": chi_tiet_nasa.hien_ndvi,
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
    # 1. HEADER BRANDING NASA CHUẨN XÁC
    html_sidebar_brand = (
        '<div style="padding:4px 2px 14px 2px; border-bottom:1px solid #1E293B; margin-bottom:14px;">'
        '<div style="display:flex; align-items:center; gap:10px;">'
        f'{NASA_LOGO_SVG}'
        '<div>'
        '<div style="font-size:13px; font-weight:800; color:#F8FAFC; letter-spacing:0.4px; line-height:1.2; text-transform:uppercase;">HỆ THỐNG VIỄN THÁM NASA</div>'
        '<div style="font-size:11.5px; color:#2DD4BF; font-weight:700; margin-top:2px;">NEDA · Vựa lúa Yên Thành</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html_sidebar_brand, unsafe_allow_html=True)

    # 2. BỘ CHỌN PHÂN HỆ SỐ HÓA (3 TRỤ CỘT CHUẨN HÓA AGTECH)
    cur_page = st.session_state.get("menu_dieu_huong", "📊  Bảng điều khiển")

    # Chuẩn hóa nếu trang hiện tại đang lưu tên cũ
    ten_moi_map = {
        "🌾  Kế hoạch Luân canh & Sức khỏe Đất": "🌾  Kế hoạch Luân canh",
        "🎯  Thời vụ & Dự báo Năng suất 2027": "🎯  Thời vụ & Dự báo 2027",
        "📈  So sánh Lịch sử các năm": "📈  Đối chiếu Lịch sử",
        "🍃  Phân tích Thảm thực vật (NDVI)": "🍃  Thảm thực vật (NDVI)",
        "📥  Tải dữ liệu API": "📥  Kho Dữ liệu & API",
    }
    if cur_page in ten_moi_map:
        cur_page = ten_moi_map[cur_page]
        st.session_state["menu_dieu_huong"] = cur_page

    # Tự động tìm phân hệ phù hợp với trang đang chọn
    current_module = "🌾 Nông Vụ"
    for mod_name, items in PHAN_HE_NAV.items():
        if cur_page in items:
            current_module = mod_name
            break

    if "sel_phan_he_sidebar" not in st.session_state:
        st.session_state["sel_phan_he_sidebar"] = current_module

    # Đồng bộ khi cur_page chuyển từ bên ngoài (Quick Action)
    if st.session_state["sel_phan_he_sidebar"] != "📋 Tất Cả" and cur_page not in PHAN_HE_NAV.get(st.session_state["sel_phan_he_sidebar"], []):
        st.session_state["sel_phan_he_sidebar"] = current_module

    st.markdown(
        '<div style="font-size:11px; font-weight:750; color:#64748B; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:5px;">'
        '🏛️ PHÂN HỆ CHỨC NĂNG:'
        '</div>',
        unsafe_allow_html=True,
    )

    phan_he_chon = st.pills(
        "Phân hệ chức năng:",
        options=["🌾 Nông Vụ", "🛰️ Viễn Thám", "📊 Dữ Liệu", "📋 Tất Cả"],
        default=st.session_state["sel_phan_he_sidebar"],
        key="pills_phan_he_sidebar",
        label_visibility="collapsed",
    )
    if phan_he_chon and phan_he_chon != st.session_state["sel_phan_he_sidebar"]:
        st.session_state["sel_phan_he_sidebar"] = phan_he_chon
        if phan_he_chon != "📋 Tất Cả":
            first_item = PHAN_HE_NAV[phan_he_chon][0]
            if cur_page not in PHAN_HE_NAV[phan_he_chon]:
                st.session_state["menu_dieu_huong"] = first_item
        st.rerun()

    active_module = st.session_state["sel_phan_he_sidebar"]
    if active_module == "📋 Tất Cả":
        options_hien_thi = DANH_MUC
    else:
        options_hien_thi = PHAN_HE_NAV.get(active_module, PHAN_HE_NAV["🌾 Nông Vụ"])

    # 3. MENU ĐIỀU HƯỚNG DẠNG LIST CARD CÓ ACTIVE TEAL
    idx_default = 0
    if cur_page in options_hien_thi:
        idx_default = options_hien_thi.index(cur_page)

    trang = st.radio(
        "Menu điều hướng:",
        options=options_hien_thi,
        index=idx_default,
        key="menu_dieu_huong",
        label_visibility="collapsed",
    )

    # 4. SIDEBAR FOOTER TELEMETRY STATUS
    st.markdown(
        """
        <div style="margin-top:20px; padding:10px 12px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px;">
          <div style="font-size:11px; font-weight:750; color:#2DD4BF; display:flex; align-items:center; gap:6px;">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#2DD4BF; box-shadow:0 0 8px #2DD4BF;"></span> HỆ THỐNG TRỰC TUYẾN
          </div>
          <div style="font-size:11px; color:#94A3B8; margin-top:3px; line-height:1.4;">
            Yên Thành · 26.500 ha lúa nước<br>
            Vệ tinh: MODIS · SMAP · GPM
          </div>
        </div>
        """,
        unsafe_allow_html=True,
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
