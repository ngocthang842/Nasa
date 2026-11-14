"""Bản đồ vệ tinh (Folium): phóng sát cánh đồng, toàn huyện, toàn tỉnh. Cần: pip install folium streamlit-folium"""
import json

import streamlit as st

import engine as E

try:
    import folium
    from streamlit_folium import st_folium
    CO_FOLIUM = True
except ImportError:
    CO_FOLIUM = False

# Khóa = E.khoa(tên huyện), không dấu, viết liền
THONG_TIN = {
    "concuong": {
        "ten": "Con Cuông", "icon": "⛰️", "center": [19.0450, 104.8950], "bounds": [[18.7763, 104.5290], [19.3524, 105.0494]],
        "vung": "Miền núi phía Tây, sát Vườn quốc gia Pù Mát",
        "nuoc": "Thượng lưu sông Lam và sông Giăng",
        "dat": "Độ dốc lớn, thung lũng sông uốn lượn, rừng đầu nguồn Pù Mát.",
    },
    "nghiloc": {
        "ten": "Nghi Lộc", "icon": "🌊", "center": [18.7980, 105.6200], "bounds": [[18.6880, 105.4669], [18.8978, 105.7575]],
        "vung": "Ven biển Đông và bán sơn địa",
        "nuoc": "Sông Cấm và hệ thống kênh hạ lưu",
        "dat": "Đất cát pha ven biển, cồn cát ven sông Cấm đổ ra vịnh Cửa Lò.",
    },
    "yenthanh": {
        "ten": "Yên Thành", "icon": "🌾", "center": [19.0076, 105.4475], "bounds": [[18.8766, 105.2981], [19.1659, 105.5801]],
        "vung": "Vựa lúa đồng bằng trung tâm Nghệ An",
        "nuoc": "Đại thủy nông Ba Ra Đô Lương và kênh Vách Bắc",
        "dat": "Vựa lúa lớn của Nghệ An, kênh mương thủy lợi ô bàn cờ.",
    },
}
CHE_DO = ["🔎 Phóng sát cánh đồng", "🌾 Toàn huyện", "🌐 Toàn tỉnh"]
NEN = ["🛰️ Ảnh vệ tinh", "🗺️ Bản đồ đường (OSM)"]
GEO_TINH = E.ROOT / "data" / "raw" / "nghe_an_tinh.geojson"   # không bắt buộc


def _doc(p):
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def hien_ve_tinh(ctx):
    vung = ctx["vung"]
    if not CO_FOLIUM:
        st.error("Thiếu thư viện bản đồ. Gõ trong terminal: pip install folium streamlit-folium")
        return
    geo = _doc(E.GEO_HUYEN)
    if not geo:
        st.warning("Thiếu data/raw/ranh_gioi_huyen.geojson")
        return

    a, b = st.columns([3, 2])
    che_do = a.radio("Mức phóng to", CHE_DO, horizontal=True, key="vt_zoom")
    nen = b.radio("Lớp nền", NEN, horizontal=True, key="vt_nen")
    ve_tinh = nen == NEN[0]

    k_chon = E.khoa(vung)
    info = THONG_TIN.get(k_chon) or THONG_TIN["yenthanh"]

    if che_do == CHE_DO[0]:
        tam, zoom = info["center"], 13
    elif che_do == CHE_DO[1]:
        tam, zoom = info["center"], 10
    else:
        tam, zoom = [19.2, 104.9], 8

    if ve_tinh:
        m = folium.Map(location=tam, zoom_start=zoom, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                       attr="Google Satellite Hybrid")
    else:
        m = folium.Map(location=tam, zoom_start=zoom, tiles="OpenStreetMap")

    tinh = _doc(GEO_TINH)
    if tinh:
        folium.GeoJson(tinh, name="Tỉnh Nghệ An", tooltip="Ranh giới tỉnh Nghệ An", style_function=lambda x: {
            "fillColor": "transparent", "color": "#FFFFFF" if ve_tinh else "#2E7D32",
            "weight": 2, "dashArray": "6, 6", "fillOpacity": 0}).add_to(m)

    def kieu(ft):
        chon = E.khoa(ft["properties"].get("ADM2_NAME", "")) == k_chon
        if chon:
            return {"fillColor": "transparent" if ve_tinh else "#0C6B52", "color": "#00E676" if ve_tinh else "#0B3C5D",
                    "weight": 4 if ve_tinh else 3, "fillOpacity": 0 if ve_tinh else .6}
        return {"fillColor": "transparent" if ve_tinh else "#FFB74D", "color": "#FFEA00" if ve_tinh else "#E65100",
                "weight": 1.8, "fillOpacity": 0 if ve_tinh else .3}

    folium.GeoJson(geo, name="3 huyện", style_function=kieu,
                   tooltip=folium.GeoJsonTooltip(fields=["ADM2_NAME"], aliases=["Huyện:"])).add_to(m)

    for k, t in THONG_TIN.items():
        chon = k == k_chon
        nen_the = "#0C6B52" if chon else "#E65100"
        bong = "box-shadow:0 0 14px rgba(0,230,118,1);" if chon else "box-shadow:0 2px 6px rgba(0,0,0,.5);"
        folium.Marker(t["center"], icon=folium.DivIcon(html=(
            f'<div style="background:{nen_the};color:#fff;padding:5px 12px;border-radius:16px;font-size:13px;'
            f'font-weight:700;white-space:nowrap;border:2.5px solid #fff;{bong}">'
            f'{t["icon"]} {t["ten"]}{" ★" if chon else ""}</div>'))).add_to(m)

    if che_do == CHE_DO[1]:
        m.fit_bounds(info["bounds"])
    elif che_do == CHE_DO[2]:
        m.fit_bounds([[18.5, 103.8], [19.8, 105.8]])

    st_folium(m, height=520, use_container_width=True, returned_objects=[], key=f"vt_{k_chon}_{che_do}_{nen}")
    st.markdown(
        f'<div style="background:#F7FBFA;border:1px solid #D7E4EF;border-radius:12px;padding:12px 16px;margin-top:8px;color:#14213D">'
        f'<b>{info["icon"]} {info["ten"]}</b> · {E.VUNG.get(vung, "")}<br>'
        f'<span style="font-size:13px;color:#33445C">• Vị trí: {info["vung"]}<br>• Nguồn nước: {info["nuoc"]}<br>• Đặc điểm: {info["dat"]}</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Ảnh vệ tinh lấy từ Google, cần có mạng. Kéo để di chuyển, cuộn chuột để phóng.")