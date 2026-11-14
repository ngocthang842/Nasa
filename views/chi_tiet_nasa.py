"""Các trang chuyên sâu theo từng chỉ số Viễn thám NASA (NDVI, SMAP, GPM, LST, Công thức, API).
Thiết kế theo chuẩn Hệ thống Phân tích Môi trường NASA (NEDA) & Vựa lúa Yên Thành (Nghệ An).
Tính năng mới:
- Bộ lọc Thời gian Thông minh: Cho phép chọn Năm (2024, 2025, 2026) & Tháng (T1–T12) để xem lại dữ liệu cũ/hiện tại
- Hàng 1: Bộ 3 Thẻ KPI, Đánh giá Nông học & Thang đo chuẩn quốc tế
- Hàng 2: Biểu đồ Chuyên sâu Toàn chiều rộng (Full-Width, Spline Area, Combo Dual-Axis, Bar Chart không đè chữ)
- Hàng 3: Bảng Ma trận Số liệu Viễn thám 12 Tháng đối chiếu Đa năm (2024–2026)
- Hàng 4: Bản đồ Viễn thám Không gian & Telemetry 4 Cụm Xã Thâm Canh (On-Demand)
"""
import calendar
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import engine as E
from views import du_lieu
from views.ve_tinh import hien_ve_tinh, CUM_XA_YEN_THANH
from views.chung import tieu_de, ve, kpi_the

# Icon chu kỳ nông học 12 tháng của lúa Yên Thành
ICON_THANG = {
    1: "🌱", 2: "🌿", 3: "🌾", 4: "🌸", 5: "✨",
    6: "🌱", 7: "🌿", 8: "🌾", 9: "🌊", 10: "🚜", 11: "☀️", 12: "💧"
}


# =============================================================================
# 0. BỘ ĐIỀU KHIỂN THỜI GIAN KHẢO SÁT VIỄN THÁM (NĂM, THÁNG & NGÀY TƯƠNG TÁC)
# =============================================================================

@st.cache_data(show_spinner=False)
def _tai_daily_power():
    """Tải chuỗi dữ liệu thời tiết & viễn thám từng ngày huyện Yên Thành (2018–2026)."""
    p = "data/raw/power/power_Yen_Thanh.csv"
    try:
        df = pd.read_csv(p)
        df["date_dt"] = pd.to_datetime(df["date"])
        df = df.dropna(subset=["T2M_MAX"])
        return df
    except Exception:
        return pd.DataFrame()


def _thanh_dieu_khien_thoi_gian(ctx, cot_id):
    """Thanh điều khiển chọn Ngày Khảo sát Viễn thám trực tiếp (DD/MM/YYYY).
    Tự động xác định Năm & Tháng, hiển thị telemetry tức thời, loại bỏ hoàn toàn selectbox Năm và danh sách Tháng."""
    key_nam = f"filter_nam_{cot_id}"
    key_thang = f"filter_thang_{cot_id}"
    key_date = f"filter_date_{cot_id}"
    key_chuyen_ngay = f"chuyen_ngay_{cot_id}"

    # Xử lý chuyển ngày an toàn từ các nút bấm lối tắt (Safe Deferred State Transition)
    if key_chuyen_ngay in st.session_state and st.session_state[key_chuyen_ngay]:
        st.session_state[key_date] = st.session_state.pop(key_chuyen_ngay)

    df_daily = _tai_daily_power()
    if not df_daily.empty:
        min_date = df_daily["date_dt"].dt.date.min()
        max_date = df_daily["date_dt"].dt.date.max()
    else:
        min_date = datetime.date(2018, 1, 1)
        max_date = datetime.date(2026, 11, 15)

    if key_date not in st.session_state or not isinstance(st.session_state[key_date], datetime.date):
        st.session_state[key_date] = datetime.date(2026, 4, 15)

    with st.container(border=True):
        col_d_box, col_event_box = st.columns([3.8, 8.2], gap="small")

        with col_d_box:
            st.markdown(
                '<div style="font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;">'
                '📆 Chọn Ngày Khảo Sát Viễn Thám (2018–2026):'
                '</div>',
                unsafe_allow_html=True,
            )
            ngay_chon = st.date_input(
                "Ngày khảo sát:",
                value=st.session_state[key_date],
                min_value=min_date,
                max_value=max_date,
                key=f"widget_{key_date}",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )
            if ngay_chon and ngay_chon != st.session_state[key_date]:
                st.session_state[key_date] = ngay_chon
                st.session_state[key_nam] = ngay_chon.year
                st.session_state[key_thang] = ngay_chon.month
                st.rerun()

        with col_event_box:
            st.markdown(
                '<div style="font-size:11.5px; font-weight:750; color:#475569; margin-bottom:4px;">'
                '⚡ Lối Tắt Mốc Nông Học & Khí Tượng Cực Đoan:'
                '</div>',
                unsafe_allow_html=True,
            )
            col_b1, col_b2, col_b3, col_b4 = st.columns(4, gap="small")
            with col_b1:
                if st.button("🌸 Trỗ xuân (15/04/2026)", key=f"btn_xuan_{cot_id}", use_container_width=True, help="Khảo sát giai đoạn lúa xuân trỗ bông"):
                    st.session_state[key_chuyen_ngay] = datetime.date(2026, 4, 15)
                    st.rerun()
            with col_b2:
                if st.button("🌾 Gặt hè thu (10/09/2026)", key=f"btn_hethu_{cot_id}", use_container_width=True, help="Khảo sát gặt né lũ lụt hè thu"):
                    st.session_state[key_chuyen_ngay] = datetime.date(2026, 9, 10)
                    st.rerun()
            with col_b3:
                if st.button("🔥 Hạn 2019 (22/06/2019)", key=f"btn_han_{cot_id}", use_container_width=True, help="Khảo sát đợt hạn gió Lào kỷ lục"):
                    st.session_state[key_chuyen_ngay] = datetime.date(2019, 6, 22)
                    st.rerun()
            with col_b4:
                if st.button("🌊 Lũ 2020 (19/10/2020)", key=f"btn_lu_{cot_id}", use_container_width=True, help="Khảo sát đỉnh lũ lụt lịch sử Kênh Vách Bắc"):
                    st.session_state[key_chuyen_ngay] = datetime.date(2020, 10, 19)
                    st.rerun()

        cur_date = st.session_state[key_date]
        cur_nam = cur_date.year
        cur_thang = cur_date.month
        st.session_state[key_nam] = cur_nam
        st.session_state[key_thang] = cur_thang

        # Phân loại vụ mùa
        if cur_thang <= 5:
            vu_str = "🌾 Vụ Chiêm Xuân (Vụ chính)"
        elif cur_thang <= 9:
            vu_str = "☀️ Vụ Hè Thu (Chạy lũ & chống hạn)"
        else:
            vu_str = "🚜 Vụ Đông / Cày phơi ải đất"

        # Trích xuất số liệu telemetry thực đo ngày
        tele_str = ""
        if not df_daily.empty:
            r_day = df_daily[df_daily["date_dt"].dt.date == cur_date]
            if not r_day.empty:
                r0 = r_day.iloc[0]
                tmax_d = float(r0.get("T2M_MAX", 0))
                tmin_d = float(r0.get("T2M_MIN", 0))
                mua_d = float(r0.get("PRECTOTCORR", 0)) if pd.notna(r0.get("PRECTOTCORR")) else 0.0
                rh_d = float(r0.get("RH2M", 70)) if pd.notna(r0.get("RH2M")) else 70.0
                rad_d = float(r0.get("ALLSKY_SFC_SW_DWN", 15)) if pd.notna(r0.get("ALLSKY_SFC_SW_DWN")) else 15.0
                tele_str = (
                    f'<span style="color:#0F172A; font-weight:700;">Tmax:</span> <b style="color:#DC2626;">{tmax_d:.1f}°C</b> · '
                    f'<span style="color:#0F172A; font-weight:700;">Tmin:</span> <b style="color:#0284C7;">{tmin_d:.1f}°C</b> · '
                    f'<span style="color:#0F172A; font-weight:700;">Mưa:</span> <b style="color:#0284C7;">{mua_d:.1f} mm</b> · '
                    f'<span style="color:#0F172A; font-weight:700;">Ẩm RH:</span> <b style="color:#16A34A;">{rh_d:.0f}%</b> · '
                    f'<span style="color:#0F172A; font-weight:700;">Bức xạ:</span> <b style="color:#D97706;">{rad_d:.1f} MJ/m²</b>'
                )

        tag_nam = "(Kế hoạch sản xuất)" if cur_nam == 2026 else f"(Dữ liệu lịch sử {cur_nam})"
        tele_html = f'<div style="color:#334155; font-size:11.5px;">🛰️ <b>Telemetry Ngày {cur_date.strftime("%d/%m/%Y")}:</b> {tele_str}</div>' if tele_str else ''

        st.markdown(
            f'<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:6px 12px; margin-top:4px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; font-size:11.5px; gap:8px;">'
            f'  <div>📌 Đang khảo sát: <b style="color:#0F766E; font-size:12.5px;">Ngày {cur_date.strftime("%d/%m/%Y")}</b> (Tháng {cur_thang}/{cur_nam}) {tag_nam} · <b style="color:#0F172A;">{vu_str}</b></div>'
            f'  {tele_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    return cur_nam, cur_thang


# =============================================================================
# 1. CÁC HÀM VẼ BIỂU ĐỒ CHUYÊN SÂU NÂNG CAO (FULL-WIDTH, KHÔNG ĐÈ CHỮ)
# =============================================================================

def _ve_bieu_do_spline_area(
    df_thang,
    cot,
    mau_chinh,
    mau_fill,
    don_vi,
    thang_hien_tai=4,
    nam_hien_tai=2026,
    nguong_an_toan=None,
    vach_canh_bao=None,
    he_so=1.0,
):
    """Vẽ biểu đồ Spline Area Chart mềm mại cho NDVI và SMAP, CHỈ HIỆN ĐƯỜNG DỮ LIỆU CỦA NĂM ĐÃ CHỌN."""
    fig = go.Figure()

    # Dải ngưỡng sinh trưởng an toàn
    if nguong_an_toan:
        min_v, max_v, nhan_v = nguong_an_toan
        fig.add_hrect(
            y0=min_v,
            y1=max_v,
            fillcolor="rgba(34, 197, 94, 0.08)",
            line=dict(width=1, dash="dash", color="rgba(34, 197, 94, 0.35)"),
            annotation_text=f"🌿 {nhan_v}",
            annotation_position="top left",
            annotation_font=dict(size=11, color="#15803D"),
        )

    # Vạch cảnh báo rủi ro
    if vach_canh_bao:
        for vb in vach_canh_bao:
            fig.add_hline(
                y=vb["val"],
                line=dict(color=vb.get("color", "#DC2626"), width=1.5, dash="dashdot"),
                annotation_text=vb.get("label", ""),
                annotation_position="bottom right",
                annotation_font=dict(size=10.5, color=vb.get("color", "#DC2626")),
            )

    # CHỈ VẼ ĐƯỜNG DỮ LIỆU CỦA NĂM ĐANG CHỌN (Không vẽ các năm khác theo yêu cầu người dùng)
    sub = df_thang[df_thang.year == nam_hien_tai].sort_values("month")
    if not sub.empty and cot in sub.columns:
        y_data = sub[cot] * he_so
        x_data = [f"T{int(m)}" for m in sub.month]
        tag_ke_hoach = " (Kế hoạch)" if nam_hien_tai == 2026 else ""

        fig.add_scatter(
            x=x_data,
            y=y_data,
            name=f"🌟 Năm {nam_hien_tai}{tag_ke_hoach}",
            mode="lines+markers",
            line=dict(shape="spline", smoothing=1.2, width=3.8, color=mau_chinh, dash="solid"),
            fill="tozeroy",
            fillcolor=mau_fill,
            marker=dict(size=9, symbol="circle", color=mau_chinh),
            hovertemplate=f"<b>Năm {nam_hien_tai} · %{{x}}</b>: %{{y:.2f}} {don_vi}<extra></extra>",
        )

    # Đánh dấu tháng hiện tại
    x_cur = f"T{int(thang_hien_tai)}"
    fig.add_shape(
        type="line",
        x0=x_cur,
        x1=x_cur,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#0F172A", width=1.6, dash="dot"),
    )
    fig.add_annotation(
        x=x_cur,
        y=1.02,
        yref="paper",
        text=f"T{int(thang_hien_tai)} (Đang xem)",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=10.5, color="#0F172A", weight="bold"),
        bgcolor="rgba(255, 255, 255, 0.9)",
    )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        legend=dict(
            orientation="h",
            y=1.12,
            x=1,
            xanchor="right",
            font=dict(size=11, family="Be Vietnam Pro"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#E2E8F0",
            borderwidth=1,
        ),
        xaxis=dict(
            title="",
            tickfont=dict(size=12, color="#0F172A", weight="bold", family="Be Vietnam Pro"),
            showgrid=True,
            gridcolor="#F1F5F9",
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text=don_vi, font=dict(size=12, color="#475569", family="Be Vietnam Pro")),
            tickfont=dict(size=11, color="#64748B", family="Be Vietnam Pro"),
            showgrid=True,
            gridcolor="#F1F5F9",
            fixedrange=True,
        ),
        hovermode="x unified",
    )
    return fig


def _ve_bieu_do_mua_bar(df_thang, thang_hien_tai=4, nam_hien_tai=2026):
    """Vẽ biểu đồ Vũ lượng Mưa GPM IMERG dạng CỘT (Bar Chart) CHỈ CHO NĂM ĐÃ CHỌN."""
    fig = go.Figure()

    # Dải mưa an toàn cho lúa
    fig.add_hrect(
        y0=50.0,
        y1=180.0,
        fillcolor="rgba(34, 197, 94, 0.08)",
        line=dict(width=1, dash="dash", color="rgba(34, 197, 94, 0.35)"),
        annotation_text="🌿 Vũ lượng thích hợp vụ lúa (50–180 mm)",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#15803D"),
    )

    # Vạch báo động bão lũ
    fig.add_hline(
        y=250.0,
        line=dict(color="#DC2626", width=1.6, dash="dashdot"),
        annotation_text="🚨 Ngưỡng báo động ngập úng Kênh Vách Bắc (≥250 mm)",
        annotation_position="bottom right",
        annotation_font=dict(size=10.5, color="#DC2626"),
    )

    # Lấy dữ liệu Năm đang chọn vẽ Bar Chart (Không vẽ các năm khác theo yêu cầu người dùng)
    sub_sel = df_thang[df_thang.year == nam_hien_tai].sort_values("month")
    if not sub_sel.empty and "mua_mm" in sub_sel.columns:
        x_bar = [f"T{int(m)}" for m in sub_sel.month]
        y_bar = sub_sel["mua_mm"].values

        # Đổi màu cột bão lũ (≥250mm) sang đỏ cam
        bar_colors = ["#DC2626" if v >= 250 else ("#0284C7" if m == thang_hien_tai else "#38BDF8") for m, v in zip(sub_sel.month, y_bar)]

        fig.add_bar(
            x=x_bar,
            y=y_bar,
            name=f"Vũ lượng Năm {nam_hien_tai}",
            marker=dict(color=bar_colors, line=dict(color="#0284C7", width=1)),
            hovertemplate=f"<b>Năm {nam_hien_tai} · %{{x}}</b>: %{{y:.0f}} mm<extra></extra>",
        )

    # Đánh dấu tháng hiện tại
    x_cur = f"T{int(thang_hien_tai)}"
    fig.add_shape(
        type="line",
        x0=x_cur,
        x1=x_cur,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#0F172A", width=1.6, dash="dot"),
    )
    fig.add_annotation(
        x=x_cur,
        y=1.02,
        yref="paper",
        text=f"T{int(thang_hien_tai)} (Đang xem)",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=10.5, color="#0F172A", weight="bold"),
        bgcolor="rgba(255, 255, 255, 0.9)",
    )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        legend=dict(
            orientation="h",
            y=1.12,
            x=1,
            xanchor="right",
            font=dict(size=11, family="Be Vietnam Pro"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#E2E8F0",
            borderwidth=1,
        ),
        xaxis=dict(
            title="",
            tickfont=dict(size=12, color="#0F172A", weight="bold", family="Be Vietnam Pro"),
            showgrid=True,
            gridcolor="#F1F5F9",
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="Lượng mưa (mm)", font=dict(size=12, color="#475569", family="Be Vietnam Pro")),
            tickfont=dict(size=11, color="#64748B", family="Be Vietnam Pro"),
            showgrid=True,
            gridcolor="#F1F5F9",
            fixedrange=True,
        ),
    )
    return fig


def _ve_bieu_do_nhiet_combo(df_thang, thang_hien_tai=4, nam_hien_tai=2026):
    """Vẽ biểu đồ COMBO 2 TRỤC Y CHỈ CHO NĂM ĐÃ CHỌN: Đường Tmax (°C) + Cột Số ngày Gió Lào."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Vạch cảnh báo gió Lào táp bông lúa ≥35°C
    fig.add_hline(
        y=35.0,
        line=dict(color="#DC2626", width=1.6, dash="dashdot"),
        annotation_text="🔥 Ngưỡng Gió Lào táp phấn hoa lúa (≥35°C)",
        annotation_position="bottom right",
        annotation_font=dict(size=10.5, color="#DC2626"),
        secondary_y=False,
    )

    # 1. Cột Số ngày Gió Lào (Trục Y phụ - phải) cho Năm đang chọn
    sub_sel = df_thang[df_thang.year == nam_hien_tai].sort_values("month")
    if not sub_sel.empty and "nong35" in sub_sel.columns:
        fig.add_bar(
            x=[f"T{int(m)}" for m in sub_sel.month],
            y=sub_sel["nong35"],
            name=f"Gió Lào ≥35°C ({nam_hien_tai})",
            marker=dict(color="rgba(251, 146, 60, 0.45)", line=dict(color="#EA580C", width=1)),
            secondary_y=True,
            hovertemplate=f"<b>Năm {nam_hien_tai} · %{{x}}</b>: %{{y:.0f}} ngày gió Lào<extra></extra>",
        )

    # 2. Đường Nhiệt độ Tmax của Năm đang chọn (Trục Y chính - trái) (Không vẽ các năm khác theo yêu cầu người dùng)
    if not sub_sel.empty and "tmax" in sub_sel.columns:
        fig.add_scatter(
            x=[f"T{int(m)}" for m in sub_sel.month],
            y=sub_sel["tmax"],
            name=f"🌟 Tmax {nam_hien_tai}",
            mode="lines+markers",
            line=dict(shape="spline", smoothing=1.2, width=3.8, color="#EA580C"),
            marker=dict(size=9, color="#EA580C"),
            secondary_y=False,
            hovertemplate=f"<b>Nhiệt Tmax {nam_hien_tai} · %{{x}}</b>: %{{y:.1f}}°C<extra></extra>",
        )

    # Đánh dấu tháng hiện tại
    x_cur = f"T{int(thang_hien_tai)}"
    fig.add_shape(
        type="line",
        x0=x_cur,
        x1=x_cur,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#0F172A", width=1.6, dash="dot"),
    )
    fig.add_annotation(
        x=x_cur,
        y=1.02,
        yref="paper",
        text=f"T{int(thang_hien_tai)} (Đang xem)",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=10.5, color="#0F172A", weight="bold"),
        bgcolor="rgba(255, 255, 255, 0.9)",
    )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        legend=dict(
            orientation="h",
            y=1.12,
            x=1,
            xanchor="right",
            font=dict(size=11, family="Be Vietnam Pro"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#E2E8F0",
            borderwidth=1,
        ),
        xaxis=dict(
            title="",
            tickfont=dict(size=12, color="#0F172A", weight="bold", family="Be Vietnam Pro"),
            showgrid=True,
            gridcolor="#F1F5F9",
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="Nhiệt độ Tmax (°C)", font=dict(size=12, color="#EA580C", family="Be Vietnam Pro")),
            tickfont=dict(size=11, color="#EA580C", family="Be Vietnam Pro"),
            showgrid=True,
            gridcolor="#F1F5F9",
            fixedrange=True,
        ),
        yaxis2=dict(
            title=dict(text="Số ngày Gió Lào (ngày)", font=dict(size=12, color="#D97706", family="Be Vietnam Pro")),
            tickfont=dict(size=11, color="#D97706", family="Be Vietnam Pro"),
            showgrid=False,
            overlaying="y",
            side="right",
            fixedrange=True,
        ),
    )
    return fig


# =============================================================================
# 2. HÀM RENDER BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
# =============================================================================

def _hien_bang_ma_tran_12_thang(
    df_thang,
    cot,
    don_vi,
    he_so=1.0,
    thang_hien_tai=4,
    nam_hien_tai=2026,
    format_str="{:.1f}",
    danh_gia_fn=None,
):
    """Tạo bảng ma trận HTML đối chiếu 12 tháng qua các năm (2024, 2025, 2026),
    highlight tháng hiện tại và kèm đánh giá nông học trực quan."""
    years = sorted(df_thang.year.unique())
    all_months = list(range(1, 13))

    data_dict = {}
    for y in years:
        sub = df_thang[df_thang.year == y].set_index("month")
        row = []
        for m in all_months:
            if m in sub.index and cot in sub.columns:
                val = float(sub.loc[m, cot]) * he_so
                row.append(val)
            else:
                row.append(np.nan)
        data_dict[y] = row

    th_cols = "".join(
        f'<th style="padding:6px 4px; text-align:center; font-size:11px; background:{"#0F766E; color:#FFFFFF;" if m == thang_hien_tai else "#F8FAFC; color:#475569;"} border-bottom:2px solid #CBD5E1;">'
        f'T{m}{" ⭐" if m == thang_hien_tai else ""}'
        f'</th>'
        for m in all_months
    )

    rows_html = ""
    for y in reversed(years):
        is_sel_yr = (y == nam_hien_tai)
        row_vals = data_dict.get(y, [])
        tds = ""
        for m, v in enumerate(row_vals, start=1):
            is_cur = (m == thang_hien_tai)
            if is_sel_yr and is_cur:
                bg = "#CCFBF1"  # Teal đậm hơn cho giao điểm Năm đang xem x Tháng đang xem
                fw = "850"
                color = "#0F766E"
            elif is_cur:
                bg = "#ECFDF5"
                fw = "800"
                color = "#0F766E"
            elif is_sel_yr:
                bg = "#F0FDFA"
                fw = "750"
                color = "#0F172A"
            else:
                bg = "#FFFFFF" if y == 2026 else "#F8FAFC"
                fw = "500"
                color = "#64748B"

            v_str = format_str.format(v) if not np.isnan(v) else "—"
            tds += f'<td style="padding:7px 4px; text-align:center; font-size:11.5px; font-weight:{fw}; color:{color}; background:{bg}; border-bottom:1px solid #E2E8F0;">{v_str}</td>'

        tb_nam = np.nanmean(row_vals) if len(row_vals) else np.nan
        tb_str = format_str.format(tb_nam) if not np.isnan(tb_nam) else "—"
        td_tb = f'<td style="padding:7px 6px; text-align:center; font-size:11.5px; font-weight:800; color:#0F172A; background:#F1F5F9; border-bottom:1px solid #E2E8F0;">{tb_str}</td>'

        nhan_nam = f"<b>Năm {y}</b> {'⭐ (Đang xem)' if is_sel_yr else ('(Kế hoạch)' if y == 2026 else '')}"
        bg_row_header = "#CCFBF1" if is_sel_yr else "#F8FAFC"
        rows_html += f'<tr><td style="padding:7px 8px; font-size:11.5px; color:#1E293B; background:{bg_row_header}; border-bottom:1px solid #E2E8F0;">{nhan_nam}</td>{tds}{td_tb}</tr>'

    # Hàng đánh giá nông học cho Năm đang chọn
    row_danh_gia = ""
    if danh_gia_fn and nam_hien_tai in data_dict:
        td_dg = ""
        vals_sel = data_dict[nam_hien_tai]
        for m, v in enumerate(vals_sel, start=1):
            is_cur = (m == thang_hien_tai)
            if not np.isnan(v):
                badge_text, badge_bg, badge_col = danh_gia_fn(v, m)
            else:
                badge_text, badge_bg, badge_col = "—", "#F1F5F9", "#64748B"
            bg = "#ECFDF5" if is_cur else "#FFFFFF"
            td_dg += (
                f'<td style="padding:5px 2px; text-align:center; background:{bg}; border-bottom:1px solid #E2E8F0;">'
                f'<span style="background:{badge_bg}; color:{badge_col}; padding:2px 4px; border-radius:4px; font-size:9.5px; font-weight:750; white-space:nowrap;">'
                f'{badge_text}'
                f'</span></td>'
            )
        row_danh_gia = f'<tr><td style="padding:6px 8px; font-size:11px; font-weight:750; color:#475569; background:#F8FAFC; border-bottom:1px solid #E2E8F0;">Đánh giá Vụ Năm {nam_hien_tai}</td>{td_dg}<td style="background:#F1F5F9; border-bottom:1px solid #E2E8F0;"></td></tr>'

    html_table = f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; overflow-x:auto; margin-top:12px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
      <div style="padding:10px 14px; border-bottom:1px solid #E2E8F0; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:13px; font-weight:800; color:#0F172A;">
          📋 Bảng Ma trận Số liệu Viễn thám 12 Tháng ({don_vi}) · Đối chiếu Đa năm Yên Thành
        </div>
        <div style="font-size:11px; color:#0F766E; font-weight:700;">
          ⭐ Cột Tháng {thang_hien_tai} / Năm {nam_hien_tai} đang được chọn khảo sát
        </div>
      </div>
      <table style="width:100%; border-collapse:collapse; min-width:680px;">
        <thead>
          <tr>
            <th style="padding:6px 8px; text-align:left; font-size:11px; color:#475569; background:#F8FAFC; border-bottom:2px solid #CBD5E1;">Chỉ số / Tháng</th>
            {th_cols}
            <th style="padding:6px 6px; text-align:center; font-size:11px; color:#0F172A; background:#F1F5F9; border-bottom:2px solid #CBD5E1;">TB Năm</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
          {row_danh_gia}
        </tbody>
      </table>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)


# =============================================================================
# 3. HÀM HIỂN THỊ KHU VỰC BẢN ĐỒ VỆ TINH THEO YÊU CẦU (ON-DEMAND INTERACTIVE)
# =============================================================================

def _hien_khu_vuc_ban_do_ve_tinh(ctx, cot_id, ten_lop, ten_chi_so, icon_lop, nam=2026, thang=4):
    """Khu vực tương tác Bản đồ Viễn thám & Telemetry 4 Cụm Xã theo Năm và Tháng đã chọn."""
    session_key = f"hien_ban_do_{cot_id}_{nam}_{thang}"

    if session_key not in st.session_state:
        st.session_state[session_key] = False

    dang_mo = st.session_state[session_key]

    with st.container(border=True):
        col_hdr, col_btn = st.columns([7.5, 2.5], gap="medium")
        with col_hdr:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-size:20px;">{icon_lop}</span>
                  <div>
                    <div style="font-size:13.5px; font-weight:800; color:#0F172A;">
                      Bản đồ Viễn thám Không gian Vệ tinh & Telemetry 4 Cụm Xã Thâm Canh
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-top:1px;">
                      Giám sát không gian thực địa tại Cụm Bắc (Đô Thành), Lòng chảo, Cụm Nam (Bảo Thành) và Cụm Tây (Mỹ Thành) · <b>Tháng {thang}/{nam}</b>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_btn:
            nhan_nut = "✖️ Thu gọn Bản đồ" if dang_mo else "🛰️ Xem Chi tiết trên Bản đồ"
            kieu_nut = "secondary" if dang_mo else "primary"
            if st.button(nhan_nut, key=f"btn_toggle_{session_key}", type=kieu_nut, use_container_width=True):
                st.session_state[session_key] = not dang_mo
                st.rerun()

        if st.session_state[session_key]:
            st.markdown(
                f'<div style="font-size:12px; font-weight:700; color:#0284C7; margin:8px 0 4px 0;">'
                f'🛰️ Đang hiển thị bản đồ viễn thám lớp: <b>{ten_lop}</b> · Tháng {thang}/{nam}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Bản đồ vệ tinh Folium cập nhật theo Năm và Tháng đã chọn
            ctx_sub = dict(ctx)
            ctx_sub["nam"] = nam
            ctx_sub["thang"] = thang
            ctx_sub["lop_hien_tai"] = ten_lop
            hien_ve_tinh(ctx_sub)

            # Telemetry 4 cụm xã dạng grid cards
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-size:12.5px; font-weight:800; color:#0F172A; margin-bottom:6px;">'
                f'📡 Telemetry Quan trắc Viễn thám tại 4 Trạm Cụm Xã Yên Thành (Tháng {thang}/{nam}):'
                f'</div>',
                unsafe_allow_html=True,
            )
            cols_cum = st.columns(4, gap="small")
            for i, c in enumerate(CUM_XA_YEN_THANH):
                with cols_cum[i]:
                    st.markdown(
                        f"""
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-top:3px solid {c['mau_icon']}; border-radius:8px; padding:8px 10px; height:100%;">
                          <div style="font-size:12px; font-weight:800; color:#0F172A;">{c['icon']} {c['ten'].split('(')[0].strip()}</div>
                          <div style="font-size:10.5px; color:#64748B; margin-top:2px;">{c['giong']}</div>
                          <hr style="margin:5px 0; border-color:#E2E8F0;">
                          <div style="font-size:10px; color:#475569; line-height:1.3;">
                            <b>Mệnh lệnh:</b> {c['hanh_dong'][:75]}...
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            cols_preview = st.columns(4, gap="small")
            for i, c in enumerate(CUM_XA_YEN_THANH):
                with cols_preview[i]:
                    st.markdown(
                        f"""
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:3px solid {c['mau_icon']}; border-radius:6px; padding:6px 10px;">
                          <div style="font-size:11.5px; font-weight:800; color:#0F172A;">{c['icon']} {c['ten'].split('(')[0].strip()}</div>
                          <div style="font-size:10.5px; color:#64748B;">{c['vung'][:35]}...</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.caption(f"💡 Bấm nút **'🛰️ Xem Chi tiết trên Bản đồ'** ở góc phải để mở Bản đồ Vệ tinh GIS & Telemetry viễn thám Tháng {thang}/{nam}.")


# =============================================================================
# 1. 🍃 PHÂN TÍCH THẢM THỰC VẬT & SỨC KHỎE LÚA (NDVI)
# =============================================================================
def hien_ndvi(ctx):
    dl = ctx["dl"]
    vung = "Yên Thành"

    # 1. BỘ ĐIỀU KHIỂN THỜI GIAN KHẢO SÁT
    nam, thang = _thanh_dieu_khien_thoi_gian(ctx, cot_id="ndvi")

    # 2. TIÊU ĐỀ
    tieu_de(vung, thang, nam, "Phân tích Thảm Thực vật & Sức khỏe Lúa (NDVI MODIS)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_ndvi = float(r_thang["ndvi"].iloc[0]) if not r_thang.empty and "ndvi" in r_thang.columns else 0.65

    # Đánh giá giai đoạn lúa theo tháng
    giai_doan_dict = {
        1:  ("🌱 Mạ non & Cấy lúa Xuân",           "NDVI thấp (0.2–0.3), ruộng ngập nước mạ mới bén rễ."),
        2:  ("🌿 Đẻ nhánh rộ",                      "NDVI tăng nhanh (0.45–0.60), sinh khối lá phát triển mạnh."),
        3:  ("🌾 Làm đòng & Ôm bòng",               "NDVI đạt đỉnh cao (0.70–0.85), thảm lá xanh kín mặt ruộng."),
        4:  ("🌸 Trỗ bông rộ",                       "NDVI duy trì mức cao (0.65–0.78), lúa thụ phấn vào hạt mẩy."),
        5:  ("✨ Chín vàng & Thu hoạch",             "NDVI giảm (0.35–0.50) do lá vàng rực và gặt rơm rạ."),
        6:  ("🌱 Xuống giống Hè Thu",                "NDVI thấp (0.2–0.35), gieo cấy chạy lũ tiểu mãn."),
        7:  ("🌿 Đẻ nhánh Hè Thu",                  "NDVI tăng (0.50–0.65), vượt đỉnh nắng nóng gió Lào."),
        8:  ("🌾 Làm đòng & Trỗ Hè Thu",            "NDVI đạt 0.70–0.80 trước khi bão lũ đổ bộ."),
        9:  ("🌊 Gặt né lũ & Mưa ngập Kênh Vách Bắc", "NDVI giảm nhanh sau khi gặt chạy lũ."),
        10: ("🚜 Cày ải đất & Rau màu vụ đông",     "NDVI vùng lúa thấp (0.25), vùng cày ải đất phơi nỏ."),
        11: ("☀️ Phơi nỏ ruộng vụ đông",            "Đất khô ải diệt mầm bệnh, tích tụ dinh dưỡng."),
        12: ("💧 Lấy nước đổ ải vụ xuân",           "Ruộng đầy nước phù sa Ba Ra Đô Lương dẫn về."),
    }
    gd_ten, gd_mota = giai_doan_dict.get(thang, ("Giai đoạn sinh trưởng lúa", "Giám sát viễn thám"))

    # HÀNG 1: BỘ 3 THẺ KPI, GIAI ĐOẠN & THANG ĐO
    c1, c2, c3 = st.columns([3.4, 4.4, 4.2], gap="small")
    with c1, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">CHỈ SỐ NDVI MODIS</div>
            <div style="font-size:34px; font-weight:800; color:#16A34A; line-height:1.1; margin:2px 0;">{cur_ndvi:.2f}</div>
            <div style="font-size:12px; color:#475569;"><b>Tháng {thang}/{nam}</b> · Vựa lúa Yên Thành</div>
            <div style="font-size:11px; color:#15803D; font-weight:700; margin-top:4px;">
              {'🟢 Sinh khối lá đạt chuẩn tối hảo' if cur_ndvi >= 0.65 else '🟡 Sinh khối trung bình'}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">CHU KỲ SINH TRƯỞNG LÚA</div>
            <div style="font-size:16px; font-weight:800; color:#0F172A; margin:3px 0;">{gd_ten}</div>
            <div style="font-size:11.5px; color:#475569; line-height:1.35;">{gd_mota}</div>
            """,
            unsafe_allow_html=True,
        )

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase; margin-bottom:4px;">QUY CHUẨN SINH KHỐI NDVI</div>
            <div style="display:flex; flex-direction:column; gap:4px; font-size:11px;">
              <div style="background:#F0FDF4; border-left:3.5px solid #16A34A; padding:3px 8px; border-radius:4px;">
                <b>🟢 NDVI ≥ 0.65:</b> Trỗ đều, sinh khối khỏe, phủ kín mặt ruộng.
              </div>
              <div style="background:#FEFCE8; border-left:3.5px solid #EAB308; padding:3px 8px; border-radius:4px;">
                <b>🟡 NDVI 0.40–0.65:</b> Giai đoạn mạ non hoặc lúa bắt đầu chín hạt.
              </div>
              <div style="background:#FEF2F2; border-left:3.5px solid #EF4444; padding:3px 8px; border-radius:4px;">
                <b>🔴 NDVI < 0.40:</b> Đất phơi ải, ngập úng hoặc bị táp lá do gió Lào.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BIỂU ĐỒ SPLINE AREA TOÀN CHIỀU RỘNG (FULL WIDTH)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <div style="font-size:13.5px; font-weight:800; color:#0F172A;">
                📈 Chuỗi Thời Gian 12 Tháng Chỉ Số NDVI MODIS — Năm {nam}
              </div>
              <div style="font-size:11px; color:#64748B;">Đường cong sinh học sinh khối tán lá lúa nước Yên Thành</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_ndvi = _ve_bieu_do_spline_area(
            dl_yt,
            cot="ndvi",
            mau_chinh="#16A34A",
            mau_fill="rgba(22, 163, 74, 0.08)",
            don_vi="NDVI",
            thang_hien_tai=thang,
            nam_hien_tai=nam,
            nguong_an_toan=(0.60, 0.85, "Dải sinh khối tối ưu (0.60–0.85)"),
            vach_canh_bao=[dict(val=0.40, label="Ngưỡng mạ non/đất ải (0.40)", color="#EAB308")],
        )
        ve(fig_ndvi, che_do="tuong_tac")

    # HÀNG 3: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
    def dg_ndvi(val, m):
        if val >= 0.65:
            return "🟢 Tối hảo", "#DCFCE7", "#15803D"
        elif val >= 0.45:
            return "🟡 Khá", "#FEF9C3", "#A16207"
        else:
            return "⚪ Mạ/Ải", "#F1F5F9", "#475569"

    _hien_bang_ma_tran_12_thang(
        dl_yt,
        cot="ndvi",
        don_vi="NDVI",
        he_so=1.0,
        thang_hien_tai=thang,
        nam_hien_tai=nam,
        format_str="{:.2f}",
        danh_gia_fn=dg_ndvi,
    )

    # HÀNG 4: BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="ndvi",
        ten_lop="🌿 Sức khỏe Lúa (NDVI)",
        ten_chi_so="NDVI MODIS",
        icon_lop="🌿",
        nam=nam,
        thang=thang,
    )


# =============================================================================
# 2. 💧 ĐỘ ẨM ĐẤT TẦNG RỄ (SMAP L-BAND)
# =============================================================================
def hien_do_am(ctx):
    dl = ctx["dl"]
    vung = "Yên Thành"

    # 1. BỘ ĐIỀU KHIỂN THỜI GIAN KHẢO SÁT
    nam, thang = _thanh_dieu_khien_thoi_gian(ctx, cot_id="smap")

    # 2. TIÊU ĐỀ
    tieu_de(vung, thang, nam, "Giám sát Độ Ẩm Đất & Cân bằng Nước Ruộng Lúa (SMAP L-band)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_sm = float(r_thang["sm_rootzone"].iloc[0] * 100) if not r_thang.empty and "sm_rootzone" in r_thang.columns else 28.0

    # HÀNG 1: BỘ 3 THẺ KPI, ĐÁNH GIÁ & THANG ĐO
    c1, c2, c3 = st.columns([3.4, 4.4, 4.2], gap="small")
    with c1, st.container(border=True):
        muc_am = "Đủ ẩm canh tác" if cur_sm >= 25 else "Thiếu ẩm cần tưới"
        col_am = "#0284C7" if cur_sm >= 25 else "#DC2626"
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">ĐỘ ẨM TẦNG RỄ (SMAP)</div>
            <div style="font-size:34px; font-weight:800; color:{col_am}; line-height:1.1; margin:2px 0;">{cur_sm:.1f}%</div>
            <div style="font-size:12px; color:#475569;"><b>Tháng {thang}/{nam}</b> · {muc_am}</div>
            <div style="font-size:11px; color:#0284C7; font-weight:700; margin-top:4px;">
              {'💧 Nước tưới ổn định từ Ba Ra' if cur_sm >= 25 else '⚠️ Cần dâng nước đệm chống hạn'}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">HỆ THỐNG THỦY NÔNG BA RA ĐÔ LƯƠNG</div>
            <div style="font-size:16px; font-weight:800; color:#0F172A; margin:3px 0;">Cấp nước 26.500 ha Lúa Yên Thành</div>
            <div style="font-size:11.5px; color:#475569; line-height:1.35;">
              Nước sông Lam chảy qua Kênh chính cấp ẩm tự chảy. Vùng trũng lòng chảo trữ nước tốt, vùng vàn cao cần trạm bơm dã chiến.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase; margin-bottom:4px;">TIÊU CHUẨN ĐỘ ẨM RUỘNG LÚA</div>
            <div style="display:flex; flex-direction:column; gap:4px; font-size:11px;">
              <div style="background:#EFF6FF; border-left:3.5px solid #0284C7; padding:3px 8px; border-radius:4px;">
                <b>🟢 25% – 35%:</b> Đủ ẩm tối hảo cho đẻ nhánh và ôm đòng.
              </div>
              <div style="background:#FFFBEB; border-left:3.5px solid #D97706; padding:3px 8px; border-radius:4px;">
                <b>🟡 20% – 25%:</b> Chớm thiếu ẩm, cần mở cống tưới luân phiên.
              </div>
              <div style="background:#FEF2F2; border-left:3.5px solid #EF4444; padding:3px 8px; border-radius:4px;">
                <b>🔴 < 20%:</b> Hạn kiệt nứt nẻ chân ruộng, nguy cơ táp lá cao.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BIỂU ĐỒ SPLINE AREA TOÀN CHIỀU RỘNG (FULL WIDTH)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <div style="font-size:13.5px; font-weight:800; color:#0F172A;">
                💧 Chuỗi 12 Tháng Độ Ẩm Đất Tầng Rễ SMAP — Năm {nam}
              </div>
              <div style="font-size:11px; color:#64748B;">Đo đạc viễn thám vi ba L-band NASA SMAP (0–100 cm)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_sm = _ve_bieu_do_spline_area(
            dl_yt,
            cot="sm_rootzone",
            mau_chinh="#0284C7",
            mau_fill="rgba(2, 132, 199, 0.08)",
            don_vi="%",
            thang_hien_tai=thang,
            nam_hien_tai=nam,
            nguong_an_toan=(25.0, 35.0, "Dải ẩm tối ưu ruộng lúa (25%–35%)"),
            vach_canh_bao=[dict(val=20.0, label="Ngưỡng hạn kiệt báo động (20%)", color="#DC2626")],
            he_so=100.0,
        )
        ve(fig_sm, che_do="tuong_tac")

    # HÀNG 3: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
    def dg_sm(val, m):
        if val >= 25.0:
            return "🟢 Đủ ẩm", "#DCFCE7", "#15803D"
        elif val >= 20.0:
            return "🟡 Thiếu nhẹ", "#FEF9C3", "#A16207"
        else:
            return "🔴 Hạn kiệt", "#FEE2E2", "#B91C1C"

    _hien_bang_ma_tran_12_thang(
        dl_yt,
        cot="sm_rootzone",
        don_vi="%",
        he_so=100.0,
        thang_hien_tai=thang,
        nam_hien_tai=nam,
        format_str="{:.1f}%",
        danh_gia_fn=dg_sm,
    )

    # HÀNG 4: BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="smap",
        ten_lop="💧 Độ ẩm Ruộng (SMAP)",
        ten_chi_so="SMAP L-band",
        icon_lop="💧",
        nam=nam,
        thang=thang,
    )


# =============================================================================
# 3. 🌧️ LƯỢNG MƯA TÍCH LŨY (NASA GPM IMERG)
# =============================================================================
def hien_luong_mua(ctx):
    dl = ctx["dl"]
    vung = "Yên Thành"

    # 1. BỘ ĐIỀU KHIỂN THỜI GIAN KHẢO SÁT
    nam, thang = _thanh_dieu_khien_thoi_gian(ctx, cot_id="gpm")

    # 2. TIÊU ĐỀ
    tieu_de(vung, thang, nam, "Giám sát Lượng Mưa Tích Lũy & Bão Lũ (NASA GPM IMERG)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_mua = float(r_thang["mua_mm"].iloc[0]) if not r_thang.empty and "mua_mm" in r_thang.columns else 85.0

    # HÀNG 1: BỘ 3 THẺ KPI, CẢNH BÁO & TIÊU ÚNG
    c1, c2, c3 = st.columns([3.4, 4.4, 4.2], gap="small")
    with c1, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">VŨ LƯỢNG THÁNG (GPM)</div>
            <div style="font-size:34px; font-weight:800; color:#0284C7; line-height:1.1; margin:2px 0;">{cur_mua:.0f} <span style="font-size:18px;">mm</span></div>
            <div style="font-size:12px; color:#475569;"><b>Tháng {thang}/{nam}</b> · Đo đạc NASA GPM IMERG</div>
            <div style="font-size:11px; color:#0284C7; font-weight:700; margin-top:4px;">
              {'🔴 Cảnh báo ngập úng' if cur_mua >= 250 else ('🟢 Lượng mưa thuận lợi' if cur_mua >= 60 else '🟡 Mùa khô ít mưa')}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">CẢNH BÁO BÃO LŨ & NÉ LŨ TIỂU MÃN</div>
            <div style="font-size:16px; font-weight:800; color:#0F172A; margin:3px 0;">Đỉnh Lũ Lớn Tập Trung Tháng 9–10</div>
            <div style="font-size:11.5px; color:#475569; line-height:1.35;">
              Vũ lượng tháng 9 thường vọt lên 350–550 mm. Cần gặt dứt điểm lúa hè thu trước ngày 15/9 để tránh ngập úng lòng chảo.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase; margin-bottom:4px;">NĂNG LỰC TIÊU ÚNG KÊNH VÁCH BẮC</div>
            <div style="display:flex; flex-direction:column; gap:4px; font-size:11px;">
              <div style="background:#F0FDF4; border-left:3.5px solid #16A34A; padding:3px 8px; border-radius:4px;">
                <b>Tháng 1–5 (Mùa khô):</b> Mưa thấp (40–120 mm), chủ yếu dùng nước tưới Ba Ra.
              </div>
              <div style="background:#FEF2F2; border-left:3.5px solid #EF4444; padding:3px 8px; border-radius:4px;">
                <b>Tháng 9–10 (Mùa lũ lớn):</b> Mở toàn bộ cống tiêu Kênh Vách Bắc thoát ra Diễn Châu.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BIỂU ĐỒ CỘT (BAR CHART) KẾT HỢP ĐƯỜNG XU HƯỚNG
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <div style="font-size:13.5px; font-weight:800; color:#0F172A;">
                🌧️ Biểu Đồ Vũ Lượng Mưa Tích Lũy 12 Tháng NASA GPM IMERG — Năm {nam}
              </div>
              <div style="font-size:11px; color:#64748B;">Cột màu đỏ cam cảnh báo tháng có nguy cơ bão lũ ngập úng (≥250 mm)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_mua = _ve_bieu_do_mua_bar(dl_yt, thang_hien_tai=thang, nam_hien_tai=nam)
        ve(fig_mua, che_do="tuong_tac")

    # HÀNG 3: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
    def dg_mua(val, m):
        if val >= 250.0:
            return "🔴 Mưa bão lũ", "#FEE2E2", "#B91C1C"
        elif val >= 60.0:
            return "🟢 Thuận lợi", "#DCFCE7", "#15803D"
        else:
            return "🟡 Mùa khô", "#FEF9C3", "#A16207"

    _hien_bang_ma_tran_12_thang(
        dl_yt,
        cot="mua_mm",
        don_vi="mm",
        he_so=1.0,
        thang_hien_tai=thang,
        nam_hien_tai=nam,
        format_str="{:.0f} mm",
        danh_gia_fn=dg_mua,
    )

    # HÀNG 4: BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="gpm",
        ten_lop="🌧️ Lượng mưa (GPM)",
        ten_chi_so="NASA GPM IMERG",
        icon_lop="🌧️",
        nam=nam,
        thang=thang,
    )


# =============================================================================
# 4. 🌡️ NHIỆT ĐỘ BỀ MẶT (LST & GIÓ LÀO TÂY NAM)
# =============================================================================
def hien_nhiet_do(ctx):
    dl = ctx["dl"]
    vung = "Yên Thành"

    # 1. BỘ ĐIỀU KHIỂN THỜI GIAN KHẢO SÁT
    nam, thang = _thanh_dieu_khien_thoi_gian(ctx, cot_id="lst")

    # 2. TIÊU ĐỀ
    tieu_de(vung, thang, nam, "Giám sát Nhiệt độ Bề mặt LST & Gió Lào Tây Nam (NASA POWER)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_tmax = float(r_thang["tmax"].iloc[0]) if not r_thang.empty and "tmax" in r_thang.columns else 32.5
    cur_nong = int(r_thang["nong35"].iloc[0]) if not r_thang.empty and "nong35" in r_thang.columns else 5

    # HÀNG 1: BỘ 3 THẺ KPI, NGUY CƠ & MỆNH LỆNH CHỐNG HẠN
    c1, c2, c3 = st.columns([3.4, 4.4, 4.2], gap="small")
    with c1, st.container(border=True):
        col_t = "#DC2626" if cur_tmax >= 35 else "#EA580C"
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">NHIỆT ĐỘ TMAX & GIÓ LÀO</div>
            <div style="font-size:34px; font-weight:800; color:{col_t}; line-height:1.1; margin:2px 0;">{cur_tmax:.1f}° <span style="font-size:18px;">C</span></div>
            <div style="font-size:12px; color:#DC2626; font-weight:700;">🔥 Có {cur_nong} ngày Gió Lào ≥35°C (Tháng {thang})</div>
            <div style="font-size:11px; color:#475569; margin-top:2px;">
              {'⚠️ Nguy cơ táp phấn bông lúa rất cao' if cur_tmax >= 35 else '🟢 Nhiệt độ trong ngưỡng kiểm soát'}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase;">HIỆU ỨNG PHƠN TÂY NAM (GIÓ LÀO)</div>
            <div style="font-size:16px; font-weight:800; color:#0F172A; margin:3px 0;">Đỉnh Nhiệt Gió Lào Tháng 5–7</div>
            <div style="font-size:11.5px; color:#475569; line-height:1.35;">
              Gió Lào vượt dãy Trường Sơn làm độ ẩm không khí tụt dưới 40%, bốc thoát hơi nước cực mạnh làm khô đầu lá và táp phấn lúa trỗ.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:11.5px; font-weight:750; color:#64748B; text-transform:uppercase; margin-bottom:4px;">MỆNH LỆNH NÔNG VỤ CHỐNG NÓNG</div>
            <div style="display:flex; flex-direction:column; gap:4px; font-size:11px;">
              <div style="background:#FFF7ED; border-left:3.5px solid #EA580C; padding:3px 8px; border-radius:4px;">
                <b>Dâng Nước Đệm 3–5 cm:</b> Giữ nước mặt ruộng điều hòa vi khí hậu gốc lúa.
              </div>
              <div style="background:#FEF2F2; border-left:3.5px solid #EF4444; padding:3px 8px; border-radius:4px;">
                <b>Không Phun Thuốc Buổi Trưa:</b> Tránh bốc hơi hóa chất và cháy lá non.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BIỂU ĐỒ COMBO DUAL-AXIS (ĐƯỜNG NHIỆT ĐỘ + CỘT NGÀY GIÓ LÀO)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <div style="font-size:13.5px; font-weight:800; color:#0F172A;">
                🌡️ Biểu Đồ Tương Quan: Nhiệt Độ Tmax & Tần Suất Gió Lào — Năm {nam}
              </div>
              <div style="font-size:11px; color:#64748B;">Trục trái: Nhiệt độ cực đại Tmax (°C) · Trục phải: Số ngày Gió Lào ≥35°C (ngày)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_tmax = _ve_bieu_do_nhiet_combo(dl_yt, thang_hien_tai=thang, nam_hien_tai=nam)
        ve(fig_tmax, che_do="tuong_tac")

    # HÀNG 3: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
    def dg_tmax(val, m):
        if val >= 35.0:
            return "🔴 Nắng nóng táp", "#FEE2E2", "#B91C1C"
        elif val >= 28.0:
            return "🟡 Nắng ấm", "#FEF9C3", "#A16207"
        elif val >= 18.0:
            return "🟢 Mát mẻ", "#DCFCE7", "#15803D"
        else:
            return "⚪ Rét đậm", "#EFF6FF", "#1D4ED8"

    _hien_bang_ma_tran_12_thang(
        dl_yt,
        cot="tmax",
        don_vi="°C",
        he_so=1.0,
        thang_hien_tai=thang,
        nam_hien_tai=nam,
        format_str="{:.1f}°C",
        danh_gia_fn=dg_tmax,
    )

    # HÀNG 4: BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="lst",
        ten_lop="🌡️ Nhiệt & Gió Lào",
        ten_chi_so="NASA POWER LST",
        icon_lop="🌡️",
        nam=nam,
        thang=thang,
    )


# =============================================================================
# 5. ƒx CÔNG THỨC & THUẬT TOÁN
# =============================================================================
def hien_cong_thuc_thuat_toan(ctx):
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Công thức Viễn thám & Thuật toán Ra Quyết định Mùa Vụ", False)

    tab_ct, = st.tabs([
        "🧮 Bảng Công thức Viễn thám NASA",
    ])

    with tab_ct:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:12px;">
                  🔬 Các Công Thức Toán Học & Vật Lý Viễn Thám Cốt Lõi Được Tích Hợp:
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2, gap="medium")
            with c1:
                st.markdown(
                    """
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px; margin-bottom:12px;">
                      <div style="font-size:13px; font-weight:800; color:#16A34A;">1. Chỉ số Khác biệt Thực vật Chuẩn hóa (NDVI)</div>
                      <div style="font-size:14px; margin:8px 0; color:#0F172A; font-family:monospace; background:#FFFFFF; padding:6px 10px; border-radius:6px; border:1px solid #CBD5E1;">
                        $$NDVI = \\frac{NIR - RED}{NIR + RED}$$
                      </div>
                      <div style="font-size:11.5px; color:#475569;">
                        <b>Đặc tả:</b> Cảm biến MODIS (Kênh NIR 841–876nm, RED 620–670nm). Đo khả năng hấp thụ quang hợp của diệp lục và tán lá lúa nước Yên Thành.
                      </div>
                    </div>

                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px;">
                      <div style="font-size:13px; font-weight:800; color:#0284C7;">2. Cán cân Nước & Bốc thoát hơi ẩm ròng (Water Balance)</div>
                      <div style="font-size:14px; margin:8px 0; color:#0F172A; font-family:monospace; background:#FFFFFF; padding:6px 10px; border-radius:6px; border:1px solid #CBD5E1;">
                        $$W_{net} = P_{GPM} - ET_0$$
                      </div>
                      <div style="font-size:11.5px; color:#475569;">
                        <b>Đặc tả:</b> Hiệu số giữa lượng mưa tích lũy GPM IMERG và bốc thoát hơi tiềm năng theo mô hình Penman-Monteith (FAO-56), xác định lượng nước cần bù đắp từ Ba Ra Đô Lương.
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    """
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px; margin-bottom:12px;">
                      <div style="font-size:13px; font-weight:800; color:#EA580C;">3. Nhiệt độ Bề mặt Đất & Không khí (LST)</div>
                      <div style="font-size:14px; margin:8px 0; color:#0F172A; font-family:monospace; background:#FFFFFF; padding:6px 10px; border-radius:6px; border:1px solid #CBD5E1;">
                        $$LST = \\frac{T_B}{1 + (\\lambda \\cdot T_B / \\rho) \\cdot \\ln(\\epsilon)}$$
                      </div>
                      <div style="font-size:11.5px; color:#475569;">
                        <b>Đặc tả:</b> Tính toán từ cảm biến nhiệt TIRS Landsat và chuỗi NASA POWER. Nhận diện các đợt nhiệt cực đại $T_{max} \\ge 35^\\circ\\text{C}$ do hiệu ứng Phơn gió Tây Nam.
                      </div>
                    </div>

                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px;">
                      <div style="font-size:13px; font-weight:800; color:#7C3AED;">4. Tổng Tích ôn Hữu hiệu Sinh học (GDD)</div>
                      <div style="font-size:14px; margin:8px 0; color:#0F172A; font-family:monospace; background:#FFFFFF; padding:6px 10px; border-radius:6px; border:1px solid #CBD5E1;">
                        $$GDD = \\sum \\max\\left(\\frac{T_{max} + T_{min}}{2} - T_{base}, 0\\right)$$
                      </div>
                      <div style="font-size:11.5px; color:#475569;">
                        <b>Đặc tả:</b> $T_{base} = 10^\\circ\\text{C}$ đối với cây lúa thuần (ST25, J02, TBR225). Dự báo chính xác ngày trỗ bông và ngày thu hoạch để né bão lũ.
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =============================================================================
# 6. 📥 TẢI DỮ LIỆU API
# =============================================================================
def hien_tai_du_lieu_api(ctx):
    du_lieu.hien(ctx)
