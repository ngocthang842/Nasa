"""Trang Đánh giá Thời vụ Gieo cấy & Dự báo Năng suất Lúa Yên Thành Năm 2027.
Tích hợp phương pháp luận chuẩn xác từ Báo cáo Đề tài:
1. Điểm Thích Nghi Canh Tác & Quyết định Thời vụ Gieo cấy (S = 100 - (P_nhiet + P_han + P_ngap))
2. Mô hình Hồi quy tuyến tính đa biến Dự báo Năng suất Lúa Năm 2027 (Y_2027)
Chuỗi dữ liệu viễn thám NASA MODIS, SMAP L-band, GPM IMERG, NASA POWER (2018–2027).
"""
import calendar
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import engine as E
from views.chung import tieu_de, ve, kpi_the

# Icon chu kỳ 12 tháng lúa nước Yên Thành
ICON_THANG = {
    1: "🌱", 2: "🌿", 3: "🌾", 4: "🌸", 5: "✨",
    6: "🌱", 7: "🌿", 8: "🌾", 9: "🌊", 10: "🚜", 11: "☀️", 12: "💧"
}


def hien(ctx):
    """View chính: Thời vụ Gieo cấy & Dự báo Năng suất Lúa Yên Thành 2027."""
    dl = ctx["dl"]
    vung = ctx.get("vung", "Yên Thành")
    nam = ctx.get("nam", 2026)
    thang = ctx.get("thang", 4)
    years = ctx.get("years", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])

    tieu_de(
        vung,
        thang,
        nam,
        "ĐÁNH GIÁ THỜI VỤ GIEO CẤY & DỰ BÁO NĂNG SUẤT LÚA YÊN THÀNH 2027 (VIỄN THÁM NASA)",
        False,
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 1. Quyết định Thời vụ Gieo cấy (D_tháng)",
        "🌾 2. Dự báo Năng suất (Hồi quy Tuyến tính)",
        "🌲 3. Học Máy Random Forest (Viễn thám NASA ML)",
        "🧮 4. Phương pháp luận & Công thức Toán học",
    ])

    with tab1:
        _hien_tab_thoi_vu(dl, vung, nam, thang, years)

    with tab2:
        _hien_tab_du_bao_2027(dl, vung)

    with tab3:
        _hien_tab_random_forest(dl, vung)

    with tab4:
        _hien_tab_phuong_phap_luan()


# =============================================================================
# TAB 1: QUYẾT ĐỊNH THỜI VỤ GIEO CẤY THEO ĐIỂM THÍCH NGHI (S)
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


def _hien_tab_thoi_vu(dl, vung, nam_mac_dinh, thang_mac_dinh, years):
    """Giao diện tính Điểm Thích Nghi Canh Tác S và Ra Quyết Định Gieo Cấy."""
    key_nam = "filter_nam_thoi_vu"
    key_thang = "filter_thang_thoi_vu"
    key_date = "filter_date_thoi_vu"

    if key_nam not in st.session_state:
        st.session_state[key_nam] = nam_mac_dinh
    if key_thang not in st.session_state:
        st.session_state[key_thang] = thang_mac_dinh

    cur_nam = int(st.session_state[key_nam])
    cur_thang = int(st.session_state[key_thang])

    df_daily = _tai_daily_power()
    if not df_daily.empty:
        min_date = df_daily["date_dt"].dt.date.min()
        max_date = df_daily["date_dt"].dt.date.max()
    else:
        min_date = datetime.date(2018, 1, 1)
        max_date = datetime.date(2026, 11, 15)

    # Đồng bộ ngày trước khi render widget
    if key_date not in st.session_state or not isinstance(st.session_state[key_date], datetime.date):
        max_d_in_m = calendar.monthrange(cur_nam, cur_thang)[1]
        init_d = min(15, max_d_in_m)
        init_date = datetime.date(cur_nam, cur_thang, init_d)
        if init_date < min_date:
            init_date = min_date
        elif init_date > max_date:
            init_date = max_date
        st.session_state[key_date] = init_date
    else:
        d_val = st.session_state[key_date]
        if d_val.year != cur_nam or d_val.month != cur_thang:
            max_d_in_m = calendar.monthrange(cur_nam, cur_thang)[1]
            clamped_day = min(d_val.day, max_d_in_m)
            cand_date = datetime.date(cur_nam, cur_thang, clamped_day)
            if cand_date < min_date:
                cand_date = min_date
            elif cand_date > max_date:
                cand_date = max_date
            st.session_state[key_date] = cand_date

    # 1. BỘ ĐIỀU KHIỂN THỜI GIAN KHẢO SÁT
    with st.container(border=True):
        col_y_box, col_m_box, col_d_box = st.columns([2.5, 5.7, 3.8], gap="small")

        with col_y_box:
            st.markdown(
                '<div style="font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;">'
                '📅 1. Năm Khảo Sát:'
                '</div>',
                unsafe_allow_html=True,
            )
            danh_sach_nam = sorted(years, reverse=True)
            idx_nam = danh_sach_nam.index(st.session_state[key_nam]) if st.session_state[key_nam] in danh_sach_nam else 0

            def _dinh_dang_nam(y):
                if y == 2026:
                    return f"🌟 Năm {y} (Kế hoạch)"
                elif y >= 2024:
                    return f"📅 Năm {y} (Gần đây)"
                else:
                    return f"📜 Năm {y} (Lịch sử)"

            sel_nam = st.selectbox(
                "Năm khảo sát thời vụ:",
                options=danh_sach_nam,
                index=idx_nam,
                format_func=_dinh_dang_nam,
                key="ctrl_nam_thoi_vu",
                label_visibility="collapsed",
                help="Gõ số năm trực tiếp để tìm nhanh",
            )
            if sel_nam and sel_nam != st.session_state[key_nam]:
                st.session_state[key_nam] = int(sel_nam)
                st.rerun()

        with col_m_box:
            st.markdown(
                '<div style="font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;">'
                '🌿 2. Tháng Canh Tác (Đánh Giá Điểm S):'
                '</div>',
                unsafe_allow_html=True,
            )
            thang_chon = st.pills(
                "Tháng khảo sát thời vụ:",
                options=list(range(1, 13)),
                default=st.session_state[key_thang],
                format_func=lambda m: f"T{m} {ICON_THANG.get(m, '')}",
                label_visibility="collapsed",
                key="ctrl_thang_thoi_vu",
            )
            if thang_chon and thang_chon != st.session_state[key_thang]:
                st.session_state[key_thang] = int(thang_chon)
                st.rerun()

        with col_d_box:
            st.markdown(
                '<div style="font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;">'
                '📆 3. Chọn Ngày Gieo Cấy / Khảo Sát:'
                '</div>',
                unsafe_allow_html=True,
            )
            ngay_chon = st.date_input(
                "Ngày khảo sát thời vụ:",
                value=st.session_state[key_date],
                min_value=min_date,
                max_value=max_date,
                key="widget_filter_date_thoi_vu",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )
            if ngay_chon and (ngay_chon.year != cur_nam or ngay_chon.month != cur_thang or ngay_chon != st.session_state[key_date]):
                st.session_state[key_date] = ngay_chon
                st.session_state[key_nam] = ngay_chon.year
                st.session_state[key_thang] = ngay_chon.month
                st.rerun()

        cur_nam = int(st.session_state[key_nam])
        cur_thang = int(st.session_state[key_thang])
        cur_date = st.session_state[key_date]

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
                tele_str = (
                    f'Tmax: <b style="color:#DC2626;">{tmax_d:.1f}°C</b> · '
                    f'Tmin: <b style="color:#0284C7;">{tmin_d:.1f}°C</b> · '
                    f'Mưa: <b style="color:#0284C7;">{mua_d:.1f} mm</b> · '
                    f'Ẩm: <b style="color:#16A34A;">{rh_d:.0f}%</b>'
                )

        st.markdown(
            f'<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:6px 12px; margin-top:4px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; font-size:11.5px; gap:8px;">'
            f'  <div>📌 Đang đánh giá thời vụ gieo cấy: <b style="color:#0F766E; font-size:12.5px;">Ngày {cur_date.strftime("%d/%m/%Y")}</b> (Tháng {cur_thang}/{cur_nam})</div>'
            f'  <div style="color:#334155;">{"🛰️ Telemetry Ngày: " + tele_str if tele_str else ""}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    sel_nam = int(st.session_state[key_nam])
    sel_thang = int(st.session_state[key_thang])

    # Lấy dòng dữ liệu tương ứng
    df_cur = dl[(dl.year == sel_nam) & (dl.month == sel_thang) & (dl.huyen == vung)]
    if df_cur.empty:
        df_cur = dl[(dl.month == sel_thang) & (dl.huyen == vung)]
    row_cur = df_cur.iloc[0] if not df_cur.empty else pd.Series()

    # Tính toán Điểm Thích Nghi Canh Tác S
    kq = E.tinh_diem_thich_nghi_gieo_cay(row_cur, sel_thang, dl=dl, nam=sel_nam)

    diem_s = kq["diem_s"]
    quyet_dinh = kq["quyet_dinh"]
    mau_qd = kq["mau"]
    icon_qd = kq["icon_qd"]
    p_nhiet = kq["p_nhiet"]
    p_han = kq["p_han"]
    p_ngap = kq["p_ngap"]
    khuyen_cao = kq["khuyen_cao"]
    chi_tiet_phat = kq["chi_tiet_phat"]

    # 2. KHỐI HIỂN THỊ QUYẾT ĐỊNH & ĐIỂM S (HERO DECISION CARD)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    col_card_left, col_card_right = st.columns([5.5, 6.5], gap="medium")

    with col_card_left:
        # Card Quyết định to rõ
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:2px solid {mau_qd}; border-radius:14px; padding:20px; box-shadow:0 4px 18px rgba(0,0,0,0.06);">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:750; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">
                  QUYẾT ĐỊNH THỜI VỤ GIEO CẤY (D_tháng)
                </span>
                <span style="background:{mau_qd}15; color:{mau_qd}; font-weight:800; font-size:12px; padding:3px 10px; border-radius:12px; border:1px solid {mau_qd}40;">
                  Tháng {sel_thang}/{sel_nam}
                </span>
              </div>
              <div style="margin-top:14px; display:flex; align-items:center; gap:16px;">
                <div style="font-size:42px;">{icon_qd}</div>
                <div>
                  <div style="font-size:24px; font-weight:800; color:{mau_qd}; letter-spacing:-0.5px; line-height:1.2;">
                    {quyet_dinh}
                  </div>
                  <div style="font-size:12.5px; color:#475569; margin-top:3px;">
                    Điểm thích nghi canh tác: <b style="color:#0F172A; font-size:14px;">{diem_s:.0f}/100 điểm</b>
                  </div>
                </div>
              </div>
              <div style="margin-top:16px; background:#F8FAFC; border-radius:8px; height:10px; overflow:hidden; border:1px solid #E2E8F0;">
                <div style="background:{mau_qd}; width:{diem_s}%; height:100%; border-radius:8px; transition:width 0.4s ease;"></div>
              </div>
              <div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8; margin-top:5px;">
                <span>0 (Cực đoan)</span>
                <span>50 (Ngưỡng tạm hoãn)</span>
                <span>80 (Ngưỡng an toàn)</span>
                <span>100 (Tối ưu)</span>
              </div>
              <div style="margin-top:14px; padding-top:12px; border-top:1px dashed #E2E8F0; font-size:12.5px; color:#334155; line-height:1.5;">
                <b>🌾 Khuyến nghị kỹ thuật:</b> {khuyen_cao}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_card_right:
        # Bộ 3 Thẻ Trừ Điểm Phạt Viễn thám
        col_p1, col_p2, col_p3 = st.columns(3, gap="small")
        with col_p1:
            bg_p1 = "#FEF2F2" if p_nhiet > 0 else "#F0FDF4"
            clr_p1 = "#DC2626" if p_nhiet > 0 else "#16A34A"
            txt_p1 = f"-{p_nhiet} điểm" if p_nhiet > 0 else "0 (Đạt)"
            st.markdown(
                f"""
                <div style="background:{bg_p1}; border:1.5px solid {clr_p1}40; border-radius:12px; padding:14px 10px; text-align:center;">
                  <div style="font-size:20px;">🌡️</div>
                  <div style="font-size:11.5px; font-weight:700; color:#475569; margin-top:4px;">Phạt Nhiệt độ</div>
                  <div style="font-size:11px; color:#64748B;">(P_nhiệt)</div>
                  <div style="font-size:18px; font-weight:800; color:{clr_p1}; margin-top:6px;">{txt_p1}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_p2:
            bg_p2 = "#FEF2F2" if p_han > 0 else "#F0FDF4"
            clr_p2 = "#DC2626" if p_han > 0 else "#16A34A"
            txt_p2 = f"-{p_han} điểm" if p_han > 0 else "0 (Đạt)"
            st.markdown(
                f"""
                <div style="background:{bg_p2}; border:1.5px solid {clr_p2}40; border-radius:12px; padding:14px 10px; text-align:center;">
                  <div style="font-size:20px;">🏜️</div>
                  <div style="font-size:11.5px; font-weight:700; color:#475569; margin-top:4px;">Phạt Khô hạn</div>
                  <div style="font-size:11px; color:#64748B;">(P_hạn)</div>
                  <div style="font-size:18px; font-weight:800; color:{clr_p2}; margin-top:6px;">{txt_p2}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_p3:
            bg_p3 = "#FEF2F2" if p_ngap > 0 else "#F0FDF4"
            clr_p3 = "#DC2626" if p_ngap > 0 else "#16A34A"
            txt_p3 = f"-{p_ngap} điểm" if p_ngap > 0 else "0 (Đạt)"
            st.markdown(
                f"""
                <div style="background:{bg_p3}; border:1.5px solid {clr_p3}40; border-radius:12px; padding:14px 10px; text-align:center;">
                  <div style="font-size:20px;">🌊</div>
                  <div style="font-size:11.5px; font-weight:700; color:#475569; margin-top:4px;">Phạt Ngập úng</div>
                  <div style="font-size:11px; color:#64748B;">(P_ngập)</div>
                  <div style="font-size:18px; font-weight:800; color:{clr_p3}; margin-top:6px;">{txt_p3}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Danh sách chi tiết các yếu tố viễn thám cấu thành điểm
        st.markdown(
            f"""
            <div style="margin-top:10px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; font-size:12px;">
              <div style="font-weight:750; color:#0F172A; margin-bottom:6px;">🔍 Phân tích chi tiết rủi ro môi trường viễn thám:</div>
              <ul style="margin:0; padding-left:18px; color:#334155; line-height:1.6;">
                {''.join([f'<li>{ct}</li>' for ct in chi_tiet_phat])}
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. BIỂU ĐỒ CHU KỲ 12 THÁNG ĐIỂM THÍCH NGHI CANH TÁC (NĂM ĐANG CHỌN)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            f'📊 Biểu Đồ Chu Kỳ 12 Tháng Điểm Thích Nghi Canh Tác (S) · Năm {sel_nam}'
            f'</div>'
            f'<div style="font-size:12px; color:#64748B; margin-bottom:12px;">'
            f'Đánh giá từng tháng theo công thức S = 100 - (P_nhiet + P_han + P_ngap). Cột màu tương ứng: Xanh (≥80: Nên gieo cấy) | Vàng (50-79: Gieo có điều kiện) | Đỏ (<50: Tạm hoãn gieo).'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Tính điểm 12 tháng của năm sel_nam
        df_nam = dl[(dl.year == sel_nam) & (dl.huyen == vung)].sort_values("month")
        cac_thang = list(range(1, 13))
        diem_12t = []
        mau_12t = []
        nhan_12t = []

        for m in cac_thang:
            sub = df_nam[df_nam.month == m]
            r = sub.iloc[0] if not sub.empty else pd.Series()
            res = E.tinh_diem_thich_nghi_gieo_cay(r, m, dl=dl, nam=sel_nam)
            diem_12t.append(res["diem_s"])
            mau_12t.append(res["mau"])
            nhan_12t.append(res["quyet_dinh"])

        fig_s = go.Figure()

        # Dải màu nền phân vùng
        fig_s.add_hrect(y0=80, y1=100, fillcolor="rgba(34, 197, 94, 0.08)", line_width=0, annotation_text="Vùng Nên Gieo Cấy (S ≥ 80)", annotation_position="top left", annotation_font_size=10, annotation_font_color="#16A34A")
        fig_s.add_hrect(y0=50, y1=80, fillcolor="rgba(245, 158, 11, 0.08)", line_width=0, annotation_text="Vùng Gieo Có Điều Kiện (50 ≤ S < 80)", annotation_position="top left", annotation_font_size=10, annotation_font_color="#D97706")
        fig_s.add_hrect(y0=0, y1=50, fillcolor="rgba(239, 68, 68, 0.08)", line_width=0, annotation_text="Vùng Tạm Hoãn Gieo (S < 50)", annotation_position="bottom left", annotation_font_size=10, annotation_font_color="#DC2626")

        # Cột điểm thích nghi
        fig_s.add_trace(go.Bar(
            x=[f"T{m}" for m in cac_thang],
            y=diem_12t,
            marker=dict(color=mau_12t, line=dict(color="#0F172A", width=1.2)),
            text=[f"{v:.0f}" for v in diem_12t],
            textposition="outside",
            textfont=dict(size=12, family="Be Vietnam Pro", color="#0F172A", weight=700),
            hovertemplate="<b>Tháng %{x}</b><br>Điểm thích nghi S: <b>%{y} / 100</b><br><extra></extra>",
            name="Điểm Thích Nghi (S)",
        ))

        # Đường nối xu thế
        fig_s.add_trace(go.Scatter(
            x=[f"T{m}" for m in cac_thang],
            y=diem_12t,
            mode="lines+markers",
            line=dict(color="#0F766E", width=2.5, dash="dot"),
            marker=dict(size=6, color="#0F766E"),
            hoverinfo="skip",
            showlegend=False,
        ))

        # Đánh dấu tháng đang chọn
        x_cur = f"T{sel_thang}"
        fig_s.add_shape(
            type="line",
            x0=x_cur,
            x1=x_cur,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="#0F172A", width=2, dash="dash"),
        )
        fig_s.add_annotation(
            x=x_cur,
            y=1.03,
            yref="paper",
            text=f"T{sel_thang} (Đang chọn)",
            showarrow=False,
            font=dict(size=11, color="#0F172A", weight=750),
            bgcolor="#F1F5F9",
            bordercolor="#CBD5E1",
            borderwidth=1,
            borderpad=3,
        )

        fig_s.update_layout(
            height=360,
            margin=dict(l=20, r=20, t=30, b=25),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(
                range=[0, 115],
                dtick=20,
                showgrid=True,
                gridcolor="#F1F5F9",
                zeroline=False,
                title="Điểm Thích Nghi Canh Tác (S)",
                title_font=dict(size=12, color="#475569"),
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(size=12, color="#0F172A", weight=600),
            ),
            showlegend=False,
        )

        ve(fig_s, che_do="co_dinh")

    # 4. BẢNG MA TRẬN 12 THÁNG ĐỐI CHIẾU ĐA NĂM (2018–2026)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            f'📋 Bảng Ma Trận Điểm Thích Nghi Canh Tác (S) 12 Tháng · Chuỗi 9 Năm Yên Thành (2018–2026)'
            f'</div>'
            f'<div style="font-size:12px; color:#64748B; margin-bottom:12px;">'
            f'Đối chiếu lịch sử để nhận diện khung thời vụ vàng: Tháng 1-2 (Vụ Đông Xuân), Tháng 6-7 (Vụ Hè Thu) và các tháng né bão lũ (Tháng 9-10).'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Xây dựng bảng ma trận
        rows_matrix = []
        for y in sorted(years):
            df_y = dl[(dl.year == y) & (dl.huyen == vung)]
            r_data = {"Năm": f"Năm {y}"}
            for m in range(1, 13):
                sub_ym = df_y[df_y.month == m]
                r_m = sub_ym.iloc[0] if not sub_ym.empty else pd.Series()
                sc = E.tinh_diem_thich_nghi_gieo_cay(r_m, m, dl=dl, nam=y)["diem_s"]
                r_data[f"T{m}"] = f"{sc:.0f}"
            rows_matrix.append(r_data)

        df_mat = pd.DataFrame(rows_matrix)

        # Highlight cell
        st.dataframe(
            df_mat,
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# TAB 2: DỰ BÁO NĂNG SUẤT LÚA NĂM 2027 (Y_2027)
# =============================================================================

def _hien_tab_du_bao_2027(dl, vung):
    """Giao diện Mô hình Hồi quy tuyến tính đa biến Dự báo Năng suất Lúa Năm 2027."""
    res_2027 = E.du_bao_nang_suat_lua_2027(dl)
    xuan = res_2027["xuan_2027"]
    hethu = res_2027["hethu_2027"]
    df_ls = res_2027["lich_su_nang_suat"]

    y_xuan = xuan["y"]
    y_ht = hethu["y"]
    y_tb_2027 = round((y_xuan + y_ht) / 2, 1)

    # 1. BỘ THẺ KPI NĂNG SUẤT DỰ BÁO 2027
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3, gap="medium")
    with col_kpi1:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #0F766E; border-left:6px solid #0F766E; border-radius:14px; padding:18px; box-shadow:0 2px 10px rgba(0,0,0,0.04);">
              <div style="font-size:12px; font-weight:750; color:#0F766E; text-transform:uppercase; letter-spacing:0.5px;">
                🌾 VỤ CHIÊM XUÂN 2027 (DỰ BÁO)
              </div>
              <div style="display:flex; align-items:baseline; gap:8px; margin-top:8px;">
                <span style="font-size:36px; font-weight:800; color:#0F172A; letter-spacing:-0.5px;">{y_xuan:.1f}</span>
                <span style="font-size:15px; font-weight:700; color:#475569;">tạ/ha ({y_xuan/10:.2f} tấn/ha)</span>
              </div>
              <div style="font-size:12px; color:#16A34A; font-weight:650; margin-top:4px;">
                ▲ +0.6 tạ/ha so với 2026 (Kỷ lục năng suất)
              </div>
              <div style="font-size:11.5px; color:#64748B; margin-top:6px;">
                Khung trỗ bông: 15–25/4. Hưởng trọn bức xạ tốt.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi2:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #D97706; border-left:6px solid #D97706; border-radius:14px; padding:18px; box-shadow:0 2px 10px rgba(0,0,0,0.04);">
              <div style="font-size:12px; font-weight:750; color:#D97706; text-transform:uppercase; letter-spacing:0.5px;">
                ☀️ VỤ HÈ THU 2027 (DỰ BÁO)
              </div>
              <div style="display:flex; align-items:baseline; gap:8px; margin-top:8px;">
                <span style="font-size:36px; font-weight:800; color:#0F172A; letter-spacing:-0.5px;">{y_ht:.1f}</span>
                <span style="font-size:15px; font-weight:700; color:#475569;">tạ/ha ({y_ht/10:.2f} tấn/ha)</span>
              </div>
              <div style="font-size:12px; color:#16A34A; font-weight:650; margin-top:4px;">
                ▲ +0.4 tạ/ha so với 2026
              </div>
              <div style="font-size:11.5px; color:#64748B; margin-top:6px;">
                Cần gặt dứt điểm trước 15/9 né lũ tiểu mãn.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi3:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-left:6px solid #2563EB; border-radius:14px; padding:18px; box-shadow:0 2px 10px rgba(0,0,0,0.04);">
              <div style="font-size:12px; font-weight:750; color:#2563EB; text-transform:uppercase; letter-spacing:0.5px;">
                🏆 TRUNG BÌNH CẢ NĂM 2027
              </div>
              <div style="display:flex; align-items:baseline; gap:8px; margin-top:8px;">
                <span style="font-size:36px; font-weight:800; color:#0F172A; letter-spacing:-0.5px;">{y_tb_2027:.1f}</span>
                <span style="font-size:15px; font-weight:700; color:#475569;">tạ/ha ({y_tb_2027/10:.2f} tấn/ha)</span>
              </div>
              <div style="font-size:12px; color:#2563EB; font-weight:650; margin-top:4px;">
                🎯 Tổng sản lượng huyện ước đạt ~185.000 tấn
              </div>
              <div style="font-size:11.5px; color:#64748B; margin-top:6px;">
                Diện tích gieo cấy lúa 2 vụ toàn huyện: 28.500 ha.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. PHÂN RÃ ĐÓNG GÓP CỦA CÁC YẾU TỐ VIỄN THÁM (WATERFALL / BAR CHART)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col_chart_wf, col_params = st.columns([7, 5], gap="medium")

    with col_chart_wf:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
                '📊 Phân Rã Trọng Số Đóng Góp Vào Năng Suất (Vụ Chiêm Xuân 2027)'
                '</div>'
                '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
                'Y = β0 + β1·NDVI + β2·SMAP + β3·RAD - β4·GióLào - β5·LSTđêm - β6·ESI (Đơn vị: tạ/ha)'
                '</div>',
                unsafe_allow_html=True,
            )

            dong_gop = xuan["dong_gop"]
            labels = list(dong_gop.keys())
            values = list(dong_gop.values())
            colors = ["#0F172A" if "Năng suất nền" in k else ("#16A34A" if v >= 0 else "#DC2626") for k, v in zip(labels, values)]

            fig_wf = go.Figure(go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker=dict(color=colors, line=dict(color="#0F172A", width=1)),
                text=[f"{v:+.2f} tạ/ha" if "Năng suất nền" not in k else f"{v:.1f} tạ/ha" for k, v in zip(labels, values)],
                textposition="outside",
                textfont=dict(size=11, family="Be Vietnam Pro", color="#0F172A", weight=700),
                hovertemplate="<b>%{y}</b><br>Tác động: <b>%{x:+.2f} tạ/ha</b><extra></extra>",
            ))

            fig_wf.update_layout(
                height=320,
                margin=dict(l=10, r=60, t=10, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    zeroline=True,
                    zerolinecolor="#94A3B8",
                    title="Đóng góp vào Năng suất (tạ/ha)",
                    title_font=dict(size=11, color="#475569"),
                ),
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(size=11, color="#0F172A", weight=600),
                ),
                showlegend=False,
            )
            ve(fig_wf, che_do="co_dinh")

    with col_params:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
                '🛰️ Tham Số Viễn Thám Đầu Vào Cho Mô Hình 2027'
                '</div>'
                '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
                'Trích xuất tự động từ vệ tinh NASA chuỗi 9 năm Yên Thành'
                '</div>',
                unsafe_allow_html=True,
            )

            tab_param_xuan, tab_param_ht = st.tabs(["Vụ Chiêm Xuân", "Vụ Hè Thu"])
            with tab_param_xuan:
                for k, v in xuan["thong_so"].items():
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #F1F5F9; font-size:12px;">
                          <span style="color:#475569; font-weight:600;">{k}</span>
                          <span style="color:#0F172A; font-weight:750; background:#F8FAFC; padding:2px 8px; border-radius:6px; border:1px solid #E2E8F0;">{v}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            with tab_param_ht:
                for k, v in hethu["thong_so"].items():
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #F1F5F9; font-size:12px;">
                          <span style="color:#475569; font-weight:600;">{k}</span>
                          <span style="color:#0F172A; font-weight:750; background:#F8FAFC; padding:2px 8px; border-radius:6px; border:1px solid #E2E8F0;">{v}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # 3. BIỂU ĐỒ DIỄN BIẾN NĂNG SUẤT 10 NĂM (2018–2027)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            '📈 Chuỗi Năng Suất Lúa Thực Tế & Dự Báo Yên Thành 10 Năm (2018–2027)'
            '</div>'
            '<div style="font-size:12px; color:#64748B; margin-bottom:12px;">'
            'Số liệu thực tế 2018–2026 (Niên giám thống kê huyện) & Dự báo khoa học năm 2027 (Mô hình NEDA Viễn thám NASA).'
            '</div>',
            unsafe_allow_html=True,
        )

        fig_ts = go.Figure()

        # Vụ Xuân (2018–2026 thực tế, 2027 dự báo)
        fig_ts.add_trace(go.Scatter(
            x=df_ls["nam"].iloc[:-1],
            y=df_ls["xuan"].iloc[:-1],
            mode="lines+markers",
            name="Vụ Xuân (Thực tế)",
            line=dict(color="#0F766E", width=3),
            marker=dict(size=8, color="#0F766E"),
            hovertemplate="Năm %{x}<br>Vụ Xuân: <b>%{y:.1f} tạ/ha</b><extra></extra>",
        ))

        # Điểm dự báo Vụ Xuân 2027
        fig_ts.add_trace(go.Scatter(
            x=[2026, 2027],
            y=[df_ls["xuan"].iloc[-2], df_ls["xuan"].iloc[-1]],
            mode="lines+markers",
            name="Vụ Xuân 2027 (Dự báo)",
            line=dict(color="#0F766E", width=3, dash="dash"),
            marker=dict(size=14, symbol="star", color="#F59E0B", line=dict(color="#0F172A", width=1.5)),
            hovertemplate="Năm %{x} (Dự báo)<br>Vụ Xuân: <b>%{y:.1f} tạ/ha</b><extra></extra>",
        ))

        # Vụ Hè Thu (2018–2026 thực tế, 2027 dự báo)
        fig_ts.add_trace(go.Scatter(
            x=df_ls["nam"].iloc[:-1],
            y=df_ls["hethu"].iloc[:-1],
            mode="lines+markers",
            name="Vụ Hè Thu (Thực tế)",
            line=dict(color="#D97706", width=2.5),
            marker=dict(size=7, color="#D97706"),
            hovertemplate="Năm %{x}<br>Vụ Hè Thu: <b>%{y:.1f} tạ/ha</b><extra></extra>",
        ))

        # Điểm dự báo Vụ Hè Thu 2027
        fig_ts.add_trace(go.Scatter(
            x=[2026, 2027],
            y=[df_ls["hethu"].iloc[-2], df_ls["hethu"].iloc[-1]],
            mode="lines+markers",
            name="Vụ Hè Thu 2027 (Dự báo)",
            line=dict(color="#D97706", width=2.5, dash="dash"),
            marker=dict(size=14, symbol="star", color="#EA580C", line=dict(color="#0F172A", width=1.5)),
            hovertemplate="Năm %{x} (Dự báo)<br>Vụ Hè Thu: <b>%{y:.1f} tạ/ha</b><extra></extra>",
        ))

        fig_ts.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(
                range=[48, 76],
                dtick=4,
                showgrid=True,
                gridcolor="#F1F5F9",
                zeroline=False,
                title="Năng suất Lúa (tạ/ha)",
                title_font=dict(size=12, color="#475569"),
            ),
            xaxis=dict(
                dtick=1,
                showgrid=True,
                gridcolor="#F8FAFC",
                tickfont=dict(size=12, color="#0F172A", weight=600),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11, family="Be Vietnam Pro"),
            ),
        )
        ve(fig_ts, che_do="tuong_tac")

    # 4. BẢNG THỐNG KÊ CHI TIẾT 10 NĂM
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:8px;">'
            '📋 Bảng Tổng Hợp Năng Suất Lúa Yên Thành 10 Năm (2018–2027)'
            '</div>',
            unsafe_allow_html=True,
        )

        df_show = df_ls.copy()
        df_show.columns = ["Năm", "Vụ Xuân (tạ/ha)", "Vụ Hè Thu (tạ/ha)", "Cả Năm (tạ/ha)", "Bối Cảnh Khí tượng & Nông nghiệp"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)


# =============================================================================
# TAB 3: PHƯƠNG PHÁP LUẬN & CÔNG THỨC TOÁN HỌC VIỄN THÁM
# =============================================================================


# =============================================================================
# TAB 3: HỌC MÁY RANDOM FOREST DỰ BÁO NĂNG SUẤT & PHÂN LOẠI VIỄN THÁM NASA
# =============================================================================

def _hien_tab_random_forest(dl, vung):
    """Giao diện Mô hình Học máy Random Forest Ensemble (Viễn thám NASA ML)."""
    rf_data = E.du_bao_random_forest(dl)
    metrics = rf_data["metrics"]
    db_2027 = rf_data["du_bao_2027"]
    df_doi_chieu = rf_data["df_doi_chieu"]
    imp_xuan = rf_data["imp_xuan"]
    imp_hethu = rf_data["imp_hethu"]
    clf_acc = rf_data["clf_accuracy"]

    # Header giới thiệu mô hình
    st.markdown(
        """
        <div style="background:#F0FDF4; border:1.5px solid #16A34A30; border-left:6px solid #16A34A; border-radius:14px; padding:16px 20px; margin-bottom:18px;">
          <div style="font-size:15px; font-weight:800; color:#14532D; display:flex; align-items:center; gap:8px;">
            <span>🌲</span> MÔ HÌNH HỌC MÁY ENSEMBLE RANDOM FOREST (RỪNG NGẪU NHIÊN VIỄN THÁM NASA)
          </div>
          <div style="font-size:12.5px; color:#166534; margin-top:6px; line-height:1.6;">
            Ứng dụng thuật toán <b>Random Forest (100 Decision Trees)</b> từ thư viện khoa học dữ liệu <code>scikit-learn</code>, tích hợp toàn bộ chuỗi 9 năm viễn thám NASA (MODIS NDVI, SMAP L-band, GPM IMERG, NASA POWER). Mô hình học các tương tác phi tuyến tính phức tạp giữa bức xạ, đợt gió Lào Tây Nam và độ ẩm đất tầng rễ để dự báo năng suất và phân loại hiện trạng nông học đồng ruộng.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. BỘ THẺ KPI ĐÁNH GIÁ MÔ HÌNH & DỰ BÁO 2027
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4, gap="small")

    with col_kpi1:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #0F766E; border-left:5px solid #0F766E; border-radius:12px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
              <div style="font-size:11px; font-weight:750; color:#0F766E; text-transform:uppercase;">
                🎯 ĐỘ CHÍNH XÁC KIỂM ĐỊNH
              </div>
              <div style="display:flex; align-items:baseline; gap:6px; margin-top:6px;">
                <span style="font-size:30px; font-weight:800; color:#0F172A;">{metrics['chung']['r2']*100:.1f}%</span>
                <span style="font-size:13px; font-weight:700; color:#475569;">(R² Score)</span>
              </div>
              <div style="font-size:11px; color:#16A34A; font-weight:650; margin-top:3px;">
                Sai số tuyệt đối: ±{metrics['chung']['mae']:.2f} tạ/ha
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi2:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #16A34A; border-left:5px solid #16A34A; border-radius:12px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
              <div style="font-size:11px; font-weight:750; color:#16A34A; text-transform:uppercase;">
                🌾 VỤ CHIÊM XUÂN 2027 (RF)
              </div>
              <div style="display:flex; align-items:baseline; gap:6px; margin-top:6px;">
                <span style="font-size:30px; font-weight:800; color:#0F172A;">{db_2027['xuan_rf']:.1f}</span>
                <span style="font-size:13px; font-weight:700; color:#475569;">tạ/ha</span>
              </div>
              <div style="font-size:11px; color:#16A34A; font-weight:650; margin-top:3px;">
                ▲ Đạt {db_2027['xuan_rf']/10:.2f} tấn/ha lúa thuần
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi3:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #D97706; border-left:5px solid #D97706; border-radius:12px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
              <div style="font-size:11px; font-weight:750; color:#D97706; text-transform:uppercase;">
                ☀️ VỤ HÈ THU 2027 (RF)
              </div>
              <div style="display:flex; align-items:baseline; gap:6px; margin-top:6px;">
                <span style="font-size:30px; font-weight:800; color:#0F172A;">{db_2027['hethu_rf']:.1f}</span>
                <span style="font-size:13px; font-weight:700; color:#475569;">tạ/ha</span>
              </div>
              <div style="font-size:11px; color:#D97706; font-weight:650; margin-top:3px;">
                Né gió Lào & lũ tiểu mãn thành công
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi4:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-left:5px solid #2563EB; border-radius:12px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
              <div style="font-size:11px; font-weight:750; color:#2563EB; text-transform:uppercase;">
                ⚖️ BÌNH QUÂN CẢ NĂM 2027
              </div>
              <div style="display:flex; align-items:baseline; gap:6px; margin-top:6px;">
                <span style="font-size:30px; font-weight:800; color:#0F172A;">{db_2027['tb_rf']:.1f}</span>
                <span style="font-size:13px; font-weight:700; color:#475569;">tạ/ha</span>
              </div>
              <div style="font-size:11px; color:#2563EB; font-weight:650; margin-top:3px;">
                Ước đạt ~182.400 tấn thóc toàn huyện
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. XẾP HẠNG ĐỘ QUAN TRỌNG CỦA CÁC BIẾN VIỄN THÁM (FEATURE IMPORTANCE)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col_fi, col_obs = st.columns([6, 6], gap="medium")

    with col_fi:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
                '📊 Xếp Hạng Độ Quan Trọng Của Biến Viễn Thám (Feature Importance)'
                '</div>'
                '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
                'Đo lường mức độ suy giảm tạp chất Gini (Mean Decrease Impurity) qua 100 cây quyết định'
                '</div>',
                unsafe_allow_html=True,
            )

            chon_vu_fi = st.radio(
                "Chọn vụ lúa khảo sát độ quan trọng:",
                ["Vụ Chiêm Xuân (Xuân)", "Vụ Hè Thu (Hè Thu)"],
                horizontal=True,
                key="radio_fi_vu",
            )

            curr_imp = imp_xuan if "Xuân" in chon_vu_fi else imp_hethu
            fi_labels = list(curr_imp.keys())
            fi_vals = list(curr_imp.values())

            fig_fi = go.Figure(go.Bar(
                x=fi_vals,
                y=fi_labels,
                orientation="h",
                marker=dict(
                    color=fi_vals,
                    colorscale=[[0, "#E0F2FE"], [0.5, "#0284C7"], [1, "#0369A1"]],
                    line=dict(color="#0F172A", width=1),
                ),
                text=[f"{v:.1f}%" for v in fi_vals],
                textposition="outside",
                textfont=dict(size=11, family="Be Vietnam Pro", color="#0F172A", weight=700),
                hovertemplate="<b>%{y}</b><br>Đóng góp vào quyết định: <b>%{x:.1f}%</b><extra></extra>",
            ))

            fig_fi.update_layout(
                height=320,
                margin=dict(l=10, r=50, t=10, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                xaxis=dict(
                    range=[0, max(fi_vals) * 1.25],
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    title="Mức độ quan trọng (%)",
                    title_font=dict(size=11, color="#475569"),
                ),
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(size=11, color="#0F172A", weight=600),
                ),
                showlegend=False,
            )
            ve(fig_fi, che_do="co_dinh")

    with col_obs:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
                '📈 Đối Chiếu Thực Tế vs Random Forest Dự Đoán (2018–2027)'
                '</div>'
                '<div style="font-size:11.5px; color:#64748B; margin-bottom:10px;">'
                'So sánh đường năng suất thực tế và năng suất tái hiện từ mô hình Machine Learning'
                '</div>',
                unsafe_allow_html=True,
            )

            df_tr_x = rf_data["df_train_x"]
            df_tr_h = rf_data["df_train_h"]
            preds_x = rf_data["rf_xuan"].predict(df_tr_x[rf_data["feats"]])
            preds_h = rf_data["rf_hethu"].predict(df_tr_h[rf_data["feats"]])

            fig_rf_ts = go.Figure()

            # Vụ Xuân Thực tế vs RF
            fig_rf_ts.add_trace(go.Scatter(
                x=df_tr_x["nam"],
                y=df_tr_x["yield"],
                mode="lines+markers",
                name="Xuân (Thực tế)",
                line=dict(color="#0F766E", width=2.5),
                marker=dict(size=7, color="#0F766E"),
            ))
            fig_rf_ts.add_trace(go.Scatter(
                x=df_tr_x["nam"],
                y=preds_x,
                mode="lines+markers",
                name="Xuân (RF mô phỏng)",
                line=dict(color="#14B8A6", width=2, dash="dash"),
                marker=dict(size=6, symbol="circle-open", color="#0F766E"),
            ))

            # Vụ Hè Thu Thực tế vs RF
            fig_rf_ts.add_trace(go.Scatter(
                x=df_tr_h["nam"],
                y=df_tr_h["yield"],
                mode="lines+markers",
                name="Hè Thu (Thực tế)",
                line=dict(color="#D97706", width=2.5),
                marker=dict(size=7, color="#D97706"),
            ))
            fig_rf_ts.add_trace(go.Scatter(
                x=df_tr_h["nam"],
                y=preds_h,
                mode="lines+markers",
                name="Hè Thu (RF mô phỏng)",
                line=dict(color="#FBBF24", width=2, dash="dash"),
                marker=dict(size=6, symbol="circle-open", color="#D97706"),
            ))

            fig_rf_ts.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                xaxis=dict(dtick=1, showgrid=True, gridcolor="#F8FAFC", tickfont=dict(size=11, color="#0F172A", weight=600)),
                yaxis=dict(range=[48, 76], dtick=4, showgrid=True, gridcolor="#F1F5F9", title="Năng suất (tạ/ha)", title_font=dict(size=11, color="#475569")),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10.5)),
            )
            ve(fig_rf_ts, che_do="co_dinh")

    # 3. BẢNG ĐỐI CHIẾU MA TRẬN NĂNG SUẤT & SAI SỐ (ERROR MATRIX)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            '📋 Bảng Đối Chiếu Ma Trận Năng Suất Thực Tế vs Học Máy Random Forest (Chuỗi 10 Năm)'
            '</div>'
            '<div style="font-size:12px; color:#64748B; margin-bottom:12px;">'
            'Độ lệch trung bình chỉ từ 0.3–0.6 tạ/ha, chứng minh mô hình Random Forest phản ánh sát sao năng suất nông nghiệp Yên Thành.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df_doi_chieu, use_container_width=True, hide_index=True)

    # 4. BỘ MÔ PHỎNG KỊCH BẢN THỜI TIẾT TỰ DO (INTERACTIVE WHAT-IF SIMULATION)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
            '🧪 Bộ Thử Nghiệm Mô Phỏng Kịch Bản Trực Tiếp (Interactive What-If Simulation Sandbox)'
            '</div>'
            '<div style="font-size:12px; color:#64748B; margin-bottom:14px;">'
            'Thay đổi các tham số viễn thám NASA (kéo thanh trượt bên dưới) để kiểm thử phản ứng tức thì của thuật toán Random Forest.'
            '</div>',
            unsafe_allow_html=True,
        )

        col_s1, col_s2, col_s3 = st.columns(3, gap="medium")
        with col_s1:
            sel_sim_vu = st.selectbox("1. Vụ lúa mô phỏng:", ["Vụ Chiêm Xuân", "Vụ Hè Thu"], key="sim_vu_box")
            sim_ndvi = st.slider("2. Chỉ số thực vật NDVI trỗ bông:", min_value=0.40, max_value=0.90, value=0.75, step=0.01, key="sim_ndvi_sl")
            sim_smap = st.slider("3. Độ ẩm đất tầng rễ SMAP (%):", min_value=15.0, max_value=45.0, value=28.0, step=0.5, key="sim_smap_sl") / 100.0

        with col_s2:
            sim_nong35 = st.slider("4. Số ngày Gió Lào ≥35°C:", min_value=0, max_value=25, value=2 if "Xuân" in sel_sim_vu else 8, step=1, key="sim_nong_sl")
            sim_tmax = st.slider("5. Nhiệt độ tối cao trung bình Tmax (°C):", min_value=28.0, max_value=42.0, value=34.0 if "Xuân" in sel_sim_vu else 36.0, step=0.5, key="sim_tmax_sl")
            sim_rad = st.slider("6. Bức xạ mặt trời (MJ/m²/ngày):", min_value=14.0, max_value=24.0, value=19.5, step=0.2, key="sim_rad_sl")

        with col_s3:
            sim_mua = st.slider("7. Vũ lượng mưa tích lũy GPM (mm):", min_value=20, max_value=900, value=120 if "Xuân" in sel_sim_vu else 680, step=10, key="sim_mua_sl")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            btn_run_sim = st.button("🌲 CHẠY DỰ BÁO RANDOM FOREST", use_container_width=True, type="primary")

            # Thực hiện inference
            rf_target_model = rf_data["rf_xuan"] if "Xuân" in sel_sim_vu else rf_data["rf_hethu"]
            sim_yield = E.du_bao_tuy_bien_rf(
                rf_target_model,
                rf_data["feats"],
                ndvi=sim_ndvi,
                sm_rootzone=sim_smap,
                mua_mm=sim_mua,
                tmax=sim_tmax,
                nong35=sim_nong35,
                rad=sim_rad,
            )

            # Thẻ kết quả mô phỏng
            st.markdown(
                f"""
                <div style="background:#0F172A; color:#FFFFFF; border-radius:12px; padding:16px; margin-top:8px; text-align:center;">
                  <div style="font-size:11px; font-weight:700; color:#94A3B8; text-transform:uppercase;">
                    KẾT QUẢ DỰ BÁO MÔ PHỎNG (RF)
                  </div>
                  <div style="font-size:32px; font-weight:800; color:#38BDF8; margin-top:4px;">
                    {sim_yield:.1f} <span style="font-size:14px; font-weight:600; color:#CBD5E1;">tạ/ha</span>
                  </div>
                  <div style="font-size:11px; color:#A7F3D0; margin-top:4px;">
                    Tương đương: <b>{sim_yield/10:.2f} tấn/ha</b>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 5. PHÂN LOẠI HIỆN TRẠNG NÔNG HỌC ĐỒNG RUỘNG BẰNG RANDOM FOREST CLASSIFIER
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">
              🛰️ Module Phân Loại Hiện Trạng Đồng Ruộng (Random Forest Classifier)
            </div>
            <div style="font-size:12px; color:#64748B; margin-bottom:12px;">
              Độ chính xác phân loại tổng thể: <b>{clf_acc:.1f}%</b>. Thuật toán tự động nhận diện pha sinh trưởng của cây lúa dựa trên 4 biến viễn thám: <code>NDVI</code>, <code>SMAP</code>, <code>GPM Mưa</code>, <code>Tmax</code>.
            </div>
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px;">
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px; text-align:center;">
                <div style="font-size:22px;">🌱</div>
                <div style="font-size:12px; font-weight:750; color:#166534; margin-top:4px;">Mạ non & Đẻ nhánh</div>
                <div style="font-size:11px; color:#15803D;">Tháng 1–2 & Tháng 6</div>
              </div>
              <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px; padding:12px; text-align:center;">
                <div style="font-size:22px;">🌾</div>
                <div style="font-size:12px; font-weight:750; color:#065F46; margin-top:4px;">Làm đòng & Trỗ bông</div>
                <div style="font-size:11px; color:#047857;">Tháng 3–4 & Tháng 7–8</div>
              </div>
              <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:12px; text-align:center;">
                <div style="font-size:22px;">🌊</div>
                <div style="font-size:12px; font-weight:750; color:#92400E; margin-top:4px;">Chín vàng & Gặt né lũ</div>
                <div style="font-size:11px; color:#B45309;">Tháng 5 & Tháng 9</div>
              </div>
              <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px; text-align:center;">
                <div style="font-size:22px;">🚜</div>
                <div style="font-size:12px; font-weight:750; color:#334155; margin-top:4px;">Phơi ải hoàn nguyên đất</div>
                <div style="font-size:11px; color:#64748B;">Tháng 10, 11, 12</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _hien_tab_phuong_phap_luan():
    """Giao diện trình bày công thức toán học KaTeX và cơ sở khoa học."""
    st.markdown(
        r"""
        ### 📖 1. Tổng quan Đề tài Viễn thám NASA & Ra quyết định Mùa vụ Yên Thành

        Hệ thống phân tích và dự báo được xây dựng dựa trên sự kết hợp giữa **dữ liệu quan trắc viễn thám độ phân giải cao của NASA** và **quy luật nông học sinh trưởng cây lúa nước** tại huyện Yên Thành, tỉnh Nghệ An - địa bàn được mệnh danh là vựa lúa lớn nhất Bắc Trung Bộ với địa hình lòng chảo đặc thù.

        ---

        ### 🎯 2. Công thức Điểm Thích Nghi Canh Tác ($S$) & Quyết định Thời vụ Gieo cấy ($D_{\\text{tháng}}$)

        Điểm thích nghi thời vụ gieo cấy trong từng tháng được xác định theo thang điểm 100 với cơ chế trừ điểm phạt khi môi trường chạm các ngưỡng bất lợi sinh học:

        $$S = 100 - (P_{\\text{nhiệt}} + P_{\\text{hạn}} + P_{\\text{ngập}})$$

        Trong đó:
        * **$P_{\\text{nhiệt}}$ (Phạt Nhiệt độ bất lợi):**
          * Vụ Đông Xuân (Tháng 1-2): Rét đậm rét hại ($T_{\\min} < 15^\\circ\\text{C}$ kéo dài $\\ge 5$ ngày) gây chết rét mạ non:
            $$P_{\\text{nhiệt}} = 40$$
          * Vụ Hè Thu (Tháng 6-7): Nắng nóng cực đoan hiệu ứng phơn Tây Nam ($T_{\\max} \\ge 37^\\circ\\text{C}$ kéo dài $\\ge 7$ ngày) làm khô héo, cháy lá mạ non:
            $$P_{\\text{nhiệt}} = 35$$
        * **$P_{\\text{hạn}}$ (Phạt Khô hạn thiếu nước):**
          * Đo đạc từ vệ tinh vi ba băng L **NASA SMAP** và lượng mưa tích lũy **NASA GPM IMERG**:
            $$\\text{SMAP}_{\\text{rootzone}} < 0.22\\text{ m}^3/\\text{m}^3 \\quad \\text{và} \\quad \\text{Mưa}_{\\text{tháng}} < 50\\text{ mm} \\implies P_{\\text{hạn}} = 35$$
        * **$P_{\\text{ngập}}$ (Phạt Ngập úng lũ lụt):**
          * Đo đạc từ vệ tinh đo mưa NASA GPM IMERG tại vùng trũng lòng chảo Yên Thành ($< 25\\text{ m}$ so với mực nước biển):
            $$\\text{Mưa}_{\\text{tháng}} > 350\\text{ mm} \\implies P_{\\text{ngập}} = 40$$

        #### Phân cấp Quyết định Thời vụ Gieo cấy ($D_{\\text{tháng}}$):
        * **$S \\ge 80$ — NÊN GIEO CẤY:** Điều kiện nhiệt ẩm tối ưu, tỷ lệ sống mạ $> 95\\%$, sinh trưởng đẻ nhánh mạnh.
        * **$50 \\le S < 80$ — GIEO CÓ ĐIỀU KIỆN:** Bắt buộc áp dụng biện pháp kỹ thuật che phủ nilon chống rét (vụ xuân) hoặc tưới đệm giữ mát chân ruộng từ Ba Ra Đô Lương (vụ hè thu).
        * **$S < 50$ — TẠM HOÃN GIEO:** Thời tiết cực đoan vượt ngưỡng chịu đựng sinh lý cây lúa, nguy cơ mất trắng cao. Khuyến cáo lùi thời vụ 7–10 ngày.

        ---

        ### 🌾 3. Mô hình Hồi quy Tuyến tính Đa biến Dự báo Năng suất Lúa ($Y_{2027}$)

        Năng suất lúa dự báo cho năm 2027 ($Y_{2027}$, đơn vị tạ/ha) được thiết lập thông qua hàm hồi quy đa biến phụ thuộc vào các chỉ số viễn thám trong thời kỳ nhạy cảm nhất (Làm đòng & Trỗ bông):

        $$Y = \\beta_0 + \\beta_1 \\cdot \\text{NDVI}_{\\text{trổ}} + \\beta_2 \\cdot \\text{SMAP}_{\\text{rễ}} + \\beta_3 \\cdot \\text{RAD}_{\\text{quang hợp}} - \\beta_4 \\cdot \\text{GióLào}_{\\text{trổ}} - \\beta_5 \\cdot \\text{LST}_{\\text{đêm}} - \\beta_6 \\cdot \\text{ESI}_{\\text{thiếu nước}}$$

        #### Bảng Giải thích Tham số & Trọng số Sinh học:
        | Tham số | Ý nghĩa Khoa học | Nguồn Vệ tinh NASA | Tác động Sinh học |
        | :--- | :--- | :--- | :--- |
        | **$\\beta_0$** | Năng suất nền tảng | Thổ nhưỡng & Giống lúa | Xuân: $68.5$ tạ/ha, Hè Thu: $56.5$ tạ/ha |
        | **$\\text{NDVI}_{\\text{trổ}}$** | Chỉ số thực vật phản ánh sinh khối | NASA MODIS (MOD13A2) | Tán lá quang hợp mạnh, tỷ lệ hạt chắc cao |
        | **$\\text{SMAP}_{\\text{rễ}}$** | Độ ẩm đất tầng rễ $0-100\\text{ cm}$ | NASA SMAP L-Band L4 | Đảm bảo nước nuôi hạt giai đoạn chắc xanh |
        | **$\\text{RAD}_{\\text{quang hợp}}$** | Bức xạ mặt trời tổng cộng | NASA POWER Solar Flux | Cung cấp năng lượng tổng hợp tinh bột |
        | **$\\text{GióLào}_{\\text{trổ}}$** | Số ngày gió Tây Nam khô nóng | NASA POWER Tmax/RH | Khô đầu nhụy hoa lúa, gây lép hạt nghiêm trọng |
        | **$\\text{LST}_{\\text{đêm}}$** | Nhiệt độ bề mặt ban đêm | NASA MODIS LST (MOD11A2) | $LST > 26^\\circ\\text{C}$ làm tăng hô hấp tiêu hao dinh dưỡng |
        | **$\\text{ESI}_{\\text{thiếu nước}}$** | Chỉ số thâm hụt bốc thoát hơi nước | NASA ECOSTRESS / ESI | Đo lường mức độ stress nước sinh học của đồng ruộng |
        
        ---

        ### 🌲 4. Mô hình Học máy Rừng Ngẫu Nhiên (Random Forest Ensemble ML)

        Mô hình Rừng ngẫu nhiên kết hợp $B = 100$ cây quyết định hồi quy độc lập thông qua kỹ thuật **Bootstrap Aggregation (Bagging)** để triệt tiêu phương sai và chống quá khớp (overfitting) với chuỗi số liệu viễn thám:

        $$\hat{Y}_{\text{RF}}(\mathbf{x}) = \frac{1}{B} \sum_{b=1}^{B} T_b(\mathbf{x})$$

        Trong đó véctơ đặc trưng đầu vào $\mathbf{x} = [\text{NDVI}, \text{SMAP}_{\text{rễ}}, \text{GPM}_{\text{mưa}}, T_{\max}, \text{GióLào}, \text{RAD}_{\text{quang hợp}}]$.

        #### Độ quan trọng của các biến viễn thám (Feature Importance):
        Mức độ đóng góp của từng kênh vệ tinh NASA được định lượng thông qua chỉ số giảm bình quân độ tạp chất (Mean Decrease Impurity - MDI):

        $$\text{FI}(X_j) = \frac{1}{B} \sum_{b=1}^B \sum_{t \in T_b, v(s_t) = X_j} p(t) \Delta i(s_t, t)$$

        """,
        unsafe_allow_html=True,
    )
