"""Module Tra Cứu & Khảo Sát Viễn Thám Theo Thời Gian (Ngày - Tháng - Năm).
Cung cấp công cụ Research chuyên sâu chuỗi dữ liệu 9 năm (2018–2026) Yên Thành:
1. Tra cứu theo Ngày Cụ Thể (Daily Telemetry Date Picker 3.240 ngày)
2. Tra cứu theo Khoảng Thời Gian Tùy Chọn (Date Range Analysis: Đợt hạn, đợt bão lũ)
3. Tra cứu theo Tháng & Đối Chiếu Chuỗi 9 Năm (Monthly Satellite Matrix)
Dữ liệu tích hợp: NASA POWER Daily, MODIS NDVI/EVI/LAI/LST, SMAP L-band, GPM IMERG.
"""
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import engine as E
from views.chung import tieu_de, ve, kpi_the

# Icon chu kỳ nông học 12 tháng lúa Yên Thành
ICON_THANG = {
    1: "🌱", 2: "🌿", 3: "🌾", 4: "🌸", 5: "✨",
    6: "🌱", 7: "🌿", 8: "🌾", 9: "🌊", 10: "🚜", 11: "☀️", 12: "💧"
}


@st.cache_data(show_spinner=False)
def tai_du_lieu_ngay():
    """Tải và làm sạch chuỗi dữ liệu thời tiết & viễn thám từng ngày (2018–2026)."""
    p = "data/raw/power/power_Yen_Thanh.csv"
    try:
        df = pd.read_csv(p)
        df["date_dt"] = pd.to_datetime(df["date"])
        df = df.dropna(subset=["T2M_MAX"])
        df["year"] = df["date_dt"].dt.year
        df["month"] = df["date_dt"].dt.month
        df["day"] = df["date_dt"].dt.day
        return df
    except Exception:
        return pd.DataFrame()


def hien(ctx):
    """View chính: Tra Cứu & Research Viễn Thám Theo Thời Gian (Ngày / Tháng / Năm)."""
    dl = ctx["dl"]
    vung = ctx.get("vung", "Yên Thành")
    nam = ctx.get("nam", 2026)
    thang = ctx.get("thang", 4)
    years = ctx.get("years", list(range(2018, 2027)))

    tieu_de(
        vung,
        thang,
        nam,
        "TRA CỨU & KHẢO SÁT VIỄN THÁM THEO THỜI GIAN (NGÀY - THÁNG - NĂM)",
        False,
    )

    df_daily = tai_du_lieu_ngay()

    if df_daily.empty:
        st.error("Không tìm thấy tệp dữ liệu thời tiết viễn thám từng ngày (data/raw/power/power_Yen_Thanh.csv).")
        return

    min_date = df_daily["date_dt"].dt.date.min()
    max_date = df_daily["date_dt"].dt.date.max()

    tab1, tab2, tab3 = st.tabs([
        "📅 1. Tra Cứu Từng Ngày Cụ Thể (Daily Date Picker)",
        "📆 2. Tra Cứu Theo Khoảng Thời Gian (Date Range)",
        "🗓️ 3. Tra Cứu Đối Chiếu Đa Năm Theo Tháng (2018–2026)",
    ])

    with tab1:
        _hien_tab_ngay(df_daily, min_date, max_date, dl, vung)

    with tab2:
        _hien_tab_khoang_ngay(df_daily, min_date, max_date)

    with tab3:
        _hien_tab_thang_nam(dl, vung, years)


# =============================================================================
# TAB 1: TRA CỨU TỪNG NGÀY CỤ THỂ (DAILY LOOKUP)
# =============================================================================

def _hien_tab_ngay(df_daily, min_date, max_date, dl, vung):
    """Tra cứu chi tiết từng ngày trong chuỗi 3.240 ngày lịch sử NASA."""
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            '🔍 Chọn Ngày Cần Tra Cứu Viễn Thám & Khí Tượng Yên Thành (2018–2026):'
            '</div>'
            '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
            f'Kho dữ liệu tích hợp liên tục 3.237 ngày từ {min_date.strftime("%d/%m/%Y")} đến {max_date.strftime("%d/%m/%Y")}.'
            '</div>',
            unsafe_allow_html=True,
        )

        col_d1, col_d2, col_d3 = st.columns([4, 4, 4], gap="small")
        with col_d1:
            ngay_mac_dinh = datetime.date(2026, 4, 15)
            if ngay_mac_dinh > max_date:
                ngay_mac_dinh = max_date
            ngay_chon = st.date_input(
                "Chọn ngày:",
                value=ngay_mac_dinh,
                min_value=min_date,
                max_value=max_date,
                key="picker_date_single",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )

        with col_d2:
            st.markdown(
                '<div style="font-size:11.5px; color:#334155; padding-top:6px;">'
                '💡 <i>Gợi ý tra cứu nhanh:</i>'
                '</div>',
                unsafe_allow_html=True,
            )
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔥 Đỉnh hạn 2019 (22/06)", use_container_width=True):
                    st.session_state["picker_date_single"] = datetime.date(2019, 6, 22)
                    st.rerun()
            with col_b2:
                if st.button("🌊 Đỉnh lũ 2020 (19/10)", use_container_width=True):
                    st.session_state["picker_date_single"] = datetime.date(2020, 10, 19)
                    st.rerun()

        with col_d3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("🌸 Ngày trổ lúa xuân 2026 (15/04)", use_container_width=True):
                st.session_state["picker_date_single"] = datetime.date(2026, 4, 15)
                st.rerun()

    # Trích xuất dữ liệu ngày được chọn
    sub_day = df_daily[df_daily["date_dt"].dt.date == ngay_chon]
    if sub_day.empty:
        st.warning(f"Không tìm thấy số liệu cho ngày {ngay_chon.strftime('%d/%m/%Y')}.")
        return

    r = sub_day.iloc[0]
    tmax = float(r["T2M_MAX"])
    tmin = float(r["T2M_MIN"])
    delta_t = tmax - tmin
    mua = float(r["PRECTOTCORR"]) if pd.notna(r["PRECTOTCORR"]) else 0.0
    rh = float(r["RH2M"]) if pd.notna(r["RH2M"]) else 75.0
    ws = float(r["WS2M"]) if pd.notna(r["WS2M"]) else 2.0
    rad = float(r["ALLSKY_SFC_SW_DWN"]) if pd.notna(r["ALLSKY_SFC_SW_DWN"]) else 15.0

    # Phân loại thời tiết ngày
    is_gio_lao = (tmax >= 35.0 and rh <= 65.0) or tmax >= 37.0
    is_ret = tmin < 15.0
    is_mua_lon = mua >= 50.0

    if is_gio_lao:
        tt_loai = "🔥 NGÀY NẮNG NÓNG GIÓ LÀO TÂY NAM (HIỆU ỨNG PHƠN)"
        tt_mau = "#DC2626"
        tt_bg = "#FEF2F2"
        khuyen_cao = "Nhiệt độ vượt 35°C kèm ẩm thấp: Rất nguy hiểm nếu lúa đang trỗ bông (gây khô phấn lép hạt). Mệnh lệnh: Dâng nước đệm 3–5 cm làm mát gốc lúa."
    elif is_ret:
        tt_loai = "❄️ NGÀY RÉT ĐẬM HẠI MẠ NON"
        tt_mau = "#2563EB"
        tt_bg = "#EFF6FF"
        khuyen_cao = "Nhiệt độ đêm dưới 15°C: Nguy cơ chết rét mạ non đầu vụ xuân. Mệnh lệnh: Che phủ nilon 100%, tuyệt đối không bón đạm urê."
    elif is_mua_lon:
        tt_loai = "🌊 NGÀY MƯA TO DỒN DẬP (NGUY CƠ NGẬP LÒNG CHẢO)"
        tt_mau = "#0284C7"
        tt_bg = "#F0F9FF"
        khuyen_cao = f"Lượng mưa ngày đạt {mua:.1f} mm: Nước dồn nhanh về Kênh Vách Bắc. Cần kiểm tra cống tiêu thoát nước chống ngập thối giống."
    else:
        tt_loai = "🟢 THỜI TIẾT ỔN ĐỊNH THUẬN LỢI CHO CÂY LÚA"
        tt_mau = "#16A34A"
        tt_bg = "#F0FDF4"
        khuyen_cao = "Điều kiện nhiệt ẩm và ánh sáng đạt chuẩn tối ưu sinh lý cây lúa nước Yên Thành."

    # Xác định vụ lúa và giai đoạn theo tháng của ngày đó
    thang_ngay = ngay_chon.month
    if thang_ngay <= 5:
        vu_str = f"🌾 Vụ Lúa Chiêm Xuân (Tháng {thang_ngay})"
    elif thang_ngay <= 9:
        vu_str = f"☀️ Vụ Lúa Hè Thu (Tháng {thang_ngay})"
    else:
        vu_str = f"🚜 Vụ Đông & Cày Phơi Ải (Tháng {thang_ngay})"

    # BANNER THỜI TIẾT & KHUYẾN NGHỊ NGÀY
    st.markdown(
        f"""
        <div style="background:{tt_bg}; border:1.5px solid {tt_mau}40; border-left:6px solid {tt_mau}; border-radius:12px; padding:12px 18px; margin-top:8px; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-size:14px; font-weight:800; color:{tt_mau};">
              {tt_loai}
            </div>
            <div style="background:#FFFFFF; border:1px solid {tt_mau}40; border-radius:999px; padding:2px 12px; font-size:12px; font-weight:750; color:{tt_mau};">
              📅 Ngày {ngay_chon.strftime('%d/%m/%Y')} · {vu_str}
            </div>
          </div>
          <div style="font-size:12.5px; color:#1E293B; margin-top:6px; line-height:1.5;">
            <b>🌾 Đánh giá tác động nông học:</b> {khuyen_cao}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # BỘ 6 THẺ TELEMETRY ĐO ĐẠC TRONG NGÀY
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6, gap="small")
    with c1:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 8px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Nhiệt độ Max (Tmax)</div>
              <div style="font-size:20px; font-weight:800; color:#F97316; margin-top:2px;">{tmax:.1f}°C</div>
              <div style="font-size:10.5px; color:#94A3B8;">NASA POWER</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 8px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Nhiệt độ Min (Tmin)</div>
              <div style="font-size:20px; font-weight:800; color:#0284C7; margin-top:2px;">{tmin:.1f}°C</div>
              <div style="font-size:10.5px; color:#94A3B8;">Ban đêm</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 8px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Biên độ nhiệt (ΔT)</div>
              <div style="font-size:20px; font-weight:800; color:#0F172A; margin-top:2px;">{delta_t:.1f}°C</div>
              <div style="font-size:10.5px; color:#94A3B8;">Ngày - Đêm</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 8px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Mưa tích lũy ngày</div>
              <div style="font-size:20px; font-weight:800; color:#0EA5E9; margin-top:2px;">{mua:.1f} mm</div>
              <div style="font-size:10.5px; color:#94A3B8;">GPM / POWER</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 8px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Độ ẩm không khí (RH)</div>
              <div style="font-size:20px; font-weight:800; color:#10B981; margin-top:2px;">{rh:.0f}%</div>
              <div style="font-size:10.5px; color:#94A3B8;">Cảm biến 2m</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 8px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Bức xạ quang hợp</div>
              <div style="font-size:20px; font-weight:800; color:#F59E0B; margin-top:2px;">{rad:.1f}</div>
              <div style="font-size:10.5px; color:#94A3B8;">MJ/m²/ngày</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # BIỂU ĐỒ 30 NGÀY XUNG QUANH NGÀY ĐANG CHỌN (15 NGÀY TRƯỚC + 15 NGÀY SAU)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            f'📈 Diễn Biến Khí Tượng 30 Ngày Lân Cận (Xung quanh ngày {ngay_chon.strftime("%d/%m/%Y")})'
            f'</div>'
            f'<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
            f'Quan sát xu thế nhiệt độ Tmax/Tmin và các đợt mưa rào xung quanh ngày được chọn để đánh giá chu kỳ thời tiết.'
            f'</div>',
            unsafe_allow_html=True,
        )

        dt_start = ngay_chon - datetime.timedelta(days=15)
        dt_end = ngay_chon + datetime.timedelta(days=15)
        sub_30d = df_daily[(df_daily["date_dt"].dt.date >= dt_start) & (df_daily["date_dt"].dt.date <= dt_end)].sort_values("date_dt")

        if not sub_30d.empty:
            fig_30 = make_subplots(specs=[[{"secondary_y": True}]])

            # Mưa dạng cột
            fig_30.add_trace(go.Bar(
                x=[d.strftime("%d/%m") for d in sub_30d["date_dt"]],
                y=sub_30d["PRECTOTCORR"],
                name="Mưa (mm/ngày)",
                marker=dict(color="rgba(14, 165, 233, 0.45)", line=dict(color="#0284C7", width=1)),
                hovertemplate="Ngày %{x}<br>Mưa: <b>%{y:.1f} mm</b><extra></extra>",
            ), secondary_y=False)

            # Tmax
            fig_30.add_trace(go.Scatter(
                x=[d.strftime("%d/%m") for d in sub_30d["date_dt"]],
                y=sub_30d["T2M_MAX"],
                name="Tmax (°C)",
                mode="lines+markers",
                line=dict(color="#F97316", width=2.5),
                marker=dict(size=6, color="#F97316"),
                hovertemplate="Ngày %{x}<br>Tmax: <b>%{y:.1f}°C</b><extra></extra>",
            ), secondary_y=True)

            # Tmin
            fig_30.add_trace(go.Scatter(
                x=[d.strftime("%d/%m") for d in sub_30d["date_dt"]],
                y=sub_30d["T2M_MIN"],
                name="Tmin (°C)",
                mode="lines+markers",
                line=dict(color="#0284C7", width=2, dash="dot"),
                marker=dict(size=5, color="#0284C7"),
                hovertemplate="Ngày %{x}<br>Tmin: <b>%{y:.1f}°C</b><extra></extra>",
            ), secondary_y=True)

            # Đường chỉ định ngày đang chọn
            lbl_cur = ngay_chon.strftime("%d/%m")
            fig_30.add_shape(
                type="line",
                x0=lbl_cur,
                x1=lbl_cur,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="#0F172A", width=2, dash="dash"),
            )
            fig_30.add_annotation(
                x=lbl_cur,
                y=1.04,
                yref="paper",
                text=f"Ngày {lbl_cur}",
                showarrow=False,
                font=dict(size=11, color="#0F172A", weight=750),
                bgcolor="#F1F5F9",
                bordercolor="#CBD5E1",
                borderwidth=1,
            )

            fig_30.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=25, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11)),
                xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
            )
            fig_30.update_yaxes(title_text="Mưa (mm)", secondary_y=False, showgrid=True, gridcolor="#F8FAFC")
            fig_30.update_yaxes(title_text="Nhiệt độ (°C)", secondary_y=True, showgrid=False)
            ve(fig_30, che_do="co_dinh")


# =============================================================================
# TAB 2: TRA CỨU THEO KHOẢNG THỜI GIAN (DATE RANGE ANALYSIS)
# =============================================================================

def _hien_tab_khoang_ngay(df_daily, min_date, max_date):
    """Phân tích thống kê và diễn biến trong một khoảng thời gian bất kỳ (ví dụ: đợt hạn, mùa lũ)."""
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            '📆 Chọn Khoảng Thời Gian Nghiên Cứu (Từ Ngày → Đến Ngày):'
            '</div>'
            '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
            'Phân tích tổng hợp vũ lượng tích lũy, số ngày nắng nóng gió Lào và các hiện tượng cực đoan.'
            '</div>',
            unsafe_allow_html=True,
        )

        d_from_def = datetime.date(2025, 6, 1)
        d_to_def = datetime.date(2025, 7, 31)

        c_r1, c_r2 = st.columns([6, 6], gap="small")
        with c_r1:
            range_val = st.date_input(
                "Khoảng ngày khảo sát:",
                value=(d_from_def, d_to_def),
                min_value=min_date,
                max_value=max_date,
                key="picker_date_range",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )

        with c_r2:
            col_k1, col_k2, col_k3 = st.columns(3)
            with col_k1:
                if st.button("🌾 Vụ Xuân 2026", use_container_width=True):
                    st.session_state["picker_date_range"] = (datetime.date(2026, 1, 1), datetime.date(2026, 5, 31))
                    st.rerun()
            with col_k2:
                if st.button("☀️ Vụ Hè Thu 2025", use_container_width=True):
                    st.session_state["picker_date_range"] = (datetime.date(2025, 6, 1), datetime.date(2025, 9, 20))
                    st.rerun()
            with col_k3:
                if st.button("🌊 Mùa Lũ 2020", use_container_width=True):
                    st.session_state["picker_date_range"] = (datetime.date(2020, 9, 15), datetime.date(2020, 11, 15))
                    st.rerun()

    if isinstance(range_val, (list, tuple)) and len(range_val) == 2:
        d_start, d_end = range_val
    else:
        d_start = range_val[0] if isinstance(range_val, (list, tuple)) else range_val
        d_end = d_start

    sub_range = df_daily[(df_daily["date_dt"].dt.date >= d_start) & (df_daily["date_dt"].dt.date <= d_end)].sort_values("date_dt")

    if sub_range.empty:
        st.info("Vui lòng chọn ngày bắt đầu và kết thúc hợp lệ.")
        return

    # Thống kê tổng hợp trong khoảng
    so_ngay = len(sub_range)
    tong_mua = float(sub_range["PRECTOTCORR"].sum())
    tmax_max = float(sub_range["T2M_MAX"].max())
    tmax_tb = float(sub_range["T2M_MAX"].mean())
    tmin_min = float(sub_range["T2M_MIN"].min())
    so_ngay_35 = int((sub_range["T2M_MAX"] >= 35.0).sum())
    so_ngay_mua = int((sub_range["PRECTOTCORR"] >= 5.0).sum())

    # BỘ THẺ THỐNG KÊ ĐỢT
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    c_s1, c_s2, c_s3, c_s4, c_s5 = st.columns(5, gap="small")
    with c_s1:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Tổng số ngày</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin-top:2px;">{so_ngay} <small style="font-size:12px;">ngày</small></div>
              <div style="font-size:10.5px; color:#16A34A;">{d_start.strftime('%d/%m')} → {d_end.strftime('%d/%m/%Y')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_s2:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Tổng lượng mưa</div>
              <div style="font-size:22px; font-weight:800; color:#0284C7; margin-top:2px;">{tong_mua:.0f} <small style="font-size:12px;">mm</small></div>
              <div style="font-size:10.5px; color:#475569;">Có {so_ngay_mua} ngày mưa</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_s3:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Gió Lào ≥35°C</div>
              <div style="font-size:22px; font-weight:800; color:#DC2626; margin-top:2px;">{so_ngay_35} <small style="font-size:12px;">ngày</small></div>
              <div style="font-size:10.5px; color:#DC2626;">Đỉnh nhiệt {tmax_max:.1f}°C</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_s4:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Nhiệt độ TB</div>
              <div style="font-size:22px; font-weight:800; color:#F97316; margin-top:2px;">{tmax_tb:.1f} <small style="font-size:12px;">°C</small></div>
              <div style="font-size:10.5px; color:#475569;">Đáy lạnh {tmin_min:.1f}°C</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_s5:
        rad_tb = float(sub_range["ALLSKY_SFC_SW_DWN"].mean())
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; text-align:center;">
              <div style="font-size:11px; font-weight:700; color:#64748B;">Bức xạ mặt trời TB</div>
              <div style="font-size:22px; font-weight:800; color:#F59E0B; margin-top:2px;">{rad_tb:.1f}</div>
              <div style="font-size:10.5px; color:#475569;">MJ/m²/ngày</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # BIỂU ĐỒ DIỄN BIẾN TOÀN BỘ KHOẢNG THỜI GIAN
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            f'📊 Biểu Đồ Diễn Biến Khí Tượng Chuỗi {so_ngay} Ngày ({d_start.strftime("%d/%m/%Y")} → {d_end.strftime("%d/%m/%Y")})'
            f'</div>',
            unsafe_allow_html=True,
        )

        fig_rng = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rng.add_trace(go.Bar(
            x=sub_range["date"],
            y=sub_range["PRECTOTCORR"],
            name="Mưa (mm/ngày)",
            marker=dict(color="rgba(14, 165, 233, 0.4)"),
        ), secondary_y=False)

        fig_rng.add_trace(go.Scatter(
            x=sub_range["date"],
            y=sub_range["T2M_MAX"],
            name="Tmax (°C)",
            mode="lines",
            line=dict(color="#F97316", width=2),
        ), secondary_y=True)

        fig_rng.add_trace(go.Scatter(
            x=sub_range["date"],
            y=sub_range["T2M_MIN"],
            name="Tmin (°C)",
            mode="lines",
            line=dict(color="#0284C7", width=1.5, dash="dot"),
        ), secondary_y=True)

        # Ngưỡng 35 độ
        fig_rng.add_hline(y=35, line_dash="dash", line_color="#DC2626", annotation_text="Ngưỡng Gió Lào 35°C", annotation_font_size=10, annotation_font_color="#DC2626", secondary_y=True)

        fig_rng.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=20, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            legend=dict(orientation="h", y=1.1, x=0),
            xaxis=dict(showgrid=True, gridcolor="#F8FAFC"),
        )
        fig_rng.update_yaxes(title_text="Mưa (mm)", secondary_y=False, showgrid=True, gridcolor="#F1F5F9")
        fig_rng.update_yaxes(title_text="Nhiệt độ (°C)", secondary_y=True, showgrid=False)
        ve(fig_rng, che_do="tuong_tac")

    # BẢNG DỮ LIỆU TỪNG NGÀY
    with st.expander(f"📋 Bảng số liệu chi tiết từng ngày trong khoảng ({so_ngay} dòng)", expanded=False):
        df_tbl = sub_range[["date", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN"]].copy()
        df_tbl.columns = ["Ngày (YYYY-MM-DD)", "Tmax (°C)", "Tmin (°C)", "Mưa (mm)", "Độ ẩm (%)", "Gió (m/s)", "Bức xạ (MJ/m²)"]
        st.dataframe(df_tbl, use_container_width=True, hide_index=True)


# =============================================================================
# TAB 3: TRA CỨU ĐỐI CHIẾU ĐA NĂM THEO THÁNG (2018–2026)
# =============================================================================

def _hien_tab_thang_nam(dl, vung, years):
    """Đối chiếu toàn bộ chuỗi 107 tháng và 9 năm của viễn thám NASA."""
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            '🗓️ Ma Trận Đối Chiếu Viễn Thám NASA 12 Tháng Chuỗi 9 Năm Yên Thành (2018–2026)'
            '</div>'
            '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
            'Chọn chỉ số vệ tinh muốn nghiên cứu đối chiếu lịch sử qua các năm.'
            '</div>',
            unsafe_allow_html=True,
        )

        chi_so_dict = {
            "Sinh khối thực vật Lúa (NDVI MODIS)": "ndvi",
            "Độ ẩm đất tầng rễ (SMAP L-band 0-100cm)": "sm_rootzone",
            "Vũ lượng mưa tích lũy tháng (GPM IMERG, mm)": "mua_mm",
            "Nhiệt độ bề mặt ban ngày (MODIS LST Day, °C)": "lst_c",
            "Số ngày nắng nóng Gió Lào (Tmax ≥ 35°C)": "nong35",
            "Chỉ số diện tích tán lá (LAI MODIS)": "lai",
            "Chỉ số thực vật nâng cao (EVI MODIS)": "evi",
            "Thâm hụt bốc thoát hơi nước (ESI)": "esi",
        }

        col_sel_cs, col_desc = st.columns([6, 6], gap="small")
        with col_sel_cs:
            ten_cs = st.selectbox(
                "Chỉ số vệ tinh cần đối chiếu:",
                options=list(chi_so_dict.keys()),
                index=0,
                key="sel_cs_matrix",
            )
            col_id = chi_so_dict[ten_cs]

        # Xây dựng bảng ma trận 9 năm x 12 tháng
        df_yt = dl[dl.huyen == vung]
        rows_m = []
        for y in sorted(years):
            df_y = df_yt[df_yt.year == y]
            r_data = {"Năm": f"Năm {y}"}
            for m in range(1, 13):
                sub_ym = df_y[df_y.month == m]
                if not sub_ym.empty and col_id in sub_ym.columns and pd.notna(sub_ym.iloc[0][col_id]):
                    val = float(sub_ym.iloc[0][col_id])
                    if col_id in ["ndvi", "evi", "lai", "esi"]:
                        r_data[f"T{m}"] = f"{val:.2f}"
                    elif col_id in ["sm_rootzone", "sm_surface"]:
                        r_data[f"T{m}"] = f"{val*100:.1f}%" if val <= 1.0 else f"{val:.1f}%"
                    elif col_id in ["mua_mm", "nong35"]:
                        r_data[f"T{m}"] = f"{val:.0f}"
                    else:
                        r_data[f"T{m}"] = f"{val:.1f}"
                else:
                    r_data[f"T{m}"] = "—"
            rows_m.append(r_data)

        st.dataframe(pd.DataFrame(rows_m), use_container_width=True, hide_index=True)
