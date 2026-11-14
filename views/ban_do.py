"""Bản đồ Plotly — giữ logic thiết kế bản đầu."""
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale

import engine as E
from views.chung import ve
from views.ve_tinh import hien_ve_tinh

LOP = list(E.CAY) + ["Nhiệt độ", "Mưa", "Độ ẩm đất", "NDVI"]
LOP_THANG = {
    "Nhiệt độ": ("tmax", ["#FEF08A", "#FB923C", "#DC2626"], 24, 40, "{:.1f}°C", "°C", ""),
    "Mưa": ("mua_mm", ["#BAE6FD", "#38BDF8", "#0369A1"], 0, 700, "{:.0f} mm", "mm", ""),
    "Độ ẩm đất": ("sm_rootzone", ["#FDE68A", "#86EFAC", "#059669"], .22, .45, "{:.0%}", "", ".0%"),
    "NDVI": ("ndvi", ["#FDE68A", "#A3E635", "#15803D"], .4, .9, "{:.2f}", "", ""),
}
MO_TA = {
    "Lúa": "Màu = mức khuyến nghị trồng lúa: xanh Nên trồng, vàng Cân nhắc, đỏ Hạn chế, xám ngoài vụ.",
    "Ngô": "Màu = mức khuyến nghị trồng ngô tháng này.",
    "Cam": "Màu = mức khuyến nghị trồng cam tháng này.",
    "Chè": "Màu = mức khuyến nghị hái/chăm chè tháng này.",
    "Sắn": "Màu = mức khuyến nghị trồng sắn tháng này.",
    "Lạc": "Màu = mức khuyến nghị trồng lạc tháng này.",
    "Ngô nếp": "Màu = mức khuyến nghị trồng ngô nếp tháng này.",
    "Nhiệt độ": "Vàng mát → cam/đỏ nóng.",
    "Mưa": "Xanh nhạt mưa ít → xanh đậm mưa nhiều.",
    "Độ ẩm đất": "Vàng khô → xanh ẩm.",
    "NDVI": "Vàng thưa → xanh đậm cây tốt.",
}

DAO = {
    "Hoàng Sa": ([16.83, 16.53, 15.78, 16.67], [112.33, 111.60, 111.20, 112.73], (17.6, 112.0), "Quần đảo Hoàng Sa (Đà Nẵng)"),
    "Trường Sa": ([11.43, 10.18, 9.88, 8.65, 7.88], [114.33, 114.37, 114.33, 111.92, 112.92], (12.4, 114.6), "Quần đảo Trường Sa (Khánh Hòa)"),
}
TP = {"Hà Nội": (21.03, 105.85), "Vinh": (18.68, 105.68), "Huế": (16.46, 107.59), "Đà Nẵng": (16.05, 108.2), "TP.HCM": (10.78, 106.7)}


@st.cache_data(show_spinner=False)
def tai_geo():
    def ld(p):
        return json.load(open(p, encoding="utf-8")) if p.exists() else None
    return ld(E.GEO_HUYEN), ld(E.GEO_VN)


def _ten_ft(ft):
    return E.ten_huyen(ft["properties"].get("ADM2_NAME", ""))


def vong(g):
    for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        yield [c[0] for c in p[0]], [c[1] for c in p[0]]


def gia_tri(h, lop, sel, diem, nam, thang):
    x = sel[sel.huyen == h]
    if x.empty:
        return E.MAU_NGOAI_VU, "Chưa có dữ liệu", "Chưa có dữ liệu"
    if lop in E.CAY:
        dd = diem[(diem.huyen == h) & (diem.year == nam) & (diem.month == thang) & (diem.cay == lop)]
        if dd.empty:
            return E.MAU_NGOAI_VU, f"{lop}: không phải cây đặc trưng của vùng", "không phải cây đặc trưng"
        d = dd.iloc[0]
        ngan = "ngoài vụ" if np.isnan(d.rui_ro) else f"{d.muc} ({d.rui_ro:.0f}/100)"
        return d.mau, f"{lop}: {ngan}", ngan
    c, cs, lo, hi, f, _, _ = LOP_THANG[lop]
    v = x.iloc[0][c]
    ngan = f.format(v)
    return sample_colorscale(cs, [float(np.clip((v - lo) / (hi - lo), 0, 1))])[0], f"{lop}: {ngan}", ngan


def ban_do(lop, che_do, sel, diem, nam, thang, vung, geo_huyen, geo_vn):
    fig = go.Figure()
    for ft in (geo_vn or {"features": []})["features"]:
        for xs, ys in vong(ft["geometry"]):
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines", fill="toself", fillcolor="#EEF6E6",
                line=dict(color="#7FB08F", width=1), hoverinfo="skip", showlegend=False,
            ))
    if che_do == "vn":
        for la, lo, (tl, tn), nhan in DAO.values():
            fig.add_trace(go.Scatter(
                x=lo, y=la, mode="markers", marker=dict(size=5, color="#1E6FA8"),
                hovertext=nhan, hoverinfo="text", showlegend=False,
            ))
            fig.add_annotation(x=tn, y=tl, text=nhan, showarrow=False, font=dict(size=11, color="#1E5A86"))
        for t, (la, lo) in TP.items():
            fig.add_trace(go.Scatter(
                x=[lo], y=[la], mode="markers+text", text=[t], textposition="middle right",
                textfont=dict(size=10, color="#35566E"), marker=dict(size=4, color="#35566E"),
                hoverinfo="skip", showlegend=False,
            ))
        fig.add_annotation(x=112.5, y=13.6, text="B I Ể N   Đ Ô N G", showarrow=False, font=dict(size=14, color="#6FA6C8"))

    ax, ay = [], []
    for ft in (geo_huyen or {"features": []})["features"]:
        h = _ten_ft(ft)
        mau, txt, ngan = gia_tri(h, lop, sel, diem, nam, thang)
        chon = h == vung
        rings = list(vong(ft["geometry"]))
        for xs, ys in rings:
            ax += xs
            ay += ys
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines", fill="toself", fillcolor=mau, opacity=.95,
                line=dict(color="#0B3C5D" if chon else "#FFFFFF", width=2.8 if chon else 1.2),
                text=f"<b>{h}</b><br>{txt}", hoverinfo="text", hoveron="fills", showlegend=False,
            ))
        if not rings:
            continue
        xs, ys = max(rings, key=lambda r: len(r[0]))
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        if che_do == "vn":
            fig.add_trace(go.Scatter(
                x=[cx], y=[cy], mode="markers", hoverinfo="skip", showlegend=False,
                marker=dict(size=36 if chon else 14, color=mau, opacity=.32 if chon else .2),
            ))
            if chon:
                fig.add_annotation(
                    x=cx, y=cy, ax=-60, ay=-40, text=f"<b>{h}</b>", showarrow=True,
                    arrowcolor="#0B3C5D", font=dict(size=13, color="#0B3C5D"),
                )
        else:
            fig.add_annotation(
                x=cx, y=cy, text=f"<b>{h}</b><br>{ngan}", showarrow=False, align="center",
                bgcolor="rgba(255,255,255,.88)",
                bordercolor="#0B3C5D" if chon else "#9FB4C7",
                borderwidth=2 if chon else 1, borderpad=4, font=dict(size=13, color="#14213D"),
            )

    if lop in E.CAY:
        for ten, mau in [(m[1], m[2]) for m in E.MUC] + [("Ngoài vụ", E.MAU_NGOAI_VU)]:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers", name=ten, showlegend=True,
                marker=dict(size=13, color=mau, symbol="square"),
            ))
        fig.update_layout(showlegend=True, legend=dict(x=.01, y=.99, bgcolor="rgba(255,255,255,.85)", font=dict(color="#14213D")))
    else:
        _, cs, lo, hi, _, dv, tf = LOP_THANG[lop]
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(
                color=[lo], cmin=lo, cmax=hi,
                colorscale=[[0, cs[0]], [.5, cs[1]], [1, cs[2]]], showscale=True,
                colorbar=dict(
                    title=dict(text=f"{lop} ({dv})" if dv else lop, side="right"),
                    thickness=14, len=.6, x=.99, y=.5, tickformat=tf, bgcolor="rgba(255,255,255,.85)",
                ),
            ),
        ))

    if che_do == "vn" or not ax:
        xr, yr, h = [101.5, 118.5], [7, 24], 640
    else:
        xr, yr, h = [min(ax) - .12, max(ax) + .12], [min(ay) - .12, max(ay) + .12], 560
    fig.update_xaxes(range=xr, visible=False)
    fig.update_yaxes(range=yr, visible=False, scaleanchor="x", scaleratio=1 / np.cos(np.radians(np.mean(yr))))
    fig.update_layout(height=h, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#BFE3F7")
    return fig


def hien_ban_do(ctx):
    """Khối bản đồ + radio lớp trên trang Tổng quan."""
    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang, vung, huyens = ctx["nam"], ctx["thang"], ctx["vung"], ctx["huyens"]
    sel = dl[(dl.year == nam) & (dl.month == thang)]
    geo_huyen, geo_vn = tai_geo()

    with st.container(border=True):
        st.markdown('<p class="cap">Bản đồ</p>', unsafe_allow_html=True)
        lop = st.radio("Lớp", LOP, horizontal=True, label_visibility="collapsed", key="lop_ban_do")
        st.caption(MO_TA.get(lop, f"Màu = mức khuyến nghị / chỉ số cho {lop} tháng này."))
        t1, t2, t3 = st.tabs(["Toàn quốc", "Phóng to vùng dữ liệu", "Vệ tinh"])
        with t1:
            ve(ban_do(lop, "vn", sel, diem, nam, thang, vung, geo_huyen, geo_vn))
        with t2:
            ve(ban_do(lop, "zoom", sel, diem, nam, thang, vung, geo_huyen, geo_vn))
            if geo_huyen:
                ten = sorted({_ten_ft(f) for f in geo_huyen["features"]})
                st.caption("Huyện trong file ranh giới: " + ", ".join(ten))
                thieu = [h for h in huyens if h not in ten]
                if thieu:
                    st.warning("Có dữ liệu nhưng thiếu ranh giới: " + ", ".join(thieu))
            else:
                st.error("Thiếu data/raw/ranh_gioi_huyen.geojson — copy file từ project cũ.")
        with t3:
            hien_ve_tinh(ctx)
        if not geo_vn:
            st.warning("Thiếu data/raw/viet_nam.geojson — bản đồ nền VN sẽ trống.")
        st.markdown(f"**So sánh 3 huyện, tháng {thang}/{nam}**")
        bang = []
        for h in huyens:
            _, _, ngan = gia_tri(h, lop, sel, diem, nam, thang)
            bang.append({"Huyện": h, lop: ngan})
        st.dataframe(pd.DataFrame(bang).set_index("Huyện"), use_container_width=True)