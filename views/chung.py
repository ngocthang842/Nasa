"""Đồ dùng chung: CSS, tiêu đề, KPI sparkline, thẻ cây."""
import numpy as np
import pandas as pd
import streamlit as st

import engine as E


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp {font-family:'Be Vietnam Pro','Segoe UI',sans-serif;}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.stApp {background:#F4F7F6 !important;}
.block-container {padding:1.1rem 1.4rem 2rem; max-width:1440px;}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp li {color:#14213D;}
.stApp [data-testid="stSidebar"] {background:#0C6B52 !important;}
.stApp [data-testid="stSidebar"] * {color:#FFFFFF !important;}
.stApp [data-testid="stSidebar"] [role="radiogroup"] label {
  background:transparent; border-radius:12px; padding:8px 12px; margin-bottom:2px;
}
.stApp [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked),
.stApp [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {
  background:#FFFFFF !important; color:#0C6B52 !important; font-weight:600;
}
.stApp [data-testid="stSidebar"] [data-baseweb="select"] > div,
.stApp [data-testid="stSidebar"] [data-baseweb="select"] span,
.stApp [data-testid="stSidebar"] [data-baseweb="select"] div {
  background:#FFFFFF !important; color:#14213D !important;
}
.stApp [data-testid="stSidebar"] [data-baseweb="select"] svg {fill:#14213D !important;}
.stApp [data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.25);}
div[data-baseweb="popover"] li, div[data-baseweb="popover"] li * {color:#14213D !important;}
div[data-testid="stVerticalBlockBorderWrapper"] {
  background:#fff; border:1px solid #E4EBE8 !important; border-radius:16px; box-shadow:none;
}
.hero {background:#0C6B52; border-radius:16px; padding:16px 22px;
  display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:8px;}
.hero .eyebrow {margin:0; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:rgba(255,255,255,.72); font-weight:600;}
.hero .ht {font-size:26px; font-weight:650; color:#fff; margin:2px 0 0;}
.hero .terrain {margin:0; font-size:14px; color:rgba(255,255,255,.85);}
.kpi {border:1px solid #E6EEEA; border-radius:16px; padding:12px 14px; background:#fff;}
.kpi .l {font-size:12px; color:#5B6E86; font-weight:500;}
.kpi .v {font-size:26px; font-weight:700; color:#14213D; line-height:1.2; margin-top:2px;}
.kpi .v small {font-size:13px; font-weight:500; color:#5B6E86;}
.kpi .d {font-size:12px; margin-top:2px;}
.up {color:#EF4444;} .dn {color:#0C6B52;} .nt {color:#5B6E86;}
.crop {border:1px solid #E6EEEA; border-left:4px solid var(--c); border-radius:14px; padding:12px 14px; margin-bottom:10px; background:#fff;}
.crop .r {font-size:13px; margin-top:6px; line-height:1.4; color:#33445C;}
.cap {font-size:15px; font-weight:650; margin:0 0 8px; color:#14213D;}
</style>
"""


def ve(fig, **kw):
    try:
        st.plotly_chart(fig, width="stretch", **kw)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, **kw)


def tieu_de(vung, thang, nam, phu, it_nam):
    dia = E.VUNG.get(vung, "")
    if it_nam:
        dia = (dia + " · mới 1 năm").strip(" ·")
    st.markdown(
        f'<div class="hero"><div><p class="eyebrow">{phu}</p>'
        f'<p class="ht">{vung} · Tháng {thang}/{nam}</p></div>'
        f'<p class="terrain">{dia}</p></div>',
        unsafe_allow_html=True,
    )


def spark(v, i, mau):
    v = np.array(v, float)
    ok = ~np.isnan(v)
    if ok.sum() < 2:
        return ""
    lo, hi = np.nanmin(v), np.nanmax(v)
    hi = hi if hi > lo else lo + 1
    xs = np.linspace(2, 118, len(v))
    ys = 32 - 28 * (v - lo) / (hi - lo)
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y, o in zip(xs, ys, ok) if o)
    dot = ""
    if i < len(v) and ok[i]:
        dot = f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="3.5" fill="{mau}"/>'
    return (
        f'<svg width="100%" height="38" viewBox="0 0 120 36" preserveAspectRatio="none">'
        f'<polyline points="{pts}" fill="none" stroke="{mau}" stroke-width="2"/>{dot}</svg>'
    )


def kpi_the(ten, cot, don_vi, mau, chuoi, thang, xau_la_xau="cao", fmt="{:.0f}", nhan=1):
    v = chuoi[cot].tolist()
    ms = chuoi.month.tolist()
    i = ms.index(thang)
    x = v[i] * nhan
    d = ""
    if i > 0 and pd.notna(v[i - 1]):
        dd = (v[i] - v[i - 1]) * nhan
        xau = (dd > 0) == (xau_la_xau == "cao")
        cls = "up" if xau and dd else ("dn" if dd else "nt")
        d = f'<div class="d {cls}">{"▲" if dd > 0 else "▼"} {abs(dd):{fmt[2:-1]}} so với tháng trước</div>'
    return (
        f'<div class="kpi">'
        f'<div class="l">{ten}</div><div class="v">{fmt.format(x)} <small>{don_vi}</small></div>'
        f'{d}</div>'
    )


def the_cay(cur_d):
    """Dùng to_dict để tránh lỗi dat_txt với itertuples."""
    if cur_d is None or len(cur_d) == 0:
        st.info("Tháng này chưa có cây đặc trưng để chấm.")
        return
    for x in cur_d.to_dict("records"):
        rui = x.get("rui_ro")
        w = 0 if rui is None or (isinstance(rui, float) and np.isnan(rui)) else rui
        mau = x.get("mau") or E.MAU_NGOAI_VU
        icon = E.CAY.get(x["cay"], {}).get("icon", "")
        mau = x.get("mau") or E.MAU_NGOAI_VU
        st.markdown(
            f"""<div class="crop" style="--c:{mau}">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
              <span style="font-size:16px;font-weight:650">{x['cay']}</span>
              <span style="font-size:12px;font-weight:650;color:{mau};border:1px solid {mau};border-radius:999px;padding:2px 8px">{x.get('muc','')}</span>
            </div>
            <div style="color:#5B6E86;font-size:12px;margin:4px 0">{x.get('giai_doan','')}</div>
            <div style="height:6px;background:#EEF2F0;border-radius:4px;margin:6px 0;overflow:hidden">
              <div style="width:{w:.0f}%;height:100%;background:{mau}"></div>
            </div>
            <div class="r">{x.get('ly_do','')}</div>
            <div style="color:#5B6E86;font-size:12px;margin-top:4px">{x.get('dat_txt') or ''}</div>
            </div>""",
            unsafe_allow_html=True,
        )