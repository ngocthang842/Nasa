"""Trang dữ liệu đang dùng."""
import pandas as pd
import streamlit as st

import engine as E
from views.chung import tieu_de


def hien(ctx):
    dl, years = ctx["dl"], ctx["years"]
    tieu_de(ctx["vung"], ctx["thang"], ctx["nam"], "Dữ liệu", len(years) < 2)
    if len(dl):
        with st.container(border=True):
            st.markdown('<p class="cap">Số tháng đang dùng</p>', unsafe_allow_html=True)
            show = pd.DataFrame({"Vùng": dl.huyen, "Năm": dl.year, "Tháng": dl.month})
            for cot, ten, nhan in (
                ("tmax", "Tmax", 1), ("mua_mm", "Mưa", 1), ("nong35", "Ngày nóng", 1),
                ("sm_rootzone", "Ẩm đất", 100), ("ndvi", "NDVI", 1),
                ("nuoc_con_lai_mm", "Nước còn", 1),
            ):
                if cot in dl.columns:
                    show[ten] = (dl[cot] * nhan).round(2 if cot in ("ndvi", "sm_rootzone") else 0)
            st.dataframe(show, hide_index=True, use_container_width=True)
    with st.container(border=True):
        st.markdown('<p class="cap">File CSV</p>', unsafe_allow_html=True)
        fs = sorted(E.PROC.glob("*.csv"))
        if not fs:
            st.warning("Chưa có file CSV trong data/processed.")
        else:
            st.dataframe(pd.DataFrame([
                dict(file=p.name, KB=round(p.stat().st_size / 1024, 1)) for p in fs
            ]), hide_index=True, use_container_width=True)