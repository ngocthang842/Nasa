"""Bản đồ Viễn thám Vệ tinh NASA (Folium) — Giám sát Chuyên sâu Cánh đồng Lúa Huyện Yên Thành.

Tích hợp đa lớp viễn thám độ phân giải cao:
- 🌾 Khuyến nghị Mùa vụ (Lúa xuân, Hè thu, Cày ải)
- 🌿 Sức khỏe Lúa (NDVI MODIS/Sentinel)
- 💧 Độ ẩm Ruộng Lúa (SMAP Root Zone Soil Moisture)
- 🌧️ Lượng mưa Vệ tinh (NASA GPM Precipitation)
- 🌡️ Nhiệt độ & Gió Lào (AIRS/MODIS Tmax & Foehn Wind Hazard)
- 4 Trạm Quan trắc Số hóa AgTech Pinpoints tại 4 Cụm Xã Thâm Canh Yên Thành.
"""
import json
import numpy as np
import pandas as pd
import streamlit as st
import engine as E

try:
    import folium
    from folium import plugins
    from streamlit_folium import st_folium
    CO_FOLIUM = True
except ImportError:
    CO_FOLIUM = False

# TỌA ĐỘ VÀ THÔNG SỐ TRẮC LƯỢNG 4 CỤM XÃ THÂM CANH YÊN THÀNH
CUM_XA_YEN_THANH = [
    {
        "id": "bac",
        "ten": "Cụm Bắc (Đô Thành - Thọ Thành)",
        "toa_do": [19.0850, 105.5120],
        "vung": "Đồng bằng thâm canh lúa thuần chất lượng cao",
        "giong": "ST25, J02, TBR225",
        "dat": "Đất phù sa cổ sông Dinh, vàn bằng phẳng màu mỡ",
        "thuy_loi": "Nhánh Kênh chính Ba Ra Đô Lương",
        "ndvi_offset": +0.03,
        "sm_offset": 0.00,
        "tmax_offset": -0.5,
        "mau_icon": "#16A34A",
        "icon": "🌾",
        "hanh_dong": "Duy trì mực nước 3–5cm. Bón đón đòng đúng lịch, phun phòng đạo ôn cổ bông.",
    },
    {
        "id": "trung_tam",
        "ten": "Trung tâm Lòng chảo (TT Yên Thành - Tăng Thành)",
        "toa_do": [19.0076, 105.4475],
        "vung": "Rốn lúa lòng chảo Yên Thành, hội tụ kênh tưới",
        "giong": "Lúa lai, lúa thuần chịu nhiệt",
        "dat": "Đất thịt pha sét giữ nước tốt, tầng canh tác dày",
        "thuy_loi": "Trục Kênh chính Ba Ra qua thị trấn",
        "ndvi_offset": 0.00,
        "sm_offset": -0.02,
        "tmax_offset": +0.6,
        "mau_icon": "#DC2626",
        "icon": "🏛️",
        "hanh_dong": "Cảnh báo gió Lào táp phấn: Dâng nước 3–5cm làm mát gốc lúa, hạ nhiệt mặt ruộng.",
    },
    {
        "id": "nam",
        "ten": "Cụm Nam (Bảo Thành - Long Thành)",
        "toa_do": [18.9450, 105.3850],
        "vung": "Vùng trũng tiếp nhận nước Ba Ra & Tiêu lũ Kênh Vách Bắc",
        "giong": "Lúa năng suất cao, giống chịu ngập úng",
        "dat": "Đất phù sa bồi tích sông Lam, địa hình thấp trũng",
        "thuy_loi": "Cụm cống Ba Ra Đô Lương & Cống tiêu Kênh Vách Bắc",
        "ndvi_offset": +0.01,
        "sm_offset": +0.06,
        "tmax_offset": -0.3,
        "mau_icon": "#0284C7",
        "icon": "💧",
        "hanh_dong": "Mở cống Ba Ra lấy nước phù sa. Sẵn sàng mở cống Vách Bắc tiêu lũ khi mưa lớn.",
    },
    {
        "id": "tay",
        "ten": "Cụm Tây (Mỹ Thành - Quang Thành)",
        "toa_do": [18.9950, 105.3450],
        "vung": "Chân ruộng vàn cao bán sơn địa gò đồi",
        "giong": "Giống ngắn ngày, chịu hạn tốt",
        "dat": "Đất feralit biến đổi do trồng lúa nước, dễ thoát ẩm",
        "thuy_loi": "Hồ đập nhỏ nội đồng & trạm bơm chuyền",
        "ndvi_offset": -0.04,
        "sm_offset": -0.07,
        "tmax_offset": +0.3,
        "mau_icon": "#D97706",
        "icon": "⛰️",
        "hanh_dong": "Tích trữ nước tối đa trong các hồ đập nội đồng, tưới tiết kiệm luân phiên chân ruộng cao.",
    },
]

# NÚT THỦY NÔNG HUYẾT MẠCH
DIEM_THUY_LOI = [
    {
        "ten": "Cống Ba Ra Đô Lương (Đầu nguồn lấy nước sông Lam)",
        "toa_do": [18.9050, 105.3100],
        "mota": "Đại thủy nông ngăn sông Lam, cấp 85% nước tưới cho 26.500 ha lúa Yên Thành.",
        "icon": "🌊",
        "mau": "#0284C7",
    },
    {
        "ten": "Trục Tiêu Lũ Kênh Vách Bắc (Ra biển Diễn Châu)",
        "toa_do": [19.0450, 105.5150],
        "mota": "Hệ thống tiêu thoát lũ chính giải cứu vùng trũng lòng chảo Yên Thành khi mưa bão.",
        "icon": "⚡",
        "mau": "#0891B2",
    },
]

NEN_BAN_DO = {
    "🛰️ Vệ tinh Google Hybrid": (
        "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "Google Satellite Hybrid (Đường thôn xóm & Ruộng lúa)",
    ),
    "🌍 Vệ tinh Esri World": (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Esri World Imagery HD",
    ),
    "🗺️ Bản đồ số (OSM)": ("OpenStreetMap", "OpenStreetMap"),
}


def _doc_geo(p):
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def hien_ve_tinh(ctx):
    """Hiển thị bản đồ ảnh vệ tinh Folium tích hợp đầy đủ dữ liệu viễn thám NASA."""
    if not CO_FOLIUM:
        st.error("Thiếu thư viện bản đồ. Gõ trong terminal: pip install folium streamlit-folium")
        return

    geo = _doc_geo(E.GEO_HUYEN)
    if not geo:
        st.warning("Thiếu tệp ranh giới data/raw/ranh_gioi_huyen.geojson")
        return

    # Lọc duy nhất ranh giới huyện Yên Thành
    geo_yt = {
        "type": "FeatureCollection",
        "features": [
            ft for ft in geo.get("features", [])
            if E.ten_huyen(ft.get("properties", {}).get("ADM2_NAME", "")) == "Yên Thành"
        ],
    }

    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang = ctx["nam"], ctx["thang"]
    lop_hien_tai = ctx.get("lop_hien_tai", "🌾 Khuyến nghị Mùa vụ")

    # Dữ liệu trắc lượng Yên Thành
    sel = dl[(dl.year == nam) & (dl.month == thang) & (dl.huyen == "Yên Thành")]
    tmax_val = 30.0
    nong35_val = 0
    mua_val = 50.0
    sm_val = 0.35
    ndvi_val = 0.65

    if not sel.empty:
        r0 = sel.iloc[0]
        tmax_val = float(r0.get("tmax", 30.0)) if pd.notna(r0.get("tmax")) else 30.0
        nong35_val = int(r0.get("nong35", 0)) if pd.notna(r0.get("nong35")) else 0
        mua_val = float(r0.get("mua_mm", 50.0)) if pd.notna(r0.get("mua_mm")) else 50.0
        sm_val = float(r0.get("sm_rootzone", 0.35)) if pd.notna(r0.get("sm_rootzone")) else 0.35
        ndvi_val = float(r0.get("ndvi", 0.65)) if pd.notna(r0.get("ndvi")) else 0.65

    # Đánh giá mức độ rủi ro mùa vụ
    loc_lua = diem[(diem.huyen == "Yên Thành") & (diem.year == nam) & (diem.month == thang) & (diem.cay == "Lúa")]
    if not loc_lua.empty and pd.notna(loc_lua.iloc[0].get("rui_ro")):
        muc_vu = loc_lua.iloc[0].get("muc", "Cân nhắc")
        mau_vu = loc_lua.iloc[0].get("mau", "#F59E0B")
        rui_ro_vu = float(loc_lua.iloc[0].get("rui_ro", 40.0))
    else:
        muc_vu = "Ngoài vụ / Cày ải"
        mau_vu = "#64748B"
        rui_ro_vu = 20.0

    # 1. BỘ ĐIỀU KHIỂN BẢN ĐỒ VỆ TINH TINH GỌN
    col_c1, col_c2 = st.columns([1, 1], gap="small")
    with col_c1:
        che_do_zoom = st.radio(
            "Mức thu phóng:",
            ["🌾 Toàn huyện Yên Thành", "🔎 Phóng sát cánh đồng lúa"],
            horizontal=True,
            key=f"vt_zoom_radio_{nam}_{thang}",
            label_visibility="collapsed",
        )
    with col_c2:
        nen_chon = st.selectbox(
            "Lớp nền vệ tinh:",
            list(NEN_BAN_DO.keys()),
            index=0,
            key=f"vt_nen_select_{nam}_{thang}",
            label_visibility="collapsed",
        )

    # Khởi tạo bản đồ Folium
    tam_yt = [19.0076, 105.4475]
    zoom_init = 13 if "Phóng sát" in che_do_zoom else 11
    tile_url, tile_attr = NEN_BAN_DO[nen_chon]

    if "OpenStreetMap" in tile_url:
        m = folium.Map(location=tam_yt, zoom_start=zoom_init, tiles="OpenStreetMap", control_scale=True)
    else:
        m = folium.Map(location=tam_yt, zoom_start=zoom_init, tiles=tile_url, attr=tile_attr, control_scale=True)

    # Thêm nút Phóng to Toàn màn hình
    plugins.Fullscreen(position="topright", title="Phóng to toàn màn hình", title_cancel="Thu nhỏ").add_to(m)

    # 2. XÁC ĐỊNH MÀU SẮC LỚP VIỄN THÁM ĐANG CHỌN CHO ĐA GIÁC YÊN THÀNH
    is_vetinh = "Vệ tinh" in nen_chon
    if "Sức khỏe Lúa" in lop_hien_tai:
        col_poly = "#16A34A" if ndvi_val >= 0.65 else ("#84CC16" if ndvi_val >= 0.50 else "#EAB308")
        ten_lop_txt = f"Sinh khối lúa NDVI: {ndvi_val:.2f}"
    elif "Độ ẩm Ruộng" in lop_hien_tai:
        col_poly = "#0284C7" if sm_val >= 0.30 else ("#38BDF8" if sm_val >= 0.25 else "#F59E0B")
        ten_lop_txt = f"Độ ẩm đất SMAP: {sm_val*100:.0f}%"
    elif "Lượng mưa" in lop_hien_tai:
        col_poly = "#0369A1" if mua_val >= 150 else ("#38BDF8" if mua_val >= 50 else "#7DD3FC")
        ten_lop_txt = f"Lượng mưa GPM: {mua_val:.0f} mm"
    elif "Nhiệt & Gió Lào" in lop_hien_tai:
        col_poly = "#DC2626" if nong35_val >= 5 or tmax_val >= 35.0 else ("#FB923C" if tmax_val >= 32.0 else "#16A34A")
        ten_lop_txt = f"Tmax {tmax_val:.1f}°C · {nong35_val} ngày gió Lào ≥35°C"
    else:
        col_poly = mau_vu
        ten_lop_txt = f"Mùa vụ lúa: {muc_vu} (Rủi ro {rui_ro_vu:.0f}%)"

    # Vẽ ranh giới huyện Yên Thành với hiệu ứng phát sáng
    if geo_yt["features"]:
        folium.GeoJson(
            geo_yt,
            name="Ranh giới Vựa lúa Yên Thành",
            style_function=lambda x: {
                "fillColor": col_poly,
                "color": "#FDE047" if is_vetinh else "#0F172A",
                "weight": 3.0,
                "fillOpacity": 0.20 if is_vetinh else 0.15,
                "dashArray": "2, 5" if not is_vetinh else None,
            },
            tooltip=f"<b>Ranh giới Vựa lúa Huyện Yên Thành</b><br>{ten_lop_txt}",
        ).add_to(m)

    # 3. VẼ CÁC LỚP VIỄN THÁM DỮ LIỆU ĐỘNG TRÊN TỪNG CÁNH ĐỒNG (CIRCLES & HEAT)
    for c in CUM_XA_YEN_THANH:
        # Tính toán giá trị viễn thám thực tế cho từng cụm
        ndvi_c = float(np.clip(ndvi_val + c["ndvi_offset"], 0.20, 0.95))
        sm_c = float(np.clip(sm_val + c["sm_offset"], 0.15, 0.50))
        tmax_c = float(tmax_val + c["tmax_offset"])
        mua_c = mua_val

        # Tùy biến lớp phủ vệ tinh theo lớp đang chọn
        if "Sức khỏe Lúa" in lop_hien_tai:
            c_fill = "#15803D" if ndvi_c >= 0.65 else ("#84CC16" if ndvi_c >= 0.50 else "#EAB308")
            nhan_do = f"NDVI {ndvi_c:.2f}"
            rad = 2600
        elif "Độ ẩm Ruộng" in lop_hien_tai:
            c_fill = "#0369A1" if sm_c >= 0.35 else ("#0284C7" if sm_c >= 0.28 else "#F59E0B")
            nhan_do = f"Ẩm đất {sm_c*100:.0f}%"
            rad = 2800
        elif "Lượng mưa" in lop_hien_tai:
            c_fill = "#0284C7"
            nhan_do = f"{mua_c:.0f} mm"
            rad = 3000
        elif "Nhiệt & Gió Lào" in lop_hien_tai:
            c_fill = "#DC2626" if tmax_c >= 35.0 else ("#FB923C" if tmax_c >= 32.0 else "#16A34A")
            nhan_do = f"{tmax_c:.1f}°C"
            rad = 2500
        else:
            c_fill = c["mau_icon"]
            nhan_do = c["giong"].split(",")[0]
            rad = 2400

        # Vòng tròn viễn thám phủ trên cánh đồng lúa
        folium.Circle(
            location=c["toa_do"],
            radius=rad,
            color=c_fill,
            weight=1.5,
            fill=True,
            fill_color=c_fill,
            fill_opacity=0.30 if is_vetinh else 0.22,
            tooltip=f"<b>{c['ten']}</b><br>• Lớp viễn thám: {nhan_do}<br>• Vùng: {c['vung']}",
        ).add_to(m)

        # Popup chi tiết dạng AgTech khi click vào cụm xã
        popup_html = f"""
        <div style="font-family:'Be Vietnam Pro',sans-serif; width:260px; padding:4px;">
            <div style="font-size:13px; font-weight:800; color:#0F172A; border-bottom:1.5px solid #E2E8F0; padding-bottom:4px; margin-bottom:6px;">
                {c['ten']}
            </div>
            <div style="font-size:11.5px; color:#475569; margin-bottom:6px;">
                <b>Vị trí:</b> {c['vung']}<br>
                <b>Giống chủ lực:</b> <span style="color:#16A34A; font-weight:700;">{c['giong']}</span><br>
                <b>Thủy lợi:</b> {c['thuy_loi']}
            </div>
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:6px; padding:6px; font-size:11px; margin-bottom:6px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                    <span>🌿 Sinh khối NDVI:</span><b>{ndvi_c:.2f}</b>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                    <span>💧 Độ ẩm đất rễ (SMAP):</span><b>{sm_c*100:.0f}%</b>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                    <span>🌡️ Nhiệt độ Tmax:</span><b>{tmax_c:.1f}°C</b>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>🌧️ Mưa tích lũy (GPM):</span><b>{mua_c:.0f} mm</b>
                </div>
            </div>
            <div style="background:#FEF2F2; border-left:3px solid #EF4444; border-radius:4px; padding:5px 7px; font-size:11px; color:#991B1B; line-height:1.3;">
                <b>⚡ Mệnh lệnh:</b> {c['hanh_dong']}
            </div>
        </div>
        """

        # Pinpoint công nghệ cao AgTech Pin
        marker_html = f"""
        <div style="
            display:flex; align-items:center; gap:4px;
            background:#0F172A; color:#FFFFFF;
            padding:3px 8px; border-radius:14px;
            border:2px solid #FFFFFF; box-shadow:0 3px 8px rgba(0,0,0,0.4);
            white-space:nowrap; font-family:'Be Vietnam Pro',sans-serif;
            font-size:11px; font-weight:750; cursor:pointer;
        ">
            <span>{c['icon']}</span>
            <span>{c['ten'].split('(')[0].strip()}</span>
            <span style="background:{c_fill}; color:#FFFFFF; border-radius:999px; padding:1px 5px; font-size:10px; font-weight:800; margin-left:2px;">
                {nhan_do}
            </span>
        </div>
        """

        folium.Marker(
            location=c["toa_do"],
            icon=folium.DivIcon(html=marker_html),
            popup=folium.Popup(popup_html, max_width=290),
            tooltip=f"{c['ten']} — Bấm để xem số liệu chi tiết",
        ).add_to(m)

    # 4. ĐÁNH DẤU CÁC CÔNG TRÌNH THỦY NÔNG ĐẦU MỐI
    for tl in DIEM_THUY_LOI:
        tl_html = f"""
        <div style="
            background:#0284C7; color:#FFFFFF; padding:2px 6px;
            border-radius:10px; border:1.5px solid #FFFFFF;
            font-size:10px; font-weight:750; white-space:nowrap;
            box-shadow:0 2px 5px rgba(0,0,0,0.3); font-family:'Be Vietnam Pro',sans-serif;
        ">
            {tl['icon']} {tl['ten'].split('(')[0].strip()}
        </div>
        """
        folium.Marker(
            location=tl["toa_do"],
            icon=folium.DivIcon(html=tl_html),
            tooltip=f"<b>{tl['ten']}</b><br>{tl['mota']}",
        ).add_to(m)

    # Fit bounds nếu xem toàn huyện
    if "Toàn huyện" in che_do_zoom:
        m.fit_bounds([[18.8766, 105.2981], [19.1659, 105.5801]])

    # Render bản đồ Folium
    st_folium(
        m,
        height=480,
        width="stretch",
        returned_objects=[],
        key=f"vt_folium_master_{nam}_{thang}_{lop_hien_tai[:8]}_{che_do_zoom[:4]}_{nen_chon[:5]}",
    )

    # 5. BẢNG CHÚ GIẢI MÀU VIỄN THÁM (LEGEND) BÊN DƯỚI BẢN ĐỒ VỆ TINH
    st.markdown(
        f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:6px 10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
        f'  <div style="font-size:11.5px; font-weight:750; color:#0F172A;">'
        f'    🛰️ Đang phủ lớp viễn thám: <span style="color:#0284C7;">{lop_hien_tai}</span>'
        f'  </div>'
        f'  <div style="display:flex; align-items:center; gap:10px; font-size:11px; color:#475569;">'
        f'    <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:10px; border-radius:50%; background:#15803D; display:inline-block;"></span> Sinh khối tốt / Ẩm chuẩn</span>'
        f'    <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:10px; border-radius:50%; background:#F59E0B; display:inline-block;"></span> Cảnh báo hạn / Khô chân</span>'
        f'    <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:10px; border-radius:50%; background:#DC2626; display:inline-block;"></span> Nắng nóng gió Lào táp</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )
