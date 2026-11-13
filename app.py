from datetime import date
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os

# Cấu hình trang tối ưu Mobile & Desktop
st.set_page_config(
    page_title="RotaNA · Nông Nghiệp Vệ Tinh NASA",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# GIAO DIỆN CHUẨN SMARTPHONE & DESKTOP (RESPONSIVE CSS)
# ==========================================
st.markdown("""
<style>
/* 1. Phông chữ và khoảng cách chung */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* 2. Tiêu đề không bị cắt chữ và co giãn theo kích thước màn hình */
h1 {
    font-size: clamp(20px, 4vw, 28px) !important;
    font-weight: 800 !important;
    color: #1b5e20 !important;
    line-height: 1.3 !important;
    padding-bottom: 4px !important;
    margin-bottom: 6px !important;
}
h2, h3 {
    font-size: clamp(16px, 3vw, 22px) !important;
    font-weight: 700 !important;
    color: #263238 !important;
    margin-top: 14px !important;
}

/* 3. Tối ưu thanh Tabs để vuốt mượt mà trên điện thoại */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding: 4px 2px 10px 2px;
    -webkit-overflow-scrolling: touch;
}
.stTabs [data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    border-radius: 20px !important;
    background-color: #f1f5f9 !important;
    color: #475569 !important;
    border: none !important;
    white-space: nowrap !important;
    min-height: 42px !important;
    display: inline-flex !important;
    align-items: center !important;
}
.stTabs [aria-selected="true"] {
    background-color: #1b5e20 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(27, 94, 32, 0.25) !important;
}

/* 4. Thẻ trạng thái Glassmorphism */
.metric-card {
    border-radius: 14px;
    padding: 14px 16px;
    color: white;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    margin-bottom: 10px;
    transition: transform 0.2s ease;
}
.metric-card:active {
    transform: scale(0.98);
}

/* 5. Tối ưu các nút trượt và chọn trên màn hình cảm ứng */
div[data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 10px !important;
}
.stSlider {
    padding-top: 6px !important;
    padding-bottom: 10px !important;
}

/* 6. Tránh thanh cuộn ngang ngoài ý muốn trên Mobile */
.main .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    padding-left: clamp(0.8rem, 3vw, 2.5rem) !important;
    padding-right: clamp(0.8rem, 3vw, 2.5rem) !important;
    max-width: 1300px;
}
</style>
""", unsafe_allow_html=True)

TEN = {"Yen Thanh": "Yên Thành", "Nghi Loc": "Nghi Lộc", "Con Cuong": "Con Cuông"}
VUNG = {"Yen Thanh": "Đồng bằng chuyên lúa", "Nghi Loc": "Ven biển, đất cát", "Con Cuong": "Đồi núi dốc"}
ICON_VUNG = {"Yen Thanh": "🌾", "Nghi Loc": "🌊", "Con Cuong": "⛰️"}

def lay_ten(h):
    return TEN.get(h, str(h))

def lay_vung(h):
    return VUNG.get(h, "Vùng canh tác mới")

def lay_icon(h):
    return ICON_VUNG.get(h, "🌱")


@st.cache_data
def tai_du_lieu():
    return pd.read_csv("data/processed/rui_ro_huyen_thang.csv", parse_dates=["thang"])


bang = tai_du_lieu()
danh_sach_huyen = bang["huyen"].unique().tolist()

# ==========================================
# KHU VỰC ĐIỀU KHIỂN NHANH (TOP BAR - PHÙ HỢP CẢ MOBILE & DESKTOP)
# ==========================================
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
    <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:32px;">🌾</span>
        <div>
            <h1 style="margin:0;padding:0;">RotaNA · Thích Ứng Nông Nghiệp</h1>
            <p style="margin:0;font-size:13px;color:#546e7a;font-weight:500;">Dữ liệu Vệ tinh NASA 2025 • Hỗ trợ ra quyết định luân canh Nghệ An</p>
        </div>
    </div>
    <div style="background:#e8f5e9;color:#1b5e20;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;display:inline-block;">
        🚀 NASA Space Apps 2026
    </div>
</div>
""", unsafe_allow_html=True)

# Bộ chọn Địa bàn và Tháng to rõ, dễ bấm trên smartphone
col_sel_huyen, col_sel_thang = st.columns([1, 1])

with col_sel_huyen:
    huyen = st.selectbox(
        "📍 Chọn Địa Bàn Nghiên Cứu",
        danh_sach_huyen,
        format_func=lambda h: f"{lay_icon(h)} {lay_ten(h)} ({lay_vung(h)})",
        index=0
    )

with col_sel_thang:
    thang = st.select_slider(
        "📅 Chọn Thời Điểm Mùa Vụ",
        options=list(range(1, 13)),
        value=date.today().month,
        format_func=lambda t: f"Tháng {t}"
    )

d = bang[bang["huyen"] == huyen].sort_values("thang_so").reset_index(drop=True)
hien = d[d["thang_so"] == thang].iloc[0]
doi_nui = bool(d["nhanh2_xoi_mon"].any())

# ==========================================
# 3 THẺ ĐÈN GIAO THÔNG (TRẠNG THÁI KHÍ HẬU THÁNG)
# ==========================================
def the(tieu_de, noi_dung, phu, mau):
    return (f'<div class="metric-card" style="background:{mau};">'
            f'<div style="font-size:13px;opacity:0.9;font-weight:600;">{tieu_de}</div>'
            f'<div style="font-size:22px;font-weight:800;margin:4px 0;">{noi_dung}</div>'
            f'<div style="font-size:13px;opacity:0.95;">{phu}</div></div>')


if hien["muc_kho_nong"] == 2:
    nong = ("Rất nóng, đất khô", "#C62828")
elif hien["muc_kho_nong"] == 1:
    nong = ("Nắng nóng", "#EF6C00")
else:
    nong = ("Bình thường", "#2E7D32")
ngay_nong = f"TB {hien['nong35_tb11nam']:.0f} ngày/tháng nắng ≥ 35°C (chu kỳ 11 năm)"

mm = hien["mua_mm"]
if hien["nhanh3_ung_ngap"]:
    mua = ("Mưa rất lớn, dễ úng", "#1565C0")
elif hien["nhanh2_xoi_mon"]:
    mua = ("Mưa lớn, dễ xói mòn", "#6D4C41")
elif mm < 50:
    mua = ("Ít mưa, khô hạn", "#F57F17")
elif mm < 200:
    mua = ("Mưa vừa ôn hòa", "#2E7D32")
else:
    mua = ("Mưa nhiều", "#0277BD")

sm = hien["sm_rootzone"] * 100
q25, q75 = (d["sm_rootzone"].quantile([0.25, 0.75]) * 100).tolist()
if sm <= q25:
    dat = ("Đất khá khô", "#EF6C00")
elif sm >= q75:
    dat = ("Đất rất ẩm", "#0277BD")
else:
    dat = ("Đất đủ ẩm", "#2E7D32")

c1, c2, c3 = st.columns(3)
c1.markdown(the("☀️ Nắng nóng (POWER)", nong[0], ngay_nong, nong[1]), unsafe_allow_html=True)
c2.markdown(the("🌧️ Lượng mưa (GPM)", mua[0], f"{mm:.0f} mm trong tháng", mua[1]), unsafe_allow_html=True)
c3.markdown(the("🌱 Độ ẩm vùng rễ (SMAP)", dat[0], f"Độ ẩm tầng rễ {sm:.0f}%", dat[1]), unsafe_allow_html=True)

# ==========================================
# HÀM TẠO MÔ HÌNH 3D ISOMETRIC
# ==========================================
def tao_khoi_3d_isometric(hien_val, huyen_key):
    fig_3d = go.Figure()
    grid_n = 22
    x_coords = np.linspace(-5, 5, grid_n)
    y_coords = np.linspace(-5, 5, grid_n)
    X, Y = np.meshgrid(x_coords, y_coords)

    do_doc = float(hien_val.get("do_doc_do", 5.0))
    do_cao = float(hien_val.get("do_cao_m", 50.0))
    mua_thang = float(hien_val.get("mua_mm", 0.0))
    val_ndvi = float(hien_val.get("ndvi", 0.5))
    val_lai = float(hien_val.get("lai", 1.0))
    val_sm = float(hien_val.get("sm_rootzone", 0.3))
    val_tmax = float(hien_val.get("tmax_2025", 30.0))
    val_lst = float(hien_val.get("lst_c", 28.0))
    val_esi = float(hien_val.get("esi", 0.6))
    pct_cat = float(hien_val.get("cat_pct", 40.0))
    pct_set = float(hien_val.get("set_pct", 25.0))
    val_carbon = float(hien_val.get("carbon_huu_co_g_kg", 15.0))

    if huyen_key == "Con Cuong":
        amp = min(1.8, max(0.7, do_doc / 7.0))
        Z_topo = 2.2 + amp * np.sin(X * 0.45) * np.cos(Y * 0.35) + 0.35 * np.sin((X + Y) * 0.4)
    elif huyen_key == "Nghi Loc":
        Z_topo = 1.9 + 0.25 * (X / 5.0) + 0.1 * np.cos(Y * 0.4)
    else:
        Z_topo = 2.0 + 0.15 * np.sin(X * 0.3) * np.cos(Y * 0.3)

    Z_bottom = np.zeros_like(X)

    # 1. Bề mặt đất
    soil_cs = [[0, '#8D6E63'], [0.5, '#5D4037'], [1, '#3E2723']] if val_sm >= 0.25 else [[0, '#D7CCC8'], [0.5, '#A1887F'], [1, '#8D6E63']]
    text_topo = [[f"<b>Tầng 3: Bề mặt đất (SRTM)</b><br>Độ cao: {do_cao:.0f}m · Độ dốc: {do_doc:.1f}°<br>Nhiệt đất LST: {val_lst:.1f}°C<br>Đất: {pct_cat:.0f}% Cát, {pct_set:.0f}% Sét" for _ in range(grid_n)] for _ in range(grid_n)]
    fig_3d.add_trace(go.Surface(
        x=X, y=Y, z=Z_topo,
        colorscale=soil_cs, cmin=1.0, cmax=4.0, showscale=False,
        name="Mặt đất SRTM", hoverinfo="text", text=text_topo, opacity=0.96
    ))

    # 2. Vách cắt lớp lòng đất
    X_f = np.array([X[0, :], X[0, :]])
    Y_f = np.array([Y[0, :], Y[0, :]])
    Z_f = np.array([Z_bottom[0, :], Z_topo[0, :]])
    fig_3d.add_trace(go.Surface(x=X_f, y=Y_f, z=Z_f, showscale=False, colorscale='Brwnyl', opacity=0.94, name="Vách đất trước", hoverinfo="skip"))

    X_r = np.array([X[:, -1], X[:, -1]])
    Y_r = np.array([Y[:, -1], Y[:, -1]])
    Z_r = np.array([Z_bottom[:, -1], Z_topo[:, -1]])
    fig_3d.add_trace(go.Surface(x=X_r, y=Y_r, z=Z_r, showscale=False, colorscale='Brwnyl', opacity=0.94, name="Vách đất bên", hoverinfo="skip"))

    # 3. Đáy nước ngầm SMAP
    root_cs = [[0, '#0D47A1'], [0.5, '#1976D2'], [1, '#42A5F5']] if val_sm >= 0.3 else [[0, '#3E2723'], [0.5, '#4E342E'], [1, '#6D4C41']]
    stt_dat = "Đủ nước tích trữ" if val_sm >= 0.28 else "Khô hạn tầng sâu"
    text_base = [[f"<b>Tầng 4: Lòng đất & Rễ (SMAP)</b><br>Độ ẩm rễ: {val_sm*100:.1f}%<br>SOC: {val_carbon:.1f} g/kg<br>Trạng thái: {stt_dat}" for _ in range(grid_n)] for _ in range(grid_n)]
    fig_3d.add_trace(go.Surface(
        x=X, y=Y, z=Z_bottom,
        colorscale=root_cs, showscale=False, opacity=0.9,
        name="Đáy nước ngầm SMAP", hoverinfo="text", text=text_base
    ))

    # 4. Tán cây sinh khối MODIS
    Z_canopy = Z_topo + 0.35 + 0.08 * np.sin(X * 2) * np.cos(Y * 2)
    if val_ndvi >= 0.65:
        ndvi_cs = [[0, '#1b5e20'], [0.5, '#2e7d32'], [1, '#43a047']]
    elif val_ndvi >= 0.45:
        ndvi_cs = [[0, '#558b2f'], [0.5, '#7cb342'], [1, '#9ccc65']]
    else:
        ndvi_cs = [[0, '#e65100'], [0.5, '#f57c00'], [1, '#ffb74d']]

    text_canopy = [[f"<b>Tầng 2: Tán cây (MODIS)</b><br>NDVI: {val_ndvi:.2f} · LAI: {val_lai:.1f}<br>Stress bốc hơi ESI: {val_esi:.2f}" for _ in range(grid_n)] for _ in range(grid_n)]
    fig_3d.add_trace(go.Surface(
        x=X, y=Y, z=Z_canopy,
        colorscale=ndvi_cs, showscale=False, opacity=0.88,
        name="Tán lá MODIS", hoverinfo="text", text=text_canopy
    ))

    # 5. Hệ rễ cây 3D
    root_x, root_y, root_z = [], [], []
    root_nodes = [-2.5, 0.0, 2.5]
    for rx in root_nodes:
        for ry in root_nodes:
            root_x.extend([rx, rx, rx + 0.35, None, rx, rx - 0.3, None])
            root_y.extend([ry, ry, ry + 0.3, None, ry, ry - 0.35, None])
            root_z.extend([2.0, 1.2, 0.3, None, 2.0, 0.7, None])
    fig_3d.add_trace(go.Scatter3d(
        x=root_x, y=root_y, z=root_z, mode="lines",
        line=dict(color="#BCAAA4", width=4),
        name="Hệ rễ cây ngầm", hoverinfo="skip"
    ))

    # 6. Khí quyển & Mưa
    Z_cloud = np.full_like(X, 6.2) + 0.15 * np.cos(X) * np.sin(Y)
    cloud_cs = [[0, '#90CAF9'], [0.5, '#64B5F6'], [1, '#42A5F5']] if mua_thang >= 50 else [[0, '#FFF9C4'], [0.5, '#FFF59D'], [1, '#FFE082']]
    text_cloud = [[f"<b>Tầng 1: Khí quyển</b><br>Mưa GPM: {mua_thang:.0f} mm<br>Nhiệt độ Tmax: {val_tmax:.1f}°C" for _ in range(grid_n)] for _ in range(grid_n)]
    fig_3d.add_trace(go.Surface(
        x=X, y=Y, z=Z_cloud,
        colorscale=cloud_cs, showscale=False, opacity=0.45,
        name="Tầng khí quyển", hoverinfo="text", text=text_cloud
    ))

    if mua_thang >= 30:
        np.random.seed(42)
        n_drops = min(75, int(mua_thang / 2.5))
        rx = np.random.uniform(-4.5, 4.5, n_drops)
        ry = np.random.uniform(-4.5, 4.5, n_drops)
        rz_top = np.random.uniform(5.5, 6.0, n_drops)
        rz_bot = rz_top - 1.4
        rain_x, rain_y, rain_z = [], [], []
        for i in range(n_drops):
            rain_x.extend([rx[i], rx[i], None])
            rain_y.extend([ry[i], ry[i], None])
            rain_z.extend([rz_top[i], rz_bot[i], None])
        fig_3d.add_trace(go.Scatter3d(
            x=rain_x, y=rain_y, z=rain_z, mode="lines",
            line=dict(color="#0288D1", width=3),
            name=f"Mưa GPM ({mua_thang:.0f}mm)", hoverinfo="skip"
        ))
    else:
        fig_3d.add_trace(go.Scatter3d(
            x=[3.5], y=[3.5], z=[6.8], mode="markers+text",
            marker=dict(size=16, color="#FF5722", symbol="circle"),
            text=["☀️ Nắng nóng"], textposition="bottom center",
            name=f"Nắng Tmax {val_tmax:.1f}°C"
        ))

    # Cấu hình Isometric chuẩn, không khoá cảm ứng cuộn màn hình
    fig_3d.update_layout(
        template="plotly_white",
        height=460,
        margin=dict(l=0, r=0, t=10, b=10),
        scene=dict(
            camera=dict(
                eye=dict(x=1.65, y=-1.65, z=1.25),
                projection=dict(type="orthographic")
            ),
            xaxis=dict(showbackground=False, showticklabels=False, title="", showgrid=False, zeroline=False),
            yaxis=dict(showbackground=False, showticklabels=False, title="", showgrid=False, zeroline=False),
            zaxis=dict(showbackground=False, showticklabels=False, title="", showgrid=False, zeroline=False),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.75)
        ),
        legend=dict(orientation="h", y=0.01, x=0.02, bgcolor="rgba(255,255,255,0.85)")
    )
    return fig_3d


# ==========================================
# CẤU TRÚC 5 TABS CHUẨN SMARTPHONE & DASHBOARD
# ==========================================
tab_3d, tab_map, tab_scenario, tab_calendar, tab_guide = st.tabs([
    "🧊 Sa Bàn 3D",
    "🗺️ Bản Đồ Vệ Tinh",
    "⚖️ Kịch Bản Luân Canh",
    "📅 Lịch Khí Hậu 12T",
    "🌾 Sổ Tay Nhà Nông"
])

# ------------------------------------------
# TAB 1: SA BÀN 3D SINH THÁI
# ------------------------------------------
with tab_3d:
    st.subheader("🧊 Sa Bàn 3D Isometric: Cắt Lớp Sinh Thái 4 Tầng")
    st.caption("Chạm & kéo để xoay 360° khối lập phương quan sát chu trình Nước - Đất - Cây trồng từ 4 vệ tinh NASA.")

    col_3d_l, col_3d_r = st.columns([13, 7])

    with col_3d_l:
        fig_iso = tao_khoi_3d_isometric(hien, huyen)
        # config={'scrollZoom': False} để khi vuốt trên smartphone không bị kẹt cảm ứng cuộn trang!
        st.plotly_chart(fig_iso, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

    with col_3d_r:
        val_ndvi = hien['ndvi']
        val_lai = hien['lai']
        val_esi = hien['esi']
        val_sm = hien['sm_rootzone'] * 100
        val_mua = hien['mua_mm']
        val_tmax = hien['tmax_2025']
        val_doc = hien['do_doc_do']
        val_cao = hien['do_cao_m']
        val_lst = hien['lst_c']
        val_soc = hien['carbon_huu_co_g_kg']

        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:8px;margin-top:6px;">
            <div style="background:#e3f2fd;border-left:5px solid #1976d2;padding:10px 12px;border-radius:8px;">
                <b style="color:#0d47a1;font-size:14px;">☁️ Tầng 1: Khí quyển (GPM & POWER)</b><br>
                <span style="font-size:13px;color:#263238;">• Lượng mưa: <b>{val_mua:.0f} mm</b><br>• Nhiệt độ tối đa: <b>{val_tmax:.1f}°C</b> ({'Rất nóng' if val_tmax>=35 else 'Ôn hòa'})</span>
            </div>
            <div style="background:#e8f5e9;border-left:5px solid #388e3c;padding:10px 12px;border-radius:8px;">
                <b style="color:#1b5e20;font-size:14px;">🌿 Tầng 2: Tán cây sinh khối (MODIS)</b><br>
                <span style="font-size:13px;color:#263238;">• NDVI: <b>{val_ndvi:.2f}</b> · LAI: <b>{val_lai:.1f}</b><br>• Stress bốc hơi ESI: <b>{val_esi:.2f}</b> ({'Stress nước' if val_esi<0.5 else 'Bình thường'})</span>
            </div>
            <div style="background:#efebe9;border-left:5px solid #795548;padding:10px 12px;border-radius:8px;">
                <b style="color:#3e2723;font-size:14px;">⛰️ Tầng 3: Mặt đất & Địa hình (SRTM)</b><br>
                <span style="font-size:13px;color:#263238;">• Độ dốc: <b>{val_doc:.1f}°</b> · Cao độ: <b>{val_cao:.0f} m</b><br>• Nhiệt bề mặt LST: <b>{val_lst:.1f}°C</b></span>
            </div>
            <div style="background:#ede7f6;border-left:5px solid #512da8;padding:10px 12px;border-radius:8px;">
                <b style="color:#311b92;font-size:14px;">💧 Tầng 4: Lòng đất & Rễ ngầm (SMAP)</b><br>
                <span style="font-size:13px;color:#263238;">• Độ ẩm rễ: <b>{val_sm:.0f}%</b> ({'Ẩm tốt' if val_sm>=28 else 'Khô cằn'})<br>• Carbon hữu cơ SOC: <b>{val_soc:.1f} g/kg</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("💡 *Mẹo: Bạn có thể chạm xoay khối 3D để xem mặt cắt rễ cây ăn sâu trong lòng đất.*")

# ------------------------------------------
# TAB 2: BẢN ĐỒ VỆ TINH NGHỆ AN
# ------------------------------------------
with tab_map:
    st.subheader(f"🗺️ Bản Đồ Vệ Tinh Địa Bàn: {lay_icon(huyen)} {lay_ten(huyen)}")
    st.caption("Xem ảnh vệ tinh độ phân giải cao phóng sát mặt đất: soi rõ từng cánh đồng lúa, bờ vùng bờ thửa, sông ngòi và kênh mương.")

    col_map_opt1, col_map_opt2 = st.columns([13, 7])
    with col_map_opt1:
        che_do_xem = st.radio(
            "Cấp độ phóng to:",
            [f"🔎 Phóng sát Cánh Đồng & Xã (Siêu nét)", f"🌾 Toàn Huyện {lay_ten(huyen)}", "🌐 Toàn tỉnh Nghệ An"],
            index=0,
            horizontal=True
        )
    with col_map_opt2:
        lop_nen = st.radio(
            "Lớp bản đồ nền:",
            ["🛰️ Ảnh Vệ Tinh Trái Đất (Google)", "🗺️ Bản Đồ Đường Xá (OSM)"],
            horizontal=True
        )

    geojson_path = "data/raw/ranh_gioi_huyen.geojson"
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        # Tọa độ trung tâm cánh đồng lúa và ranh giới từng huyện
        THONG_TIN_MAP = {
            "Con Cuong": {
                "center": [19.0450, 104.8950],  # Vòng cung thung lũng lúa sông Lam & TT Con Cuông
                "zoom_sat": 13,
                "bounds": [[18.7763, 104.5290], [19.3524, 105.0494]],
                "vung": "Miền núi phía Tây (sát Vườn Quốc Gia Pù Mát)",
                "thuy_loi": "Thượng lưu sông Lam & sông Giăng",
                "dac_diem": "Độ dốc lớn, thung lũng sông uốn lượn, rừng đầu nguồn Pù Mát."
            },
            "Nghi Loc": {
                "center": [18.7980, 105.6200],  # Cánh đồng cát và TT Quán Hành
                "zoom_sat": 13,
                "bounds": [[18.6880, 105.4669], [18.8978, 105.7575]],
                "vung": "Vùng ven biển Đông & Bán sơn địa",
                "thuy_loi": "Sông Cấm & Hệ thống kênh ngọt hạ lưu",
                "dac_diem": "Đất cát pha ven biển, cồn cát ven sông Cấm đổ ra vịnh Cửa Lò."
            },
            "Yen Thanh": {
                "center": [19.0076, 105.4475],  # Vựa lúa trung tâm quanh TT Yên Thành & Kênh Vách Bắc
                "zoom_sat": 13,
                "bounds": [[18.8766, 105.2981], [19.1659, 105.5801]],
                "vung": "Vựa lúa đồng bằng trung tâm Nghệ An",
                "thuy_loi": "Đại thủy nông Ba Ra Đô Lương & Kênh Vách Bắc",
                "dac_diem": "Vựa lúa lớn nhất Nghệ An, mạng lưới kênh mương thủy lợi ô bàn cờ."
            }
        }

        h_info = THONG_TIN_MAP.get(huyen, THONG_TIN_MAP["Yen Thanh"])

        # 1. Khởi tạo bản đồ: Đặt camera và zoom theo chế độ người dùng chọn
        is_sat_layer = lop_nen.startswith("🛰️")

        if che_do_xem.startswith("🔎"):
            map_loc = h_info["center"]
            map_zoom = h_info["zoom_sat"]
        elif che_do_xem.startswith("🌾"):
            map_loc = h_info["center"]
            map_zoom = 10
        else:
            map_loc = [19.2, 104.9]
            map_zoom = 8

        if is_sat_layer:
            # Lớp Google Satellite Hybrid siêu nét, có nhãn địa danh tiếng Việt
            m = folium.Map(
                location=map_loc,
                zoom_start=map_zoom,
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                attr="Google Satellite Hybrid"
            )
        else:
            m = folium.Map(
                location=map_loc,
                zoom_start=map_zoom,
                tiles="OpenStreetMap"
            )

        # 2. Thêm khung bao toàn tỉnh Nghệ An
        tinh_path = "data/raw/nghe_an_tinh.geojson"
        if os.path.exists(tinh_path):
            with open(tinh_path, "r", encoding="utf-8") as tf:
                tinh_data = json.load(tf)
            folium.GeoJson(
                tinh_data,
                name="Ranh giới Tỉnh Nghệ An",
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': '#ffffff' if is_sat_layer else '#2e7d32',
                    'weight': 2.0,
                    'dashArray': '6, 6',
                    'fillOpacity': 0.0
                },
                tooltip="Ranh giới Tỉnh Nghệ An"
            ).add_to(m)

        # 3. Vẽ ranh giới huyện: Khi xem vệ tinh, BỎ HẲN MÀU TÔ (fillOpacity=0) để nhìn xuyên thấu xuống cánh đồng
        def style_function(feature):
            ten_h = feature['properties'].get('ADM2_NAME', '')
            if ten_h == huyen:
                return {
                    'fillColor': 'transparent' if is_sat_layer else '#1b5e20',
                    'color': '#00e676' if is_sat_layer else '#0d3810',
                    'weight': 4.0 if is_sat_layer else 3.0,
                    'fillOpacity': 0.0 if is_sat_layer else 0.65
                }
            else:
                return {
                    'fillColor': 'transparent' if is_sat_layer else '#ffb74d',
                    'color': '#ffea00' if is_sat_layer else '#e65100',
                    'weight': 1.8,
                    'fillOpacity': 0.0 if is_sat_layer else 0.35
                }

        folium.GeoJson(
            geojson_data,
            name="3 Huyện Nghiên cứu",
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=['ADM2_NAME'], aliases=['Huyện:'])
        ).add_to(m)

        # 4. Gắn nhãn tên huyện to rõ trên bản đồ
        for k_h, info in THONG_TIN_MAP.items():
            is_active = (k_h == huyen)
            bg_badge = "#00c853" if is_active else "#ff6d00"
            border_badge = "2.5px solid #ffffff"
            shadow_badge = "box-shadow: 0 0 14px rgba(0, 230, 118, 1);" if is_active else "box-shadow: 0 2px 6px rgba(0,0,0,0.5);"
            folium.Marker(
                location=info["center"],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="background:{bg_badge};color:white;padding:5px 12px;border-radius:16px;
                                font-size:13px;font-weight:800;white-space:nowrap;border:{border_badge};{shadow_badge}">
                        {lay_icon(k_h)} {lay_ten(k_h)} {'★ Đang chọn' if is_active else ''}
                    </div>
                    """
                )
            ).add_to(m)

        # 5. Nếu chọn toàn huyện hoặc toàn tỉnh thì căn bounds vừa vặn
        if che_do_xem.startswith("🌾") and huyen in THONG_TIN_MAP:
            m.fit_bounds(THONG_TIN_MAP[huyen]["bounds"])
        elif che_do_xem.startswith("🌐"):
            m.fit_bounds([[18.5, 103.8], [19.8, 105.8]])

        st_folium(m, height=480, use_container_width=True)

        # 6. Thẻ hồ sơ địa lý của huyện đang chọn
        st.markdown(f"""
        <div style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:10px;padding:12px 16px;margin-top:10px;">
            <div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:4px;">
                📍 Vùng trọng điểm quan sát: Huyện {lay_ten(huyen)} ({lay_icon(huyen)} {lay_vung(huyen)})
            </div>
            <div style="font-size:13px;color:#475569;line-height:1.5;">
                • <b>Vị trí địa lý:</b> {h_info.get('vung', '')}<br>
                • <b>Nguồn nước & Thủy lợi:</b> {h_info.get('thuy_loi', '')}<br>
                • <b>Đặc thù đất đai trên ảnh vệ tinh:</b> {h_info.get('dac_diem', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Không tìm thấy file ranh giới.")

# ------------------------------------------
# TAB 3: SO SÁNH KỊCH BẢN LUÂN CANH
# ------------------------------------------
with tab_scenario:
    st.subheader("🌾 Lựa Chọn & Chấm Điểm Kịch Bản Luân Canh")
    st.caption("Kéo 3 thanh trượt dưới đây theo mục tiêu canh tác của bạn để thuật toán xếp hạng kịch bản tối ưu nhất.")

    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        w_nuoc = st.slider("💧 Ưu tiên Tiết kiệm nước", 0.0, 1.0, 0.33, step=0.05)
    with col_w2:
        w_dat = st.slider("🌱 Ưu tiên Sức khỏe đất", 0.0, 1.0, 0.33, step=0.05)
    with col_w3:
        w_kt = st.slider("💰 Ưu tiên Lợi nhuận kinh tế", 0.0, 1.0, 0.34, step=0.05)

    tong_w = w_nuoc + w_dat + w_kt
    if tong_w > 0:
        w_nuoc, w_dat, w_kt = w_nuoc / tong_w, w_dat / tong_w, w_kt / tong_w

    kịch_bản = {
        "KB 0: Độc canh (Lúa - Trống - Lúa)": {"nuoc": 35, "dat": 42, "kt": 28, "mau": "#9E9E9E"},
        "KB 1: Ưu tiên đất (Lúa - Đậu xanh - Lúa)": {"nuoc": 48, "dat": 78, "kt": 45, "mau": "#4CAF50"},
        "KB 2: Chịu hạn (Lúa - Vừng đen - Lúa)": {"nuoc": 30, "dat": 80, "kt": 52, "mau": "#2196F3"},
        "KB 3: Đa dạng kinh tế (Gia vị - Đậu đen - Ngô)": {"nuoc": 45, "dat": 68, "kt": 68, "mau": "#FF9800"}
    }

    ket_qua = []
    for ten_kb, diem in kịch_bản.items():
        tong_diem = (diem["nuoc"] * w_nuoc) + (diem["dat"] * w_dat) + (diem["kt"] * w_kt)
        ket_qua.append({"Kịch bản": ten_kb, "Điểm tổng": round(tong_diem, 1), "Màu": diem["mau"]})

    df_kq = pd.DataFrame(ket_qua).sort_values("Điểm tổng", ascending=True)
    best = df_kq.iloc[-1]

    st.success(f"**🏆 Kịch bản tối ưu nhất cho bạn là:** {best['Kịch bản']} (Điểm: **{best['Điểm tổng']}/100**)")

    fig_kb = go.Figure(go.Bar(
        x=df_kq["Điểm tổng"], y=df_kq["Kịch bản"], orientation='h',
        marker_color=df_kq["Màu"], text=df_kq["Điểm tổng"], textposition="outside"
    ))
    fig_kb.update_layout(
        template="plotly_white", height=280,
        xaxis=dict(title="Điểm tổng hợp (0 - 100)", range=[0, 105]),
        margin=dict(l=10, r=40, t=10, b=10)
    )
    st.plotly_chart(fig_kb, use_container_width=True, config={'displayModeBar': False})

# ------------------------------------------
# TAB 4: LỊCH RỦI RO 12 THÁNG & BIỂU ĐỒ
# ------------------------------------------
with tab_calendar:
    st.subheader(f"📅 Lịch Rủi Ro Khí Hậu 12 Tháng: Huyện {lay_ten(huyen)}")
    hang = ["Nắng nóng, đất khô", "Mưa lớn, xói mòn", "Mưa rất lớn, úng ngập"]
    z = [d["muc_kho_nong"].tolist(),
         (d["nhanh2_xoi_mon"].astype(int) * 2).tolist(),
         (d["nhanh3_ung_ngap"].astype(int) * 2).tolist()]

    lich = go.Figure(go.Heatmap(
        z=z, x=d["thang_so"], y=hang, zmin=0, zmax=2,
        colorscale=[[0, "#A5D6A7"], [0.5, "#FFB74D"], [1, "#E53935"]],
        showscale=False, xgap=4, ygap=4, hovertemplate="Tháng %{x}<extra></extra>"))
    lich.add_vrect(x0=thang - 0.5, x1=thang + 0.5, line_color="#1F2A1F",
                   line_width=3, fillcolor="rgba(0,0,0,0)")
    lich.update_layout(
        template="plotly_white", height=230, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
                   ticktext=[f"T{t}" for t in range(1, 13)], side="top"),
        yaxis=dict(autorange="reversed"))
    st.plotly_chart(lich, use_container_width=True, config={'displayModeBar': False})
    st.caption("🟢 An toàn · 🟠 Cần chú ý · 🔴 Rủi ro cao. Khung đen là tháng đang chọn.")

    st.markdown("#### Biểu đồ chi tiết chuỗi thời gian")
    def mau_cot(dam, nhat):
        return [dam if t == thang else nhat for t in d["thang_so"]]

    def dinh_dang(fig, tieu_de):
        fig.update_layout(
            template="plotly_white", title=tieu_de, height=290, showlegend=False,
            margin=dict(l=10, r=10, t=45, b=10),
            xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=[f"T{t}" for t in range(1, 13)]))
        return fig

    f1 = go.Figure(go.Bar(x=d["thang_so"], y=d["mua_mm"], marker_color=mau_cot("#1565C0", "#90CAF9")))
    nguong, nhan = (180, "Mưa lớn (>180 mm)") if doi_nui else (400, "Mưa rất lớn (>400 mm)")
    f1.add_hline(y=nguong, line_dash="dash", line_color="#C62828", annotation_text=nhan)
    dinh_dang(f1, "Lượng mưa mỗi tháng (GPM - mm)")

    f2 = go.Figure()
    f2.add_bar(x=d["thang_so"], y=d["nong35_tb11nam"], name="TB 11 năm", marker_color=mau_cot("#EF6C00", "#FFCC80"))
    f2.add_scatter(x=d["thang_so"], y=d["nong35_2025"], mode="markers", name="Năm 2025", marker=dict(symbol="diamond", size=9, color="#B71C1C"))
    dinh_dang(f2, "Số ngày nắng nóng ≥ 35°C (POWER)")
    f2.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15))

    f3 = go.Figure(go.Scatter(
        x=d["thang_so"], y=d["sm_rootzone"] * 100, mode="lines+markers", fill="tozeroy",
        line=dict(color="#6D4C41", width=3),
        marker=dict(size=[12 if t == thang else 6 for t in d["thang_so"]])))
    f3.update_yaxes(range=[0, d["sm_rootzone"].max() * 130])
    dinh_dang(f3, "Độ ẩm đất tầng rễ (SMAP - %)")

    k1, k2, k3 = st.columns(3)
    k1.plotly_chart(f1, use_container_width=True, config={'displayModeBar': False})
    k2.plotly_chart(f2, use_container_width=True, config={'displayModeBar': False})
    k3.plotly_chart(f3, use_container_width=True, config={'displayModeBar': False})

# ------------------------------------------
# TAB 5: SỔ TAY NHÀ NÔNG (LỜI KHUYÊN DỄ HIỂU & GÓC KỸ THUẬT)
# ------------------------------------------
with tab_guide:
    st.subheader(f"🌾 Sổ Tay Nhà Nông: Vụ Mùa Tháng {thang} ({lay_ten(huyen)})")
    st.caption("Lời khuyên hành động thực tế bằng ngôn ngữ nhà nông. Làm theo để né hạn, chống úng và tiết kiệm tiền phân bón.")

    # 1. HỘP CẢNH BÁO BẰNG NGÔN NGỮ BÌNH DÂN (DÀNH CHO BÀ CON NÔNG DÂN)
    if hien["muc_kho_nong"] >= 1:
        st.markdown("""
        <div style="background:#fff3e0;border:2px solid #ff9800;border-radius:12px;padding:14px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:800;color:#e65100;margin-bottom:6px;">🔥 TRỜI NẮNG GẮT, ĐẤT ĐANG KHÁT NƯỚC (GIÓ LÀO)</div>
            <div style="font-size:14px;color:#37474f;line-height:1.5;">
                • <b>Nếu đang cấy lúa:</b> Bác nhớ cho nước vào ruộng giữ mực nước <b>3 đến 5 phân (3-5 cm)</b> vào lúc chiều mát để làm mát chân lúa, tránh cho lúa bị cháy phấn, lem lép hạt.<br>
                • <b>Nếu kênh mương cạn đáy:</b> Đừng cố cấy lúa hè thu kẻo mất trắng! Cân nhắc chuyển sang <b>gieo Vừng đen (Mè đen)</b> — cây vừng chỉ cần 1-2 trận mưa rào là sống khỏe, tiết kiệm được một nửa tiền dầu bơm nước!
            </div>
        </div>
        """, unsafe_allow_html=True)

    if hien["nhanh2_xoi_mon"]:
        st.markdown("""
        <div style="background:#efebe9;border:2px solid #8d6e63;border-radius:12px;padding:14px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:800;color:#4e342e;margin-bottom:6px;">⛰️ MƯA LỚN TRÊN ĐẤT ĐỒI DỐC: NGUY CƠ TRÔI MÀU ĐẤT</div>
            <div style="font-size:14px;color:#37474f;line-height:1.5;">
                • <b>Bà con tuyệt đối không để đất trống đồi trọc:</b> Mưa to sẽ cuốn trôi sạch lớp đất mùn màu mỡ và phân bón xuống suối.<br>
                • <b>Khuyên dùng:</b> Trồng xen <b>Đậu xanh hoặc Đậu triều</b>. Bộ lá đậu sẽ che chở mặt đất như chiếc áo tơi, rễ cây bám chặt giữ lại 85% đất phù sa màu mỡ.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if hien["nhanh3_ung_ngap"]:
        st.markdown("""
        <div style="background:#e1f5fe;border:2px solid #0288d1;border-radius:12px;padding:14px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:800;color:#01579b;margin-bottom:6px;">🌊 NGUY CƠ MƯA TO DẦM DỀ, DỄ ÚNG THỐI RỄ</div>
            <div style="font-size:14px;color:#37474f;line-height:1.5;">
                • <b>Với ruộng hoa màu, ruộng đậu:</b> Cây đậu rất sợ úng, ngâm nước quá 1 ngày là rễ thối đen. Bà con cần vác cuốc ra <b>xẻ rãnh thoát nước sâu 20cm (1 gang tay)</b> quanh luống ngay trước khi trời đổ mưa.<br>
                • <b>Tuyệt đối không gieo hạt</b> lúc ruộng đang sũng nước kẻo thối mầm.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if hien["muc_kho_nong"] == 0 and not hien["nhanh2_xoi_mon"] and not hien["nhanh3_ung_ngap"]:
        st.markdown("""
        <div style="background:#e8f5e9;border:2px solid #4caf50;border-radius:12px;padding:14px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:800;color:#1b5e20;margin-bottom:6px;">✅ THỜI TIẾT THUẬN HÒA, MÁT MẺ</div>
            <div style="font-size:14px;color:#37474f;line-height:1.5;">
                • Đất đủ ẩm, trời không quá nắng, cũng không lo ngập úng. Rất đẹp ngày để bà con cày ải, làm cỏ và xuống giống vụ mới theo lịch của xã.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. BẢNG TÍNH LỢI ÍCH KINH TẾ RA TIỀN THẬT CHO BÀ CON
    st.markdown("#### 💰 Lợi Ích Túi Tiền Cho Nhà Nông Khi Đổi Mùa Vụ")
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:10px;margin-bottom:16px;">
        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:12px;border-radius:10px;">
            <b style="color:#2e7d32;font-size:15px;">🌱 Trồng Đậu Xanh Vụ Hè:</b><br>
            <span style="font-size:13px;color:#475569;">
            • Vừa thu hạt bán được tiền nhanh (chỉ 50 ngày).<br>
            • Rễ đậu tự nhả đạm vào lòng đất tương đương bón thêm <b>1 bao đạm Urea/ha</b>, vụ sau cấy lúa bớt được mấy trăm nghìn tiền mua phân!
            </span>
        </div>
        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:12px;border-radius:10px;">
            <b style="color:#0288d1;font-size:15px;">🌾 Trồng Vừng Đen Chịu Hạn:</b><br>
            <span style="font-size:13px;color:#475569;">
            • Cây vừng chịu hạn giỏi nhất, giảm <b>gần một nửa tiền dầu máy bơm nước</b>.<br>
            • Giá hạt mè đen trên thị trường luôn cao và dễ bán, không lo thương lái ép giá.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)



# ==========================================
# SIDEBAR THÔNG TIN DỰ ÁN
# ==========================================
with st.sidebar:
    st.markdown("### 🌾 Dự Án RotaNA")
    st.caption("Field Shift: Thích ứng Nông trại với Dữ liệu Quan sát Trái Đất NASA.")
    st.markdown("---")
    st.markdown(f"""
    **Địa bàn đang xem:** {lay_ten(huyen)}  
    **Vùng sinh thái:** {lay_vung(huyen)}  
    **Tháng:** {thang} / 2025  
    """)
    st.markdown("---")
    st.caption("Bản quyền © 2026 RotaNA Team · NASA Space Apps Challenge")
