"""Bản đồ Chuyên đề Giám sát Vựa lúa Huyện Yên Thành (Nghệ An) — Tương tác chuẩn GIS & Map Sidebar chuyên trách."""
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale

import engine as E
from views.ve_tinh import hien_ve_tinh

LOP = [
    "🌾 Khuyến nghị Mùa vụ",
    "🌿 Sức khỏe Lúa (NDVI)",
    "💧 Độ ẩm Ruộng (SMAP)",
    "🌧️ Lượng mưa (GPM)",
    "🌡️ Nhiệt & Gió Lào",
]

LOP_THANG = {
    "🌡️ Nhiệt & Gió Lào": ("tmax", ["#FEF08A", "#FB923C", "#DC2626"], 24, 40, "{:.1f}°C", "°C", ""),
    "🌧️ Lượng mưa (GPM)": ("mua_mm", ["#BAE6FD", "#38BDF8", "#0369A1"], 0, 700, "{:.0f} mm", "mm", ""),
    "💧 Độ ẩm Ruộng (SMAP)": ("sm_rootzone", ["#FDE68A", "#86EFAC", "#059669"], .20, .40, "{:.0%}", "", ".0%"),
    "🌿 Sức khỏe Lúa (NDVI)": ("ndvi", ["#FDE68A", "#A3E635", "#15803D"], .4, .9, "{:.2f}", "", ""),
}

# 5 TIỂU VÙNG ZOOM NHANH 1-CLICK (KHÔNG DÙNG KÉO HỘP BOX-ZOOM)
ZOOM_PRESETS = {
    "🗺️ Toàn huyện": ([105.27, 105.63], [18.85, 19.21], "Toàn cảnh ranh giới Huyện Yên Thành"),
    "🌾 Cụm Bắc (Đô Thành)": ([105.44, 105.58], [19.04, 19.16], "Vùng lúa thâm canh Đô Thành - Thọ Thành"),
    "🏛️ Trung tâm (Lòng chảo)": ([105.38, 105.52], [18.96, 19.08], "Thị trấn Yên Thành & Trục Kênh chính Ba Ra"),
    "💧 Cụm Nam (Bảo Thành)": ([105.35, 105.49], [18.88, 19.00], "Cụm cống Ba Ra sông Lam & Tiêu lũ Kênh Vách Bắc"),
    "⛰️ Cụm Tây (Mỹ Thành)": ([105.28, 105.42], [18.93, 19.05], "Chân ruộng vàn cao bán sơn địa Mỹ Thành"),
}


@st.cache_data(show_spinner=False)
def tai_geo():
    if E.GEO_HUYEN.exists():
        with open(E.GEO_HUYEN, encoding="utf-8") as f:
            return json.load(f)
    return None


def _ten_ft(ft):
    return E.ten_huyen(ft["properties"].get("ADM2_NAME", ""))


def vong(g):
    for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        yield [c[0] for c in p[0]], [c[1] for c in p[0]]


def gia_tri(lop, sel, diem, nam, thang):
    x = sel[sel.huyen == "Yên Thành"]
    if x.empty:
        return E.MAU_NGOAI_VU, "Chưa có dữ liệu", "Chưa có dữ liệu"

    if "Khuyến nghị Mùa vụ" in lop:
        dd = diem[(diem.huyen == "Yên Thành") & (diem.year == nam) & (diem.month == thang) & (diem.cay == "Lúa")]
        if dd.empty:
            return E.MAU_NGOAI_VU, "Lúa Yên Thành: Ngoài vụ hoặc đang cày ải", "Ngoài vụ"
        d = dd.iloc[0]
        if pd.isna(d.rui_ro):
            return E.MAU_NGOAI_VU, "Lúa Yên Thành: Ngoài thời vụ chính (Đang cày ải ruộng)", "Ngoài vụ"
        ngan = f"{d.muc} ({d.rui_ro:.0f}%)"
        return d.mau, f"Lúa Yên Thành: {ngan}", ngan

    c, cs, lo, hi, f, _, _ = LOP_THANG[lop]
    v = x.iloc[0][c]
    ngan = f.format(v) if pd.notna(v) else "—"
    mau = sample_colorscale(cs, [float(np.clip((v - lo) / (hi - lo), 0, 1))])[0] if pd.notna(v) else "#CBD5E1"
    return mau, f"{lop}: {ngan}", ngan


def ban_do_yen_thanh(lop, sel, diem, nam, thang, geo_huyen, zoom_chon):
    fig = go.Figure()
    ax, ay = [], []

    # 1. LỌC DUY NHẤT RẢNH GIỚI HUYỆN YÊN THÀNH
    features_yt = [
        ft for ft in (geo_huyen or {}).get("features", [])
        if _ten_ft(ft) == "Yên Thành"
    ]

    mau, txt, ngan = gia_tri(lop, sel, diem, nam, thang)

    for ft in features_yt:
        rings = list(vong(ft["geometry"]))
        for xs, ys in rings:
            ax += xs
            ay += ys
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines", fill="toself",
                fillcolor=mau, opacity=0.88,
                line=dict(color="#0F172A", width=3),
                text=f"<b>Huyện Yên Thành (Vựa lúa xứ Nghệ)</b><br>{txt}",
                hoverinfo="text", hoveron="fills", showlegend=False,
            ))

    # Thông số thực tế
    tmax_val = 30.0
    ndvi_val = 0.65
    sm_val = 0.35
    if not sel.empty:
        r0 = sel.iloc[0]
        tmax_val = r0.get("tmax", 30.0) if pd.notna(r0.get("tmax")) else 30.0
        ndvi_val = r0.get("ndvi", 0.65) if pd.notna(r0.get("ndvi")) else 0.65
        sm_val = r0.get("sm_rootzone", 0.35) if pd.notna(r0.get("sm_rootzone")) else 0.35

    gd_ngan = "Lúa xuân" if thang <= 5 else ("Lúa hè thu" if thang <= 9 else "Cày ải")
    if thang == 4:
        gd_ngan = "Trỗ bông rộ"
    elif thang == 3:
        gd_ngan = "Làm đòng"
    elif thang == 5:
        gd_ngan = "Chín & Gặt"
    elif thang == 8:
        gd_ngan = "Trỗ hè thu"

    # 2. ĐIỂM TRẠM PINPOINT SẮC NÉT (KHÔNG DÙNG HỘP CHỮ TO ĐÈ LÊN NHAU)
    cac_diem_yt = [
        ("Đô Thành", 19.0850, 105.5120, f"<b>🌾 CỤM BẮC: ĐÔ THÀNH</b><br>• Giống lúa thuần: ST25, J02<br>• Sinh khối: NDVI {ndvi_val:.2f}", "#16A34A"),
        ("TT Yên Thành", 19.0076, 105.4475, f"<b>🏛️ TRUNG TÂM: LÒNG CHẢO</b><br>• Trạng thái: {gd_ngan}<br>• Nhiệt độ: {tmax_val:.1f}°C · Kênh Ba Ra giữ 3-5cm", "#0F172A"),
        ("Bảo Thành", 18.9450, 105.3850, f"<b>💧 CỤM NAM: BẢO THÀNH</b><br>• Cống Ba Ra mở 85% lưu lượng<br>• Ẩm đất rễ: {sm_val*100:.0f}% · Tiêu Vách Bắc", "#0284C7"),
        ("Mỹ Thành", 18.9950, 105.3450, f"<b>⛰️ CỤM TÂY: MỸ THÀNH</b><br>• Chân ruộng vàn cao bán sơn địa<br>• Hồ đập nhỏ nội đồng", "#D97706"),
        ("Tăng Thành", 18.9950, 105.4700, "<b>🌱 TĂNG THÀNH</b><br>Cánh đồng mẫu lớn lúa chất lượng cao", "#0F172A"),
        ("Long Thành", 19.0350, 105.4850, "<b>🌊 LONG THÀNH</b><br>Vùng trũng tiếp giáp Kênh Vách Bắc", "#0F172A"),
    ]

    for ten, la, lo, tooltip_txt, col_pt in cac_diem_yt:
        fig.add_trace(go.Scatter(
            x=[lo], y=[la], mode="markers+text",
            text=[f"  {ten}"], textposition="middle right",
            textfont=dict(size=10.5, color="#0F172A", family="Be Vietnam Pro", weight="bold"),
            marker=dict(size=9, color=col_pt, line=dict(color="#FFFFFF", width=2)),
            hoverinfo="text", hovertext=tooltip_txt,
            showlegend=False,
        ))

    # 3. CHÚ THÍCH MÀU GỌN GÀNG DƯỚI BẢN ĐỒ
    if "Khuyến nghị Mùa vụ" in lop:
        for ten_muc, mau_muc in [(m[1], m[2]) for m in E.MUC] + [("Ngoài vụ / Cày ải", E.MAU_NGOAI_VU)]:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers", name=ten_muc, showlegend=True,
                marker=dict(size=11, color=mau_muc, symbol="square"),
            ))
        fig.update_layout(
            showlegend=True,
            legend=dict(
                x=0.01, y=0.02,
                bgcolor="rgba(255,255,255,0.92)",
                bordercolor="#E2E8F0",
                borderwidth=1,
                font=dict(color="#0F172A", size=10),
                orientation="h",
            ),
        )
    else:
        _, cs, lo, hi, _, dv, tf = LOP_THANG[lop]
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(
                color=[lo], cmin=lo, cmax=hi,
                colorscale=[[0, cs[0]], [.5, cs[1]], [1, cs[2]]], showscale=True,
                colorbar=dict(
                    title=dict(text=f"{lop} ({dv})" if dv else lop, side="right"),
                    thickness=11, len=0.55, x=0.98, y=0.5, tickformat=tf,
                    bgcolor="rgba(255,255,255,0.9)", bordercolor="#E2E8F0", borderwidth=1,
                ),
            ),
        ))

    # 4. TÍNH TOÁN ZOOM RANGE THEO TIỂU VÙNG ĐƯỢC CHỌN (KHÔNG BỊ HỘP VUÔNG)
    if zoom_chon in ZOOM_PRESETS:
        xr, yr, _ = ZOOM_PRESETS[zoom_chon]
    else:
        xr = [min(ax) - 0.035, max(ax) + 0.035] if ax else [105.27, 105.63]
        yr = [min(ay) - 0.03, max(ay) + 0.035] if ay else [18.85, 19.21]

    fig.update_xaxes(range=xr, visible=False)
    fig.update_yaxes(range=yr, visible=False, scaleanchor="x", scaleratio=1 / np.cos(np.radians(19.0)))
    
    # KÍCH HOẠT CHẾ ĐỘ KÉO DI CHUYỂN (PAN) — LOẠI BỎ HOÀN TOÀN KÉO HỘP BOX-ZOOM!
    fig.update_layout(
        height=510,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F8FAFC",
        dragmode="pan",
    )
    return fig


def hien_ban_do(ctx):
    """Khối bản đồ chuyên nghiệp (Split-View: Bản đồ sạch 66% + Map Sidebar 34%)."""
    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang = ctx["nam"], ctx["thang"]
    sel = dl[(dl.year == nam) & (dl.month == thang) & (dl.huyen == "Yên Thành")]
    geo_huyen = tai_geo()

    # Dữ liệu trắc lượng khí hậu
    tmax_val = 30.0
    nong35_val = 0
    mua_val = 50.0
    sm_val = 0.35
    ndvi_val = 0.65
    if not sel.empty:
        r0 = sel.iloc[0]
        tmax_val = r0.get("tmax", 30.0) if pd.notna(r0.get("tmax")) else 30.0
        nong35_val = int(r0.get("nong35", 0)) if pd.notna(r0.get("nong35")) else 0
        mua_val = r0.get("mua_mm", 50.0) if pd.notna(r0.get("mua_mm")) else 50.0
        sm_val = r0.get("sm_rootzone", 0.35) if pd.notna(r0.get("sm_rootzone")) else 0.35
        ndvi_val = r0.get("ndvi", 0.65) if pd.notna(r0.get("ndvi")) else 0.65

    # Khởi tạo lớp viễn thám hiện tại từ session state trước khi vẽ bản đồ
    lop_chon_hien_tai = st.session_state.get(f"radio_lop_mapsidebar_{nam}_{thang}", LOP[0])
    ctx["lop_hien_tai"] = lop_chon_hien_tai

    with st.container(border=True):
        # 1. HEADER KHỐI BẢN ĐỒ + BỘ ZOOM NHANH 1-CLICK THEO TIỂU VÙNG
        c_ttl, c_zoom = st.columns([4, 6], gap="small")
        with c_ttl:
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A;">🗺️ Bản đồ Số hóa Vựa lúa Yên Thành</div>'
                '<div style="font-size:11px; color:#64748B;">🖐️ Kéo chuột để di chuyển (Pan) · 🔄 Lăn chuột để Phóng to/Thu nhỏ</div>',
                unsafe_allow_html=True,
            )
        with c_zoom:
            zoom_chon = st.pills(
                "Zoom nhanh tiểu vùng:",
                options=list(ZOOM_PRESETS.keys()),
                default="🗺️ Toàn huyện",
                label_visibility="collapsed",
                key=f"zoom_preset_pill_{nam}_{thang}",
            )
            if not zoom_chon:
                zoom_chon = "🗺️ Toàn huyện"

        # 2. BĂNG CẢNH BÁO THỜI TIẾT NGOÀI BẢN ĐỒ (KHÔNG BAO GIỜ BỊ CẮT CHỮ)
        if nong35_val >= 5 or tmax_val >= 35.0:
            st.markdown(
                f'<div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; border-radius:8px; padding:6px 10px; font-size:12px; color:#991B1B; margin:6px 0; display:flex; align-items:center; gap:8px;">'
                f'  <span>🔥</span>'
                f'  <div><b>CẢNH BÁO:</b> Có <b>{nong35_val} ngày gió Lào ≥35°C</b> (Nguy cơ táp bông lúa) ➔ <b>Mệnh lệnh: Dâng nước 3–5 cm làm mát ruộng</b></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        elif mua_val >= 200:
            st.markdown(
                f'<div style="background:#F0F9FF; border:1px solid #BAE6FD; border-left:4px solid #0284C7; border-radius:8px; padding:6px 10px; font-size:12px; color:#075985; margin:6px 0; display:flex; align-items:center; gap:8px;">'
                f'  <span>🌊</span>'
                f'  <div><b>CẢNH BÁO:</b> Lượng mưa tích lũy <b>{mua_val:.0f} mm</b> ➔ <b>Mệnh lệnh: Mở cống Kênh Vách Bắc tiêu úng</b></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 3. SPLIT-VIEW: BẢN ĐỒ SẠCH (66%) & MAP SIDEBAR CHUYÊN TRÁCH (34%)
        col_map, col_mapsidebar = st.columns([66, 34], gap="small")

        with col_map:
            tab_vector, tab_vetinh = st.tabs([
                f"🗺️ {zoom_chon}",
                "🛰️ Ảnh Vệ tinh Thật (Folium)"
            ])
            with tab_vector:
                # CẤU HÌNH PLOTLY CHUẨN GIS: CUỘN CHUỘT ZOOM, NÚT [+] [-] TRÊN GÓC, KHÔNG CÓ BOX-ZOOM
                cfg = {
                    "scrollZoom": True,
                    "displayModeBar": True,
                    "modeBarButtonsToAdd": ["zoomIn2d", "zoomOut2d", "resetScale2d", "pan2d"],
                    "modeBarButtonsToRemove": ["select2d", "lasso2d", "zoom2d", "autoScale2d", "toImage"],
                    "displaylogo": False,
                    "responsive": True,
                }
                fig_map = ban_do_yen_thanh(ctx.get("lop_hien_tai", LOP[0]), sel, diem, nam, thang, geo_huyen, zoom_chon)
                try:
                    st.plotly_chart(fig_map, width="stretch", config=cfg)
                except TypeError:
                    st.plotly_chart(fig_map, use_container_width=True, config=cfg)

            with tab_vetinh:
                hien_ve_tinh(ctx)

        # 4. MAP SIDEBAR CHUYÊN TRÁCH: BỘ CHỌN LỚP DỌC & TELEMETRY 4 CỤM XÃ
        with col_mapsidebar:
            st.markdown(
                '<div style="font-size:12px; font-weight:750; color:#0F172A; margin-bottom:4px;">'
                '🎛️ Lớp Viễn thám & Đo đạc:'
                '</div>',
                unsafe_allow_html=True,
            )

            # Chọn lớp hiển thị dạng dọc (không bị rớt 2 hàng)
            lop_chon = st.radio(
                "Chọn lớp:",
                LOP,
                index=0,
                key=f"radio_lop_mapsidebar_{nam}_{thang}",
                label_visibility="collapsed",
            )
            ctx["lop_hien_tai"] = lop_chon
            _, _, ngan_lop = gia_tri(lop_chon, sel, diem, nam, thang)

            # Giá trị đo đạc của lớp đang chọn
            st.markdown(
                f'<div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:5px 8px; font-size:11.5px; margin-bottom:8px;">'
                f'📊 <b>{lop_chon}:</b> <b style="color:#0F172A;">{ngan_lop}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # BẢNG TELEMETRY 4 CỤM XÃ SỐ HÓA (XẾP DỌC NGĂN NẮP, KHÔNG ĐÈ LÊN BẢN ĐỒ)
            st.markdown(
                '<div style="font-size:12px; font-weight:750; color:#0F172A; margin:6px 0 4px 0;">'
                '📍 Telemetry 4 Cụm Xã Số Hóa:'
                '</div>',
                unsafe_allow_html=True,
            )

            # 4 Thẻ cụm xã gọn gàng
            gd_cluster = "Trỗ bông rộ" if thang == 4 else ("Làm đòng" if thang == 3 else ("Gặt rộ" if thang == 5 else "Phát triển"))
            thong_tin_cum = [
                ("🌾 Cụm Bắc (Đô Thành)", f"ST25, J02 · NDVI {ndvi_val:.2f}", "#16A34A", "#F0FDF4"),
                ("🏛️ Trung tâm (Lòng chảo)", f"{gd_cluster} · {tmax_val:.1f}°C · Nước 3–5cm", "#0F172A", "#F8FAFC"),
                ("💧 Cụm Nam (Bảo Thành)", f"Cống Ba Ra 85% · Ẩm đất {sm_val*100:.0f}%", "#0284C7", "#F0F9FF"),
                ("⛰️ Cụm Tây (Mỹ Thành)", "Ruộng vàn cao · Giữ ẩm hồ đập", "#D97706", "#FFFBEB"),
            ]

            for ten_c, mota_c, mau_c, bg_c in thong_tin_cum:
                st.markdown(
                    f'<div style="background:{bg_c}; border:1px solid #E2E8F0; border-left:3.5px solid {mau_c}; border-radius:6px; padding:5px 8px; margin-bottom:4px;">'
                    f'<div style="font-size:11px; font-weight:800; color:{mau_c};">{ten_c}</div>'
                    f'<div style="font-size:10.5px; color:#334155; line-height:1.3; margin-top:1px;">{mota_c}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
