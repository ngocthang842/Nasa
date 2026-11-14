"""Các trang chuyên sâu theo từng chỉ số Viễn thám NASA (NDVI, SMAP, GPM, LST, Công thức, API).
Thiết kế theo chuẩn Hệ thống Phân tích Môi trường NASA (NEDA) & Vựa lúa Yên Thành (Nghệ An).
Tối ưu hóa hiển thị: Biểu đồ nâng cao có ngưỡng an toàn, Bảng ma trận số liệu 12 tháng,
và Chế độ xem Bản đồ Viễn thám & Telemetry Vệ tinh theo yêu cầu (On-Demand).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine as E
from views import du_lieu
from views.ve_tinh import hien_ve_tinh, CUM_XA_YEN_THANH
from views.chung import tieu_de, ve, kpi_the


# -----------------------------------------------------------------------------
# 1. HÀM VẼ BIỂU ĐỒ NÂNG CAO CÓ NGƯỠNG AN TOÀN CHO CÂY LÚA NƯỚC
# -----------------------------------------------------------------------------
def _ve_chuoi_thoi_gian_chuyen_nghiep(
    df_thang,
    cot,
    tieu_de_bieu_do,
    mau_chinh,
    don_vi="",
    thang_hien_tai=4,
    nguong_an_toan=None,
    vach_canh_bao=None,
    he_so=1.0,
):
    """Vẽ biểu đồ chuỗi thời gian 12 tháng chuyên nghiệp:
    - So sánh đa năm (2024, 2025, 2026)
    - Dải màu ngưỡng sinh trưởng an toàn cho cây lúa nước
    - Vạch cảnh báo ngưỡng rủi ro
    - Làm nổi bật tháng hiện tại đang được chọn
    """
    fig = go.Figure()
    nam_colors = {2026: mau_chinh, 2025: "#0284C7", 2024: "#94A3B8"}
    nam_styles = {
        2026: dict(width=3.8, dash="solid"),
        2025: dict(width=2.4, dash="solid"),
        2024: dict(width=1.8, dash="dot"),
    }

    # Dải ngưỡng sinh trưởng an toàn (nếu có)
    if nguong_an_toan:
        min_v, max_v, nhan_v = nguong_an_toan
        fig.add_hrect(
            y0=min_v,
            y1=max_v,
            fillcolor="rgba(34, 197, 94, 0.08)",
            line=dict(width=1, dash="dash", color="rgba(34, 197, 94, 0.35)"),
            annotation_text=f"🌿 {nhan_v}",
            annotation_position="top left",
            annotation_font=dict(size=10.5, color="#15803D"),
        )

    # Vạch cảnh báo rủi ro (nếu có)
    if vach_canh_bao:
        for vb in vach_canh_bao:
            fig.add_hline(
                y=vb["val"],
                line=dict(color=vb.get("color", "#DC2626"), width=1.5, dash="dashdot"),
                annotation_text=vb.get("label", "Ngưỡng cảnh báo"),
                annotation_position="bottom right",
                annotation_font=dict(size=10.5, color=vb.get("color", "#DC2626")),
            )

    # Vẽ đường số liệu các năm
    for y in sorted(df_thang.year.unique()):
        sub = df_thang[df_thang.year == y].sort_values("month")
        if cot not in sub.columns:
            continue
        y_data = sub[cot] * he_so
        x_data = [f"T{int(m)}" for m in sub.month]

        fig.add_scatter(
            x=x_data,
            y=y_data,
            name=f"Năm {y}",
            mode="lines+markers",
            line=dict(color=nam_colors.get(y, "#64748B"), **nam_styles.get(y, {})),
            marker=dict(size=8 if y == 2026 else 5),
            text=[f"{v:.1f} {don_vi}".strip() for v in y_data],
            hovertemplate=f"<b>Năm {y} · %{{x}}</b>: %{{y:.1f}} {don_vi}<extra></extra>",
        )

    # Đánh dấu tháng hiện tại bằng vạch dọc (dùng add_shape + add_annotation tránh lỗi categorical của Plotly)
    x_cur = f"T{int(thang_hien_tai)}"
    fig.add_shape(
        type="line",
        x0=x_cur,
        x1=x_cur,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#0F172A", width=1.5, dash="dot"),
    )
    fig.add_annotation(
        x=x_cur,
        y=1.02,
        yref="paper",
        text=f"T{int(thang_hien_tai)} (Hiện tại)",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=10, color="#0F172A", weight="bold"),
        bgcolor="rgba(255, 255, 255, 0.85)",
    )

    fig.update_layout(
        title=dict(
            text=tieu_de_bieu_do,
            font=dict(size=13.5, family="Be Vietnam Pro", weight="bold", color="#0F172A"),
        ),
        height=290,
        margin=dict(l=8, r=8, t=36, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.14, x=0, font=dict(size=11)),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11)),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            title=dict(text=don_vi, font=dict(size=11)),
            tickfont=dict(size=11),
        ),
        hovermode="x unified",
    )
    return fig


# -----------------------------------------------------------------------------
# 2. HÀM RENDER BẢNG MA TRẬN SỐ LIỆU 12 THÁNG (DATA MATRIX TABLE)
# -----------------------------------------------------------------------------
def _hien_bang_ma_tran_12_thang(
    df_thang,
    cot,
    don_vi,
    he_so=1.0,
    thang_hien_tai=4,
    format_str="{:.1f}",
    danh_gia_fn=None,
):
    """Tạo bảng ma trận HTML đối chiếu 12 tháng qua các năm (2024, 2025, 2026),
    highlight tháng hiện tại và kèm đánh giá nông học trực quan."""
    years = sorted(df_thang.year.unique())
    all_months = list(range(1, 13))

    # Tạo dict chứa dữ liệu
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

    # Xây dựng HTML table hiện đại
    th_cols = "".join(
        f'<th style="padding:6px 4px; text-align:center; font-size:11px; background:{"#0F766E; color:#FFFFFF;" if m == thang_hien_tai else "#F8FAFC; color:#475569;"} border-bottom:2px solid #CBD5E1;">'
        f'T{m}{" ⭐" if m == thang_hien_tai else ""}'
        f'</th>'
        for m in all_months
    )

    rows_html = ""
    for y in reversed(years):
        is_plan = (y == 2026)
        row_vals = data_dict.get(y, [])
        tds = ""
        for m, v in enumerate(row_vals, start=1):
            is_cur = (m == thang_hien_tai)
            bg = "#ECFDF5" if is_cur else ("#FFFFFF" if is_plan else "#F8FAFC")
            fw = "800" if is_cur else ("700" if is_plan else "500")
            color = "#0F766E" if is_cur else ("#0F172A" if is_plan else "#64748B")
            v_str = format_str.format(v) if not np.isnan(v) else "—"
            tds += f'<td style="padding:7px 4px; text-align:center; font-size:11.5px; font-weight:{fw}; color:{color}; background:{bg}; border-bottom:1px solid #E2E8F0;">{v_str}</td>'

        tb_nam = np.nanmean(row_vals) if len(row_vals) else np.nan
        tb_str = format_str.format(tb_nam) if not np.isnan(tb_nam) else "—"
        td_tb = f'<td style="padding:7px 6px; text-align:center; font-size:11.5px; font-weight:800; color:#0F172A; background:#F1F5F9; border-bottom:1px solid #E2E8F0;">{tb_str}</td>'

        nhan_nam = f"<b>Năm {y}</b> {'(Kế hoạch)' if is_plan else ''}"
        rows_html += f'<tr><td style="padding:7px 8px; font-size:11.5px; color:#1E293B; background:#F8FAFC; border-bottom:1px solid #E2E8F0;">{nhan_nam}</td>{tds}{td_tb}</tr>'

    # Hàng đánh giá trạng thái nông vụ nếu có hàm đánh giá
    row_danh_gia = ""
    if danh_gia_fn and 2026 in data_dict:
        td_dg = ""
        vals_2026 = data_dict[2026]
        for m, v in enumerate(vals_2026, start=1):
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
        row_danh_gia = f'<tr><td style="padding:6px 8px; font-size:11px; font-weight:750; color:#475569; background:#F8FAFC; border-bottom:1px solid #E2E8F0;">Đánh giá Vụ Lúa</td>{td_dg}<td style="background:#F1F5F9; border-bottom:1px solid #E2E8F0;"></td></tr>'

    html_table = f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; overflow-x:auto; margin-top:10px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
      <div style="padding:10px 14px; border-bottom:1px solid #E2E8F0; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:12.5px; font-weight:800; color:#0F172A;">
          📋 Bảng Ma trận Số liệu Viễn thám 12 Tháng ({don_vi}) · Đối chiếu Đa năm Yên Thành
        </div>
        <div style="font-size:11px; color:#0F766E; font-weight:700;">
          ⭐ Cột Tháng {thang_hien_tai} đang được chọn khảo sát
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


# -----------------------------------------------------------------------------
# 3. HÀM HIỂN THỊ KHU VỰC BẢN ĐỒ VỆ TINH THEO YÊU CẦU (ON-DEMAND INTERACTIVE)
# -----------------------------------------------------------------------------
def _hien_khu_vuc_ban_do_ve_tinh(ctx, cot_id, ten_lop, ten_chi_so, icon_lop):
    """Khu vực tương tác Bản đồ Viễn thám:
    Mặc định hiển thị Card Tóm tắt Trạng thái 4 Cụm Xã & Nút bấm 'Xem Chi tiết trên Bản đồ'.
    Khi người dùng bấm vào, bung ra Bản đồ Vệ tinh NASA Folium + Telemetry 4 Cụm Xã."""
    nam = ctx["nam"]
    thang = ctx.get("thang", 4)
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
                      Giám sát tọa độ thực địa tại Cụm Bắc (Đô Thành), Lòng chảo, Cụm Nam (Bảo Thành) và Cụm Tây (Mỹ Thành)
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
            # Đã click mở: Hiển thị Bản đồ Vệ tinh Folium và Telemetry chi tiết
            st.markdown(
                f'<div style="font-size:12px; font-weight:700; color:#0284C7; margin:8px 0 4px 0;">'
                f'🛰️ Đang hiển thị bản đồ viễn thám lớp: <b>{ten_lop}</b> · Tháng {thang}/{nam}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Bản đồ vệ tinh Folium
            ctx_sub = dict(ctx)
            ctx_sub["lop_hien_tai"] = ten_lop
            hien_ve_tinh(ctx_sub)

            # Telemetry 4 cụm xã dạng grid cards
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:12.5px; font-weight:800; color:#0F172A; margin-bottom:6px;">'
                '📡 Telemetry Quan trắc Viễn thám tại 4 Trạm Cụm Xã Yên Thành:'
                '</div>',
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
            # Chưa click mở: Hiển thị thẻ tóm tắt thanh lịch với nút xem chi tiết
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
            st.caption("💡 Bấm nút **'🛰️ Xem Chi tiết trên Bản đồ'** ở góc phải để mở Bản đồ Vệ tinh GIS & Telemetry viễn thám chuyên sâu.")


# =============================================================================
# 1. 🍃 PHÂN TÍCH THẢM THỰC VẬT & SỨC KHỎE LÚA (NDVI)
# =============================================================================
def hien_ndvi(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Phân tích Thảm Thực vật & Sức khỏe Lúa (NDVI MODIS)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_ndvi = float(r_thang["ndvi"].iloc[0]) if not r_thang.empty and "ndvi" in r_thang.columns else 0.65

    # Đánh giá giai đoạn lúa theo tháng
    giai_doan_dict = {
        1:  ("🌱 Mạ non & Cấy lúa Xuân",           "NDVI thấp (0.2–0.3), ruộng ngập nước mạ mới bén."),
        2:  ("🌿 Đẻ nhánh rộ",                      "NDVI tăng nhanh (0.45–0.60), sinh khối lá phát triển mạnh."),
        3:  ("🌾 Làm đòng & Ôm bòng",               "NDVI đạt đỉnh cao (0.70–0.85), thảm phủ xanh kín mặt ruộng."),
        4:  ("🌸 Trỗ bông rộ",                       "NDVI duy trì mức cao (0.65–0.78), lúa bắt đầu vào mẩy."),
        5:  ("✨ Chín vàng & Thu hoạch",             "NDVI giảm (0.35–0.50) do lá vàng và gặt rơm rạ."),
        6:  ("🌱 Xuống giống Hè Thu",                "NDVI thấp (0.2–0.35), cấy chạy lũ tiểu mãn."),
        7:  ("🌿 Đẻ nhánh Hè Thu",                  "NDVI tăng nhanh (0.50–0.65) vượt đỉnh nhiệt gió Lào."),
        8:  ("🌾 Làm đòng & Trỗ Hè Thu",            "NDVI đạt 0.70–0.80 trước mùa bão."),
        9:  ("🌊 Gặt né lũ & Ngập Kênh Vách Bắc",  "NDVI giảm nhanh sau khi gặt chạy lũ."),
        10: ("🚜 Cày ải đất & Rau màu vụ đông",     "NDVI vùng lúa thấp (0.25), vùng ngô/lạc đạt 0.55."),
        11: ("☀️ Phơi nỏ ruộng vụ đông",            "Đất khô ải, chuẩn bị lấy nước."),
        12: ("💧 Lấy nước đổ ải vụ xuân",           "Ruộng đầy nước phù sa sông Lam."),
    }
    gd_ten, gd_mota = giai_doan_dict.get(thang, ("Giai đoạn sinh trưởng lúa", "Giám sát viễn thám"))

    # HÀNG 1: THẺ KPI & THANG ĐO
    c1, c2, c3 = st.columns([3.2, 5.2, 3.6])
    with c1, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:750; color:#64748B;">CHỈ SỐ NDVI MODIS</div>
            <div style="font-size:32px; font-weight:800; color:#16A34A; line-height:1.1;">{cur_ndvi:.2f}</div>
            <div style="font-size:12px; color:#475569; margin-top:4px;"><b>Tháng {thang}/{nam}</b> · Vựa lúa Yên Thành</div>
            <hr style="margin:8px 0; border-color:#E2E8F0;">
            <div style="font-size:12px; color:#1E293B;"><b>{gd_ten}</b></div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">{gd_mota}</div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        # Biểu đồ chuỗi thời gian NDVI nâng cao có ngưỡng sinh khối tốt
        fig_ndvi = _ve_chuoi_thoi_gian_chuyen_nghiep(
            dl_yt,
            cot="ndvi",
            tieu_de_bieu_do="Biểu đồ Chuỗi 12 Tháng NDVI MODIS (Đa năm 2024–2026)",
            mau_chinh="#16A34A",
            don_vi="NDVI",
            thang_hien_tai=thang,
            nguong_an_toan=(0.60, 0.85, "Sinh khối lúa tốt (0.60–0.85)"),
            vach_canh_bao=[dict(val=0.40, label="Ngưỡng mạ/đất ải (0.40)", color="#EAB308")],
        )
        ve(fig_ndvi, che_do="tuong_tac")

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">🔬 Thang Đo Sức Khỏe Lúa NDVI</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:6px 10px; border-radius:6px;">
                <b>🟢 NDVI > 0.70:</b> Lúa trỗ đều, sinh khối khỏe, tán lá xanh kín mặt ruộng.
              </div>
              <div style="background:#FEFCE8; border:1px solid #FEF08A; border-left:4px solid #EAB308; padding:6px 10px; border-radius:6px;">
                <b>🟡 NDVI 0.40–0.70:</b> Giai đoạn mạ non hoặc lúa bắt đầu chín vào hạt.
              </div>
              <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; padding:6px 10px; border-radius:6px;">
                <b>🔴 NDVI < 0.40:</b> Đất phơi ải, ruộng trũng ngập úng hoặc bị hạn táp lá.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
    def dg_ndvi(val, m):
        if val >= 0.70:
            return "🟢 Rất tốt", "#DCFCE7", "#15803D"
        elif val >= 0.50:
            return "🟡 Khá", "#FEF9C3", "#A16207"
        else:
            return "⚪ Mạ/Ải", "#F1F5F9", "#475569"

    _hien_bang_ma_tran_12_thang(
        dl_yt,
        cot="ndvi",
        don_vi="NDVI",
        he_so=1.0,
        thang_hien_tai=thang,
        format_str="{:.2f}",
        danh_gia_fn=dg_ndvi,
    )

    # HÀNG 3: KHU VỰC BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="ndvi",
        ten_lop="🌿 Sức khỏe Lúa (NDVI)",
        ten_chi_so="NDVI MODIS",
        icon_lop="🌿",
    )


# =============================================================================
# 2. 💧 ĐỘ ẨM ĐẤT TẦNG RỄ (SMAP L-BAND)
# =============================================================================
def hien_do_am(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Giám sát Độ Ẩm Đất & Cân bằng Nước Ruộng Lúa (SMAP L-band)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_sm = float(r_thang["sm_rootzone"].iloc[0] * 100) if not r_thang.empty and "sm_rootzone" in r_thang.columns else 28.0

    # HÀNG 1: THẺ KPI & THANG ĐO
    c1, c2, c3 = st.columns([3.2, 5.2, 3.6])
    with c1, st.container(border=True):
        muc_am = "Đủ ẩm canh tác" if cur_sm >= 25 else "Thiếu ẩm cần tưới"
        col_am = "#0284C7" if cur_sm >= 25 else "#DC2626"
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:750; color:#64748B;">ĐỘ ẨM ĐẤT TẦNG RỄ (SMAP)</div>
            <div style="font-size:32px; font-weight:800; color:{col_am}; line-height:1.1;">{cur_sm:.1f}%</div>
            <div style="font-size:12px; color:#475569; margin-top:4px;"><b>Tháng {thang}/{nam}</b> · {muc_am}</div>
            <hr style="margin:8px 0; border-color:#E2E8F0;">
            <div style="font-size:12px; color:#1E293B;"><b>Hệ thống Thủy nông Ba Ra Đô Lương:</b></div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">Cung cấp nước tưới tự chảy qua Kênh chính cho 26.500 ha đồng ruộng Yên Thành.</div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        # Biểu đồ chuỗi thời gian SMAP nâng cao có dải ẩm an toàn
        fig_sm = _ve_chuoi_thoi_gian_chuyen_nghiep(
            dl_yt,
            cot="sm_rootzone",
            tieu_de_bieu_do="Biểu đồ Chuỗi 12 Tháng Độ Ẩm Đất SMAP (Đa năm 2024–2026)",
            mau_chinh="#0284C7",
            don_vi="%",
            thang_hien_tai=thang,
            nguong_an_toan=(25.0, 35.0, "Dải ẩm tối ưu cho lúa (25%–35%)"),
            vach_canh_bao=[dict(val=20.0, label="Ngưỡng hạn kiệt (20%)", color="#DC2626")],
            he_so=100.0,
        )
        ve(fig_sm, che_do="tuong_tac")

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">💧 Điều tiết Nước theo Địa hình Yên Thành</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #0284C7; padding:6px 10px; border-radius:6px;">
                <b>Vùng Trũng Lòng Chảo (Bảo Thành, Vĩnh Thành):</b> Nguy cơ ngập úng khi mưa lớn dồn về Kênh Vách Bắc.
              </div>
              <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #D97706; padding:6px 10px; border-radius:6px;">
                <b>Vùng Vàn Cao (Mỹ Thành, Tân Thành):</b> Dốc thoải, dễ mất nước khi có gió Lào, cần tích nước hồ đập.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
    def dg_sm(val, m):
        if val >= 25.0:
            return "🟢 Đủ ẩm", "#DCFCE7", "#15803D"
        elif val >= 20.0:
            return "🟡 Thiếu ẩm", "#FEF9C3", "#A16207"
        else:
            return "🔴 Hạn kiệt", "#FEE2E2", "#B91C1C"

    _hien_bang_ma_tran_12_thang(
        dl_yt,
        cot="sm_rootzone",
        don_vi="%",
        he_so=100.0,
        thang_hien_tai=thang,
        format_str="{:.1f}%",
        danh_gia_fn=dg_sm,
    )

    # HÀNG 3: KHU VỰC BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="smap",
        ten_lop="💧 Độ ẩm Ruộng (SMAP)",
        ten_chi_so="SMAP L-band",
        icon_lop="💧",
    )


# =============================================================================
# 3. 🌧️ LƯỢNG MƯA TÍCH LŨY (NASA GPM IMERG)
# =============================================================================
def hien_luong_mua(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Giám sát Lượng Mưa Tích Lũy & Bão Lũ (NASA GPM IMERG)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_mua = float(r_thang["mua_mm"].iloc[0]) if not r_thang.empty and "mua_mm" in r_thang.columns else 85.0

    # HÀNG 1: THẺ KPI & THANG ĐO
    c1, c2, c3 = st.columns([3.2, 5.2, 3.6])
    with c1, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:750; color:#64748B;">LƯỢNG MƯA THÁNG (GPM)</div>
            <div style="font-size:32px; font-weight:800; color:#0284C7; line-height:1.1;">{cur_mua:.0f} <span style="font-size:16px;">mm</span></div>
            <div style="font-size:12px; color:#475569; margin-top:4px;"><b>Tháng {thang}/{nam}</b> · Đo đạc GPM IMERG</div>
            <hr style="margin:8px 0; border-color:#E2E8F0;">
            <div style="font-size:12px; color:#1E293B;"><b>Nguy cơ Lũ Tiểu mãn & Bão:</b></div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">Đỉnh mưa lũ tập trung mạnh nhất vào Tháng 9 (300–600 mm). Cần gặt xong lúa hè thu trước 15/9.</div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        # Biểu đồ chuỗi thời gian GPM nâng cao có vạch báo động lũ
        fig_mua = _ve_chuoi_thoi_gian_chuyen_nghiep(
            dl_yt,
            cot="mua_mm",
            tieu_de_bieu_do="Biểu đồ Vũ lượng 12 Tháng GPM IMERG (Đa năm 2024–2026)",
            mau_chinh="#0284C7",
            don_vi="mm",
            thang_hien_tai=thang,
            nguong_an_toan=(50.0, 180.0, "Mưa vừa vụ lúa (50–180 mm)"),
            vach_canh_bao=[dict(val=250.0, label="Ngưỡng báo động ngập úng (250 mm)", color="#DC2626")],
        )
        ve(fig_mua, che_do="tuong_tac")

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">🌊 Năng Lực Tiêu Úng Kênh Vách Bắc</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:6px 10px; border-radius:6px;">
                <b>Tháng 1–5 (Mùa khô):</b> Lượng mưa thấp (40–120 mm), phụ thuộc nước tưới Ba Ra Đô Lương.
              </div>
              <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; padding:6px 10px; border-radius:6px;">
                <b>Tháng 9–10 (Mùa lũ lớn):</b> Mưa bão dồn dập, cần mở thông các cống tiêu Kênh Vách Bắc ra biển.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
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
        format_str="{:.0f} mm",
        danh_gia_fn=dg_mua,
    )

    # HÀNG 3: KHU VỰC BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="gpm",
        ten_lop="🌧️ Lượng mưa (GPM)",
        ten_chi_so="NASA GPM IMERG",
        icon_lop="🌧️",
    )


# =============================================================================
# 4. 🌡️ NHIỆT ĐỘ BỀ MẶT (LST & GIÓ LÀO TÂY NAM)
# =============================================================================
def hien_nhiet_do(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Giám sát Nhiệt độ Bề mặt LST & Gió Lào Tây Nam (NASA POWER)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_tmax = float(r_thang["tmax"].iloc[0]) if not r_thang.empty and "tmax" in r_thang.columns else 32.5
    cur_nong = int(r_thang["nong35"].iloc[0]) if not r_thang.empty and "nong35" in r_thang.columns else 5

    # HÀNG 1: THẺ KPI & THANG ĐO
    c1, c2, c3 = st.columns([3.2, 5.2, 3.6])
    with c1, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:750; color:#64748B;">NHIỆT ĐỘ TMAX & GIÓ LÀO</div>
            <div style="font-size:32px; font-weight:800; color:#EA580C; line-height:1.1;">{cur_tmax:.1f}° <span style="font-size:16px;">C</span></div>
            <div style="font-size:12px; color:#DC2626; font-weight:700; margin-top:4px;">🔥 Có {cur_nong} ngày Gió Lào ≥35°C (Tháng {thang})</div>
            <hr style="margin:8px 0; border-color:#E2E8F0;">
            <div style="font-size:12px; color:#1E293B;"><b>Tác động đến Vụ Lúa Yên Thành:</b></div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">Gió Lào khô nóng làm táp phấn lúa trỗ bông tháng 4–5 và hạn hán vụ hè thu tháng 6–7.</div>
            """,
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        # Biểu đồ chuỗi thời gian Tmax nâng cao có vạch báo nhiệt táp lúa
        fig_tmax = _ve_chuoi_thoi_gian_chuyen_nghiep(
            dl_yt,
            cot="tmax",
            tieu_de_bieu_do="Biểu đồ Nhiệt độ Tmax 12 Tháng Đối chiếu Đa năm (2024–2026)",
            mau_chinh="#EA580C",
            don_vi="°C",
            thang_hien_tai=thang,
            nguong_an_toan=(22.0, 32.0, "Nhiệt độ tối hảo cho lúa (22°C–32°C)"),
            vach_canh_bao=[dict(val=35.0, label="Ngưỡng Gió Lào táp bông (≥35°C)", color="#DC2626")],
        )
        ve(fig_tmax, che_do="tuong_tac")

    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">🛡️ Mệnh Lệnh Canh Tác Chống Nóng</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#FFF7ED; border:1px solid #FFEDD5; border-left:4px solid #EA580C; padding:6px 10px; border-radius:6px;">
                <b>Giữ Mực Nước Đệm 3–5 cm:</b> Dâng nước làm mát gốc lúa, hạ nhiệt vi khí hậu ruộng đồng khi gió Lào thổi mạnh.
              </div>
              <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; padding:6px 10px; border-radius:6px;">
                <b>Tuyệt Đối Không Phun Thuốc Buổi Trưa:</b> Phun vào sáng sớm hoặc chiều mát tránh bốc hơi và cháy lá.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # HÀNG 2: BẢNG MA TRẬN SỐ LIỆU 12 THÁNG
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
        format_str="{:.1f}°C",
        danh_gia_fn=dg_tmax,
    )

    # HÀNG 3: KHU VỰC BẢN ĐỒ VIỄN THÁM THEO YÊU CẦU
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    _hien_khu_vuc_ban_do_ve_tinh(
        ctx,
        cot_id="lst",
        ten_lop="🌡️ Nhiệt & Gió Lào",
        ten_chi_so="NASA POWER LST",
        icon_lop="🌡️",
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
