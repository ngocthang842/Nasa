"""Trang Dữ liệu & Giám sát Viễn thám Vệ tinh NASA — Huyện Yên Thành."""
import pandas as pd
import streamlit as st

import engine as E
from views.chung import tieu_de
from views.ve_tinh import hien_ve_tinh

LOP_NASA = [
    "🌾 Khuyến nghị Mùa vụ",
    "🌿 Sức khỏe Lúa (NDVI)",
    "💧 Độ ẩm Ruộng (SMAP)",
    "🌧️ Lượng mưa (GPM)",
    "🌡️ Nhiệt & Gió Lào",
]


def hien(ctx):
    dl, years = ctx["dl"], ctx["years"]
    nam = ctx["nam"]
    vung = "Yên Thành"
    thang = ctx.get("thang", 4)
    tieu_de(vung, thang, nam, "Phòng Giám sát Viễn thám & Dữ liệu Vệ tinh NASA", len(years) < 2)

    tab_gis, tab_table = st.tabs([
        "🛰️ Phòng Giám sát Viễn thám Toàn màn hình (Full-Width GIS)",
        "📁 Kho Dữ liệu & Chuỗi Thời gian (CSV)"
    ])

    with tab_gis:
        with st.container(border=True):
            st.markdown(
                '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                '  <div>'
                '    <div style="font-size:15px; font-weight:800; color:#0F172A;">🛰️ Bản đồ Viễn thám Vệ tinh Toàn màn hình Huyện Yên Thành</div>'
                '    <div style="font-size:11.5px; color:#64748B;">Giám sát ảnh vệ tinh độ phân giải cao, phủ dữ liệu MODIS, SMAP, GPM trên toàn bộ 26.500 ha ruộng lúa</div>'
                '  </div>'
                '</div>',
                unsafe_allow_html=True,
            )

            # Chọn lớp viễn thám NASA
            c_lop, c_thang = st.columns([7, 3], gap="small")
            with c_lop:
                lop_chon = st.segmented_control(
                    "Lớp viễn thám:",
                    options=LOP_NASA,
                    default=LOP_NASA[1],
                    key="seg_lop_nasa_fullwidth",
                ) if hasattr(st, "segmented_control") else st.radio("Lớp viễn thám:", LOP_NASA, horizontal=True, key="rad_lop_nasa_fullwidth")
            with c_thang:
                thang_chon = st.selectbox(
                    "Tháng khảo sát:",
                    range(1, 13),
                    index=thang - 1,
                    key="sel_thang_nasa_fullwidth",
                    format_func=lambda m: f"Tháng {m}",
                )

            # Tạo context riêng cho bản đồ viễn thám toàn màn hình
            ctx_gis = dict(ctx)
            ctx_gis["thang"] = thang_chon
            ctx_gis["lop_hien_tai"] = lop_chon or LOP_NASA[1]

            # Hiển thị bản đồ vệ tinh độ phân giải cao
            hien_ve_tinh(ctx_gis)

    with tab_table:
        dl_yt = dl[dl.huyen == vung] if not dl.empty else dl
        if len(dl_yt):
            with st.container(border=True):
                st.markdown('<p class="cap">Dữ liệu Chuỗi thời gian Vựa lúa Yên Thành</p>', unsafe_allow_html=True)
                show = pd.DataFrame({"Vùng": dl_yt.huyen, "Năm": dl_yt.year, "Tháng": dl_yt.month})
                for cot, ten, nhan in (
                    ("tmax", "Tmax (°C)", 1),
                    ("mua_mm", "Lượng mưa (mm)", 1),
                    ("nong35", "Ngày ≥35°C (Gió Lào)", 1),
                    ("sm_rootzone", "Độ ẩm đất rễ (%)", 100),
                    ("ndvi", "Độ xanh NDVI", 1),
                    ("nuoc_con_lai_mm", "Cán cân nước (mm)", 1),
                ):
                    if cot in dl_yt.columns:
                        show[ten] = (dl_yt[cot] * nhan).round(2 if cot in ("ndvi", "sm_rootzone") else 1)
                try:
                    st.dataframe(show.sort_values(["Năm", "Tháng"], ascending=[False, True]), hide_index=True, width="stretch")
                except TypeError:
                    st.dataframe(show.sort_values(["Năm", "Tháng"], ascending=[False, True]), hide_index=True, use_container_width=True)

        with st.container(border=True):
            st.markdown('<p class="cap">Kho dữ liệu vệ tinh & khí hậu đã xử lý</p>', unsafe_allow_html=True)
            fs = sorted(E.PROC.glob("*.csv"))
            if not fs:
                st.warning("Chưa có file CSV trong data/processed.")
            else:
                try:
                    st.dataframe(pd.DataFrame([
                        dict(file=p.name, KB=round(p.stat().st_size / 1024, 1)) for p in fs
                    ]), hide_index=True, width="stretch")
                except TypeError:
                    st.dataframe(pd.DataFrame([
                        dict(file=p.name, KB=round(p.stat().st_size / 1024, 1)) for p in fs
                    ]), hide_index=True, use_container_width=True)
