"""Đồ dùng chung: CSS theme Trắng chuyên nghiệp, tiêu đề, KPI sparkline, thẻ cây."""
import numpy as np
import pandas as pd
import streamlit as st

import engine as E

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {
  font-family: 'Be Vietnam Pro', 'Segoe UI', -apple-system, sans-serif !important;
}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.stApp {
  background: #F8FAFC !important;
}
.block-container {
  padding: 1.2rem 1.6rem 2.5rem;
  max-width: 1440px;
}
div[data-testid="stMain"] h1,
div[data-testid="stMain"] h2,
div[data-testid="stMain"] h3,
div[data-testid="stMain"] h4,
div[data-testid="stMain"] p,
div[data-testid="stMain"] label,
div[data-testid="stMain"] li {
  color: #0F172A;
}

/* =========================================================================
   SIDEBAR THEME: DARK COMMAND CENTER (NASA NEDA - PHÓNG TO & CĂN CHỈNH ĐẸP MẮT)
   Độ rộng 340px, Thẻ menu 15.5px, Nền dạ quang Teal, Ẩn triệt để chấm radio
   ========================================================================= */
[data-testid="stSidebar"] {
  background-color: #0A111E !important;
  min-width: 330px !important;
  max-width: 360px !important;
  border-right: 1.5px solid #1E293B !important;
  box-shadow: 6px 0 25px rgba(0, 0, 0, 0.4) !important;
}

[data-testid="stSidebar"] > div:first-child {
  padding: 1rem 1rem 2rem 1rem !important;
}

[data-testid="stSidebar"] * {
  color: #94A3B8;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] b,
[data-testid="stSidebar"] strong {
  color: #F8FAFC !important;
}

/* ĐIỀU CHỈNH DROPDOWN / SELECTBOX TRONG SIDEBAR THEME TỐI */
[data-testid="stSidebar"] div[data-baseweb="select"] {
  background-color: #111C2E !important;
  border-radius: 10px !important;
  border: 1.5px solid #1E293B !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background-color: #111C2E !important;
  border: none !important;
  min-height: 44px !important;
  border-radius: 10px !important;
}

/* Chữ trong ô chọn: MÀU TRẮNG SÁNG #F8FAFC */
[data-testid="stSidebar"] div[data-baseweb="select"] * {
  color: #F8FAFC !important;
  -webkit-text-fill-color: #F8FAFC !important;
  font-weight: 650 !important;
  font-size: 14px !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] p {
  color: #F8FAFC !important;
  -webkit-text-fill-color: #F8FAFC !important;
  margin: 0 !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] svg {
  fill: #94A3B8 !important;
}

/* POPOVER DANH SÁCH DROPDOWN KHI CLICK VÀO */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div {
  background-color: #111C2E !important;
  border-radius: 10px !important;
  border: 1.5px solid #1E293B !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important;
}

div[data-baseweb="popover"] *,
ul[role="listbox"],
ul[role="listbox"] * {
  background-color: #111C2E !important;
  color: #F8FAFC !important;
  -webkit-text-fill-color: #F8FAFC !important;
  font-size: 14px !important;
}

ul[role="listbox"] li:hover,
ul[role="listbox"] li:hover * {
  background-color: #1E293B !important;
  color: #2DD4BF !important;
  -webkit-text-fill-color: #2DD4BF !important;
}

/* THIẾT KẾ MENU SIDEBAR NASA NEDA DẠNG THẺ LỚN (EXPANDED CARDS) */
div[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] {
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  padding: 4px 0 !important;
}

div[data-testid="stSidebar"] div[data-testid="stRadio"] label {
  display: flex !important;
  align-items: center !important;
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1.5px solid rgba(255, 255, 255, 0.07) !important;
  border-radius: 12px !important;
  padding: 12px 16px !important;
  margin: 0 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
}

/* ẨN TRIỆT ĐỂ DẤU CHẤM TRÒN RADIO TRÊN MỌI PHIÊN BẢN STREAMLIT (REACT ARIA) */
div[data-testid="stSidebar"] div[data-testid="stRadio"] label > div > div:first-child,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label > div > span,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label input[type="radio"],
div[data-testid="stSidebar"] div[data-testid="stRadio"] label span:has(input[type="radio"]),
div[data-testid="stSidebar"] div[data-testid="stRadio"] label div[class*="RadioMark"],
div[data-testid="stSidebar"] div[data-testid="stRadio"] label [data-testid="stRadioMark"],
div[data-testid="stSidebar"] div[data-testid="stRadio"] label div[class*="ex50key4"],
div[data-testid="stSidebar"] div[data-testid="stRadio"] label div[class*="ex50key5"],
div[data-testid="stSidebar"] div[data-testid="stRadioOption"] > div > div:first-child,
div[data-testid="stSidebar"] [role="radiogroup"] label div:first-child:not(:last-child) {
  display: none !important;
  opacity: 0 !important;
  width: 0 !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  visibility: hidden !important;
}

/* CHỮ MENU MẶC ĐỊNH: TO RÕ RÀNG (15px), MÀU BẠC ÁNH KIM */
div[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label span,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label * {
  color: #94A3B8 !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  line-height: 1.35 !important;
  letter-spacing: -0.1px !important;
}

/* HOVER: SÁNG BỪNG TRẮNG BẠC, TRƯỢT NHẸ SANG PHẢI */
div[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
  background: rgba(255, 255, 255, 0.08) !important;
  border-color: rgba(45, 212, 191, 0.35) !important;
  transform: translateX(4px) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
}

div[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover * {
  color: #FFFFFF !important;
}

/* MỤC ĐANG CHỌN (ACTIVE): PHÓNG TO, NỀN GRADIENT TEAL, VIỀN XANH NGỌC SÁNG */
div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(20, 184, 166, 0.24) 0%, rgba(20, 184, 166, 0.10) 100%) !important;
  border: 1.5px solid rgba(45, 212, 191, 0.5) !important;
  border-left: 5px solid #2DD4BF !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 18px rgba(20, 184, 166, 0.2) !important;
}

div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span,
div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) * {
  color: #2DD4BF !important;
  font-size: 15.5px !important;
  font-weight: 800 !important;
}

/* Radio ngang (Chế độ xem Đợt vs Tháng) */
[data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] {
  display: flex !important;
  flex-direction: row !important;
  gap: 6px !important;
}

[data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] > label {
  flex: 1 1 0 !important;
  justify-content: center !important;
  padding: 8px 6px !important;
  text-align: center !important;
  background: #F8FAFC !important;
  border: 1px solid #E2E8F0 !important;
}

[data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] > label p {
  font-size: 12.5px !important;
  white-space: nowrap !important;
  color: #334155 !important;
}

[data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] > label:has(input:checked) {
  background: #0F172A !important;
  border-color: #0F172A !important;
}

[data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] > label:has(input:checked) p {
  color: #FFFFFF !important;
  font-weight: 700 !important;
}

/* Slider trong Sidebar */
[data-testid="stSidebar"] [data-testid="stSlider"] div[data-testid="stWidgetLabel"] p {
  color: #0F172A !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stSliderThumbValue"] {
  color: #FFFFFF !important;
  font-weight: 700 !important;
  background: #0F172A !important;
  border-radius: 6px !important;
  padding: 2px 6px !important;
}

[data-testid="stSidebar"] hr {
  border-color: #E2E8F0 !important;
  margin: 14px 0 !important;
}

/* =========================================================================
   GIAO DIỆN TRANG CHÍNH: THEME TRẮNG TỐI GIẢN & HIỆN ĐẠI (CLEAN STUDIO)
   ========================================================================= */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 16px !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
}

/* HERO BANNER "TỔNG QUAN": ĐỔI TỪ MÀU XANH LÁ SANG MÀU TRẮNG TINH TẾ */
.hero {
  background: #FFFFFF !important;
  border: 1.5px solid #E2E8F0 !important;
  border-radius: 16px !important;
  padding: 20px 26px !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: flex-end !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
.hero .eyebrow {
  margin: 0 !important;
  font-size: 11.5px !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: #64748B !important;
  font-weight: 700 !important;
}
.hero .ht {
  font-size: 26px !important;
  font-weight: 800 !important;
  color: #0F172A !important;
  margin: 4px 0 0 !important;
  letter-spacing: -0.4px !important;
}
.hero .terrain {
  margin: 0 !important;
  font-size: 13.5px !important;
  color: #334155 !important;
  background: #F1F5F9 !important;
  border: 1px solid #CBD5E1 !important;
  padding: 5px 14px !important;
  border-radius: 20px !important;
  font-weight: 600 !important;
}

.kpi {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 14px 16px;
  background: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.06);
}
.kpi .l {
  font-size: 12px;
  color: #64748B;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.kpi .v {
  font-size: 26px;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.2;
  margin-top: 4px;
}
.kpi .v small {
  font-size: 13px;
  font-weight: 600;
  color: #64748B;
}
.kpi .d {
  font-size: 12px;
  margin-top: 4px;
  font-weight: 600;
}
.up { color: #DC2626; }
.dn { color: #16A34A; }
.nt { color: #64748B; }

.crop {
  border: 1px solid #E2E8F0;
  border-left: 4.5px solid var(--c);
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 10px;
  background: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.crop .r {
  font-size: 13px;
  margin-top: 6px;
  line-height: 1.45;
  color: #334155;
}
.cap {
  font-size: 16px;
  font-weight: 750;
  margin: 0 0 10px;
  color: #0F172A;
  letter-spacing: -0.2px;
}

/* Nút bấm (Buttons) */
button[kind="primary"],
.stButton > button {
  background-color: #0F172A !important;
  color: #FFFFFF !important;
  border: 1px solid #0F172A !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all 0.2s ease !important;
}
button[kind="primary"]:hover,
.stButton > button:hover {
  background-color: #1E293B !important;
  border-color: #1E293B !important;
  transform: translateY(-1px) !important;
}
</style>
"""

NASA_LOGO_SVG = '<svg width="42" height="42" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;flex-shrink:0;"><circle cx="60" cy="60" r="58" fill="#0B3D91"/><circle cx="28" cy="38" r="1.6" fill="#FFFFFF"/><circle cx="46" cy="22" r="1.3" fill="#FFFFFF"/><circle cx="86" cy="28" r="1.8" fill="#FFFFFF"/><circle cx="96" cy="62" r="1.4" fill="#FFFFFF"/><circle cx="34" cy="84" r="1.6" fill="#FFFFFF"/><circle cx="76" cy="88" r="1.3" fill="#FFFFFF"/><path d="M20 62 L98 34 L78 52 L96 56 L38 80 Z" fill="#FC3D21"/><ellipse cx="60" cy="60" rx="52" ry="19" stroke="#FFFFFF" stroke-width="2.6" fill="none" transform="rotate(-32 60 60)"/><text x="60" y="69" font-family="Arial,sans-serif" font-weight="900" font-size="28" fill="#FFFFFF" text-anchor="middle" letter-spacing="2">NASA</text></svg>'


def ve(fig, che_do="co_dinh", **kw):
    """Vẽ biểu đồ Plotly với cơ chế tương tác chuẩn chuyên nghiệp.
    
    che_do:
    - 'co_dinh': Dành cho biểu đồ cột (Bar), KPI, đồng hồ đo (Gauge), Gantt chart.
                 Khóa hoàn toàn kéo hộp zoom (dragmode=False) tránh biến dạng khi rê chuột.
                 Chỉ hiển thị hover tooltip sắc nét, cố định tỷ lệ chuẩn mực.
    - 'tuong_tac': Dành cho biểu đồ đường chuỗi thời gian nhiều năm.
                   Hỗ trợ Pan di chuyển mượt mà (dragmode='pan') và 4 nút chuẩn: [+] [-] [🖐️] [⟲].
                   Tuyệt đối loại bỏ kéo hộp chọn vùng (box zoom), tắt cuộn chuột zoom nhầm.
    """
    if che_do == "co_dinh":
        fig.update_layout(dragmode=False)
        cfg = kw.pop("config", {
            "displayModeBar": False,
            "scrollZoom": False,
            "responsive": True,
        })
    else:
        fig.update_layout(dragmode="pan")
        cfg = kw.pop("config", {
            "displayModeBar": True,
            "modeBarButtonsToAdd": ["zoomIn2d", "zoomOut2d", "resetScale2d", "pan2d"],
            "modeBarButtonsToRemove": ["select2d", "lasso2d", "zoom2d", "autoScale2d", "toImage"],
            "displaylogo": False,
            "scrollZoom": False,
            "responsive": True,
        })

    try:
        st.plotly_chart(fig, width="stretch", config=cfg, **kw)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config=cfg, **kw)


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
    if i > 0 and pd.notna(v[i - 1]) and pd.notna(v[i]):
        dd = (v[i] - v[i - 1]) * nhan
        xau = (dd > 0) == (xau_la_xau == "cao")
        cls = "up" if xau and dd else ("dn" if dd else "nt")
        d = f'<div class="d {cls}">{"▲" if dd > 0 else "▼"} {abs(dd):{fmt[2:-1]}} so với tháng trước</div>'
    
    # Xử lý an toàn khi giá trị NaN
    if pd.isna(x):
        val_str = "—"
        unit_str = ""
    else:
        val_str = fmt.format(x)
        unit_str = f"<small>{don_vi}</small>"

    return (
        f'<div class="kpi">'
        f'<div class="l">{ten}</div><div class="v">{val_str} {unit_str}</div>'
        f'{d}</div>'
    )


def the_cay(cur_d):
    """Dùng to_dict để tránh lỗi dat_txt với itertuples, ưu tiên Cây Lúa hiển thị lên đầu."""
    if cur_d is None or len(cur_d) == 0:
        st.info("Tháng này chưa có thông tin mùa vụ.")
        return
    recs = cur_d.to_dict("records")
    # Đưa Lúa lên vị trí đầu tiên
    recs = sorted(recs, key=lambda x: 0 if x.get("cay") == "Lúa" else 1)
    for x in recs:
        rui = x.get("rui_ro")
        w = 0 if rui is None or (isinstance(rui, float) and np.isnan(rui)) else rui
        mau = x.get("mau") or E.MAU_NGOAI_VU
        icon = E.CAY.get(x["cay"], {}).get("icon", "🌱")
        st.markdown(
            f"""<div class="crop" style="--c:{mau}">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
              <span style="font-size:16px;font-weight:750;color:#0F172A">{icon} {x['cay']}</span>
              <span style="font-size:12px;font-weight:700;color:{mau};border:1px solid {mau};border-radius:999px;padding:2px 8px">{x.get('muc','')}</span>
            </div>
            <div style="color:#64748B;font-size:12px;margin:4px 0">{x.get('giai_doan','')}</div>
            <div style="height:6px;background:#F1F5F9;border-radius:4px;margin:6px 0;overflow:hidden">
              <div style="width:{w:.0f}%;height:100%;background:{mau}"></div>
            </div>
            <div class="r">{x.get('ly_do','')}</div>
            <div style="color:#64748B;font-size:12px;margin-top:4px">{x.get('dat_txt') or ''}</div>
            </div>""",
            unsafe_allow_html=True,
        )
