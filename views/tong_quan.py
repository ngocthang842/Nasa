"""Trang Tổng quan: KPI sparkline, bản đồ, đánh giá nông dân, biểu đồ."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import engine as E
from views.ban_do import hien_ban_do
from views.chung import kpi_the, the_cay, tieu_de, ve


def hien(ctx):
    dl, diem, nam_df = ctx["dl"], ctx["diem"], ctx["nam_df"]
    nam, thang, vung, years = ctx["nam"], ctx["thang"], ctx["vung"], ctx["years"]
    chuoi = dl[(dl.year == nam) & (dl.huyen == vung)].sort_values("month")
    tieu_de(vung, thang, nam, "Tổng quan", len(years) < 2)
    st.write("")
    if chuoi.empty or thang not in set(chuoi.month):
        st.warning("Chưa có chuỗi tháng cho vùng này.")
        return

    c = st.columns(5)
    th = [
        kpi_the("Nhiệt độ cao nhất", "tmax", "°C", "#F97316", chuoi, thang, "cao", "{:.1f}"),
        kpi_the("Mưa trong tháng", "mua_mm", "mm", "#0EA5E9", chuoi, thang, "cao"),
        kpi_the(f"Ngày ≥{E.NGUONG_NONG}°C", "nong35", "ngày", "#EF4444", chuoi, thang, "cao"),
        kpi_the("Độ ẩm đất vùng rễ", "sm_rootzone", "%", "#10B981", chuoi, thang, "thap", "{:.0f}", 100),
        kpi_the("NDVI (độ xanh)", "ndvi", "", "#84CC16", chuoi, thang, "thap", "{:.2f}"),
    ]
    for col, html in zip(c, th):
        col.markdown(html, unsafe_allow_html=True)

    st.write("")
    trai, phai = st.columns([5, 3], gap="medium")
    with trai:
        hien_ban_do(ctx)
    with phai, st.container(border=True):
        st.markdown('<p class="cap">Đánh giá cho nông dân</p>', unsafe_allow_html=True)
        loc = diem[(diem.huyen == vung) & (diem.year == nam) & (diem.month == thang)] if len(diem) else diem
        the_cay(loc)

    st.write("")
    a, b, c3 = st.columns(3, gap="medium")
    with a, st.container(border=True):
        st.markdown('<p class="cap">Mưa và nhiệt độ theo tháng</p>', unsafe_allow_html=True)
        f = make_subplots(specs=[[{"secondary_y": True}]])
        f.add_bar(x=chuoi.month, y=chuoi.mua_mm, name="Mưa (mm)", marker_color="#7DD3FC")
        if "tmax" in chuoi.columns:
            f.add_scatter(
                x=chuoi.month, y=chuoi.tmax, name="Tmax (°C)", mode="lines+markers",
                line=dict(color="#F97316", width=3), secondary_y=True,
            )
        f.add_vrect(x0=thang - .5, x1=thang + .5, fillcolor="#1F6FEB", opacity=.1, line_width=0)
        f.update_xaxes(dtick=1)
        f.update_layout(
            height=280, margin=dict(l=8, r=8, t=24, b=8),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.15),
        )
        ve(f)

    with b, st.container(border=True):
        st.markdown(f'<p class="cap">Số ngày ≥{E.NGUONG_NONG}°C mỗi năm</p>', unsafe_allow_html=True)
        n = nam_df[(nam_df.huyen == vung) & (nam_df.nguong == E.NGUONG_NONG)].sort_values("nam") if len(nam_df) else nam_df
        if n is None or getattr(n, "empty", True):
            st.caption("Chưa có gio_lao_theo_nam.csv")
        else:
            g = go.Figure(go.Bar(
                x=n.nam.astype(str), y=n.so_ngay,
                marker_color=["#E11D48" if y == nam else "#FDA4AF" for y in n.nam],
            ))
            g.update_layout(
                height=280, margin=dict(l=8, r=8, t=24, b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            ve(g)

    with c3, st.container(border=True):
        st.markdown(f'<p class="cap">Rủi ro cây × tháng, năm {nam}</p>', unsafe_allow_html=True)
        z, hv = [], []
        for cay in E.CAY_VUNG.get(vung, []):
            q = diem[(diem.huyen == vung) & (diem.year == nam) & (diem.cay == cay)].set_index("month")
            z.append([q.rui_ro.get(m, np.nan) if len(q) else np.nan for m in range(1, 13)])
            hv.append([
                f"{cay}, T{m}: {q.giai_doan.get(m, 'chưa có') if len(q) else 'chưa có'}<br>{q.muc.get(m, '') if len(q) else ''}"
                for m in range(1, 13)
            ])
        if z:
            f = go.Figure(go.Heatmap(
                z=z, x=[f"T{m}" for m in range(1, 13)], y=list(E.CAY_VUNG.get(vung, [])),
                text=hv, hoverinfo="text", zmin=0, zmax=100, xgap=3, ygap=3,
                colorscale=[[0, "#34D399"], [.45, "#FBBF24"], [1, "#F43F5E"]],
                colorbar=dict(title="Rủi ro", thickness=10),
            ))
            f.update_layout(
                height=280, margin=dict(l=8, r=8, t=24, b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            ve(f)
        else:
            st.caption("Chưa có điểm rủi ro.")