"""Trang So sánh giữa các năm — Đối chiếu Khí hậu & Rủi ro Vụ Lúa Yên Thành.
Thiết kế đồ họa trực quan chuẩn AgTech (3 Thẻ Đối chiếu Độc lập, Hero Badges, Không méo biểu đồ).
"""
import calendar
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine as E
from views.chung import tieu_de, ve


@st.cache_data(show_spinner=False)
def _tai_daily_power():
    """Tải chuỗi dữ liệu thời tiết & viễn thám từng ngày huyện Yên Thành (2018–2026)."""
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


def ve_cot_don(x_vals, y_vals, nam_hien_tai, mau_chinh, don_vi="", fmt="{:.0f}"):
    """Tạo biểu đồ cột đơn gọn gàng, tỷ lệ cân đối, bo góc đẹp mắt cho từng chỉ số."""
    fig = go.Figure()
    
    # Màu sắc phân định theo năm
    colors = []
    for y in x_vals:
        if str(y) == str(nam_hien_tai):
            colors.append(mau_chinh)
        elif str(y) == "2025":
            colors.append("#38BDF8" if mau_chinh != "#0284C7" else "#60A5FA")
        else:
            colors.append("#CBD5E1")

    text_labels = [f"{fmt.format(v)} {don_vi}".strip() for v in y_vals]

    fig.add_trace(go.Bar(
        x=[str(y) for y in x_vals],
        y=y_vals,
        marker=dict(
            color=colors,
            cornerradius=6,
            line=dict(color="#FFFFFF", width=1.5),
        ),
        text=text_labels,
        textposition="outside",
        textfont=dict(size=12, family="Be Vietnam Pro", weight="bold", color="#0F172A"),
        hoverinfo="x+text",
    ))

    max_y = max(y_vals) if len(y_vals) and max(y_vals) > 0 else 10
    fig.update_layout(
        height=195,
        margin=dict(l=8, r=8, t=28, b=6),
        bargap=0.36,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, family="Be Vietnam Pro", weight="bold", color="#475569"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            range=[0, max_y * 1.25],
            showticklabels=False,
        ),
    )
    return fig


def hien(ctx):
    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang, years = ctx["nam"], ctx.get("thang", 4), ctx["years"]
    vung = "Yên Thành"

    # 1. TIÊU ĐỀ & BANNER THÔNG TIN TRỰC QUAN
    tieu_de(vung, thang, nam, "Đối chiếu Đa năm · Vụ Lúa Yên Thành", len(years) < 2)

    st.markdown(
        f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:10px; padding:8px 14px; margin-bottom:12px; font-size:12px; color:#1E293B; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
          <div>
            <b>📈 Phân tích Xu thế Khí hậu Đa năm ({', '.join(map(str, years))} & Chuẩn 11 năm NASA):</b> Nhận diện sớm biến động thời tiết (đỉnh nhiệt gió Lào Tây Nam, mưa bão ngập úng Kênh Vách Bắc) để chủ động thời vụ.
          </div>
          <div style="font-weight:750; color:#16A34A; background:#FFFFFF; border:1px solid #BBF7D0; border-radius:999px; padding:2px 10px; font-size:11px;">
            🌾 Vựa lúa Yên Thành
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_dot, tab_thang, tab_ngay = st.tabs([
        "🌾 Đối chiếu theo Đợt Mùa Vụ Đa Năm",
        "📈 So Sánh Chuỗi 12 Tháng Liên Tục",
        "📆 Đối Chiếu Cùng Ngày Qua Các Năm (2018–2026)",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: ĐỐI CHIẾU THEO ĐỢT MÙA VỤ GIỮA CÁC NĂM
    # -------------------------------------------------------------------------
    with tab_dot:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:6px;">'
                '🌾 Chọn Vụ mùa cần đối chiếu đa năm tại Yên Thành:'
                '</div>',
                unsafe_allow_html=True,
            )

            # BỘ CHỌN VỤ MÙA TRỰC QUAN TRÊN TOÀN CHIỀU RỘNG (KHÔNG BỊ CẮT CHỮ)
            cac_lua_chon_vu = [
                "🌾 Vụ Lúa Chiêm Xuân (Tháng 1 – Tháng 5)",
                "☀️ Vụ Lúa Hè Thu (Tháng 6 – Tháng 9)",
                "🍂 Vụ Đông / Cày Ải (Tháng 10 – Tháng 12)",
                "⚙️ Tùy chỉnh khoảng tháng",
            ]

            vu_chon = st.pills(
                "Chọn vụ mùa:",
                options=cac_lua_chon_vu,
                default=cac_lua_chon_vu[0],
                key=f"pills_vu_doi_chieu_{nam}",
                label_visibility="collapsed",
            )
            if not vu_chon:
                vu_chon = cac_lua_chon_vu[0]

            # Xử lý tham số tháng theo lựa chọn
            if "Xuân" in vu_chon:
                t_start, t_end = 1, 5
                ten_vu = "Vụ Lúa Chiêm Xuân (T1–T5)"
                mota_vu = "Vụ lúa chính số 1 Yên Thành: gieo mạ chống rét T1, trỗ rộ 20/4–5/5, gặt trước 25/5."
                ic_vu = "🌾"
            elif "Hè Thu" in vu_chon:
                t_start, t_end = 6, 9
                ten_vu = "Vụ Lúa Hè Thu (T6–T9)"
                mota_vu = "Vụ lúa chạy lụt: Xuống giống cực nhanh trước 10/6 để gặt xong trước ngày 15/9 né bão lũ."
                ic_vu = "☀️"
            elif "Đông" in vu_chon:
                t_start, t_end = 10, 12
                ten_vu = "Vụ Đông / Cày Ải Đất (T10–T12)"
                mota_vu = "Giai đoạn cải tạo đất: Cày lật sâu 18–22 cm phơi nỏ ruộng 30–45 ngày diệt triệt để nguồn nấm bệnh đạo ôn cho vụ sau."
                ic_vu = "🍂"
            else:
                # Tùy chỉnh khoảng tháng
                col_c1, col_c2, col_c3 = st.columns([2, 2, 6])
                t_start = col_c1.selectbox("Từ tháng:", range(1, 13), index=0, format_func=lambda m: f"Tháng {m}")
                t_end = col_c2.selectbox("Đến tháng:", range(1, 13), index=4, format_func=lambda m: f"Tháng {m}")
                if t_end < t_start:
                    t_end = t_start
                ten_vu = f"Giai đoạn Tháng {t_start} – Tháng {t_end}"
                mota_vu = f"Chuỗi {t_end - t_start + 1} tháng khảo sát tự chọn."
                ic_vu = "⚙️"

            # Badge thông tin vụ đang khảo sát
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:6px 12px; margin:8px 0 14px 0; font-size:12px; color:#475569; display:flex; align-items:center; gap:8px;">
                  <span style="font-size:14px;">{ic_vu}</span>
                  <div><b>Đang đối chiếu:</b> <span style="color:#0F172A; font-weight:750;">{ten_vu}</span> — {mota_vu}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # LẤY DỮ LIỆU ĐỐI CHIẾU
            df_dot_ss = E.so_sanh_dot_qua_cac_nam(dl, vung, t_start, t_end)

            if df_dot_ss.empty:
                st.warning("Chưa có đủ dữ liệu để đối chiếu giai đoạn này.")
            else:
                nam_vals = df_dot_ss["nam"].tolist()
                r_2026 = df_dot_ss[df_dot_ss.nam == nam].iloc[0] if (df_dot_ss.nam == nam).any() else df_dot_ss.iloc[-1]
                r_2025 = df_dot_ss[df_dot_ss.nam == 2025].iloc[0] if (df_dot_ss.nam == 2025).any() else None

                # -------------------------------------------------------------
                # 3 THẺ ĐỐI CHIẾU ĐỘC LẬP CAO CẤP (KHÔNG BỊ RỖNG, KHÔNG MÉO CỘT)
                # -------------------------------------------------------------
                col_1, col_2, col_3 = st.columns(3, gap="medium")

                # CARD 1: NẮNG NÓNG GIÓ LÀO >= 35°C
                with col_1, st.container(border=True):
                    val_nong = int(r_2026.get("nong35_tong", 0))
                    val_nong_25 = int(r_2025.get("nong35_tong", 0)) if r_2025 is not None else 0
                    diff_nong = val_nong - val_nong_25
                    tag_diff_nong = f"▲ +{diff_nong} ngày" if diff_nong > 0 else (f"▼ {diff_nong} ngày" if diff_nong < 0 else "Bằng năm ngoái")
                    col_tag_nong = "#DC2626" if diff_nong > 0 else "#16A34A"

                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                          <div style="font-size:13px; font-weight:800; color:#0F172A;">🔥 Nắng nóng Gió Lào ≥35°C</div>
                          <div style="font-size:11px; font-weight:750; color:{col_tag_nong}; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:999px; padding:1px 8px;">{tag_diff_nong}</div>
                        </div>
                        <div style="font-size:24px; font-weight:800; color:#0F172A; line-height:1.1;">{val_nong} <span style="font-size:13px; color:#64748B; font-weight:500;">ngày ({nam})</span></div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Biểu đồ cột đơn riêng biệt
                    fig_nong = ve_cot_don(nam_vals, df_dot_ss["nong35_tong"].tolist(), nam, "#0F172A", "ngày")
                    ve(fig_nong, che_do="co_dinh")

                    st.markdown(
                        f'<div style="font-size:11px; color:#475569; background:#F8FAFC; border-radius:6px; padding:6px 8px; margin-top:4px; line-height:1.35;">'
                        f'💡 <b>Nhận xét:</b> Có {val_nong} ngày gió Lào trong {ten_vu}. Cần dâng nước ruộng 3–5cm làm mát gốc khi trỗ.'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # CARD 2: LƯỢNG MƯA TÍCH LŨY (GPM)
                with col_2, st.container(border=True):
                    val_mua = float(r_2026.get("mua_tong_mm", 0))
                    val_mua_25 = float(r_2025.get("mua_tong_mm", 0)) if r_2025 is not None else 0
                    diff_mua = val_mua - val_mua_25
                    tag_diff_mua = f"▲ +{diff_mua:.0f} mm" if diff_mua > 0 else (f"▼ {diff_mua:.0f} mm" if diff_mua < 0 else "Bằng năm ngoái")
                    col_tag_mua = "#0284C7" if diff_mua >= 0 else "#DC2626"

                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                          <div style="font-size:13px; font-weight:800; color:#0F172A;">🌧️ Lượng mưa Tích lũy (GPM)</div>
                          <div style="font-size:11px; font-weight:750; color:{col_tag_mua}; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:999px; padding:1px 8px;">{tag_diff_mua}</div>
                        </div>
                        <div style="font-size:24px; font-weight:800; color:#0284C7; line-height:1.1;">{val_mua:.0f} <span style="font-size:13px; color:#64748B; font-weight:500;">mm ({nam})</span></div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Biểu đồ cột đơn riêng biệt
                    fig_mua = ve_cot_don(nam_vals, df_dot_ss["mua_tong_mm"].tolist(), nam, "#0284C7", "mm")
                    ve(fig_mua, che_do="co_dinh")

                    phan_tram_mua = (diff_mua / val_mua_25 * 100) if val_mua_25 > 0 else 0
                    st.markdown(
                        f'<div style="font-size:11px; color:#475569; background:#F8FAFC; border-radius:6px; padding:6px 8px; margin-top:4px; line-height:1.35;">'
                        f'💡 <b>Nguồn nước:</b> Tổng mưa {val_mua:.0f} mm ({phan_tram_mua:+.0f}% so với 2025). Cần phụ thuộc nguồn nước Ba Ra.'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # CARD 3: NHIỆT ĐỘ TMAX TRUNG BÌNH
                with col_3, st.container(border=True):
                    val_tmax = float(r_2026.get("tmax_tb", 0))
                    val_tmax_25 = float(r_2025.get("tmax_tb", 0)) if r_2025 is not None else 0
                    diff_tmax = val_tmax - val_tmax_25
                    tag_diff_tmax = f"▲ +{diff_tmax:.1f}°C" if diff_tmax > 0 else (f"▼ {diff_tmax:.1f}°C" if diff_tmax < 0 else "Bằng năm ngoái")
                    col_tag_tmax = "#EA580C" if diff_tmax > 0 else "#16A34A"

                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                          <div style="font-size:13px; font-weight:800; color:#0F172A;">🌡️ Nhiệt độ Tmax Trung bình</div>
                          <div style="font-size:11px; font-weight:750; color:{col_tag_tmax}; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:999px; padding:1px 8px;">{tag_diff_tmax}</div>
                        </div>
                        <div style="font-size:24px; font-weight:800; color:#EA580C; line-height:1.1;">{val_tmax:.1f}° <span style="font-size:13px; color:#64748B; font-weight:500;">C ({nam})</span></div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Biểu đồ cột đơn riêng biệt
                    fig_tmax = ve_cot_don(nam_vals, df_dot_ss["tmax_tb"].tolist(), nam, "#EA580C", "°C", "{:.1f}")
                    ve(fig_tmax, che_do="co_dinh")

                    st.markdown(
                        f'<div style="font-size:11px; color:#475569; background:#F8FAFC; border-radius:6px; padding:6px 8px; margin-top:4px; line-height:1.35;">'
                        f'💡 <b>Nhiệt học:</b> Nền nhiệt TB {val_tmax:.1f}°C. Đỉnh nhiệt đo được trong đợt đạt {r_2026.get("tmax_max", 0):.1f}°C.'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # -------------------------------------------------------------
                # 4. BẢNG TỔNG HỢP SỐ LIỆU ĐA NĂM DẠNG CARD CHUYÊN NGHIỆP
                # -------------------------------------------------------------
                st.write("")
                with st.expander("📋 Xem Bảng Tổng Hợp Chi Tiết Đa Năm (Đối Chiếu Toàn Diện)", expanded=False):
                    table_rows = ""
                    for _, row in df_dot_ss.iterrows():
                        y = int(row["nam"])
                        is_current = (y == nam)
                        row_bg = "#F8FAFC" if not is_current else "#EFF6FF"
                        border_stl = "border-left:4px solid #0284C7;" if is_current else ""
                        badge_current = '<span style="background:#0284C7; color:#FFFFFF; font-size:10px; font-weight:750; border-radius:999px; padding:1px 6px; margin-left:6px;">Hiện tại</span>' if is_current else ""

                        table_rows += f"""
                        <tr style="background:{row_bg}; {border_stl} border-bottom:1px solid #E2E8F0;">
                          <td style="padding:10px 12px; font-weight:800; color:#0F172A;">Năm {y} {badge_current}</td>
                          <td style="padding:10px 12px; text-align:center; font-weight:700; color:#DC2626;">{row['nong35_tong']:.0f} ngày</td>
                          <td style="padding:10px 12px; text-align:center; font-weight:700; color:#0284C7;">{row['mua_tong_mm']:.0f} mm</td>
                          <td style="padding:10px 12px; text-align:center; font-weight:700; color:#EA580C;">{row['tmax_tb']:.1f}°C</td>
                          <td style="padding:10px 12px; text-align:center; font-weight:700; color:#991B1B;">{row.get('tmax_max', 0):.1f}°C</td>
                          <td style="padding:10px 12px; text-align:center; font-weight:600; color:#475569;">{row.get('nuoc_con_mm', 0):.0f} mm</td>
                          <td style="padding:10px 12px; text-align:center; font-weight:700; color:#16A34A;">{row.get('sm_tb', 0):.0f}%</td>
                        </tr>
                        """

                    st.markdown(
                        f"""
                        <div style="overflow-x:auto; border-radius:8px; border:1px solid #E2E8F0; margin-top:4px;">
                          <table style="width:100%; border-collapse:collapse; font-size:12px; font-family:'Be Vietnam Pro',sans-serif;">
                            <thead>
                              <tr style="background:#F1F5F9; color:#475569; text-transform:uppercase; font-size:10.5px; letter-spacing:0.04em;">
                                <th style="padding:8px 12px; text-align:left;">Năm Khảo Sát</th>
                                <th style="padding:8px 12px; text-align:center;">Gió Lào ≥35°C</th>
                                <th style="padding:8px 12px; text-align:center;">Lượng Mưa Tích Lũy</th>
                                <th style="padding:8px 12px; text-align:center;">Tmax Trung Bình</th>
                                <th style="padding:8px 12px; text-align:center;">Tmax Đỉnh Điểm</th>
                                <th style="padding:8px 12px; text-align:center;">Cán Cân Ẩm</th>
                                <th style="padding:8px 12px; text-align:center;">Độ Ẩm Đất Rễ</th>
                              </tr>
                            </thead>
                            <tbody>
                              {table_rows}
                            </tbody>
                          </table>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # -------------------------------------------------------------------------
    # TAB 2: SO SÁNH CHUỖI 12 THÁNG
    # -------------------------------------------------------------------------
    with tab_thang:
        CH = {
            "🌡️ Nhiệt độ Tmax (°C)": ("tmax", "°C", "#EA580C"),
            "🌧️ Lượng mưa GPM (mm)": ("mua_mm", "mm", "#0284C7"),
            "🔥 Gió Lào ≥35°C (ngày)": ("nong35", "ngày", "#DC2626"),
            "💧 Độ ẩm ruộng SMAP (%)": ("sm_rootzone", "%", "#10B981"),
            "🌿 Sinh khối NDVI": ("ndvi", "", "#16A34A"),
            "⚖️ Cán cân ẩm ròng (mm)": ("nuoc_con_lai_mm", "mm", "#0F172A"),
        }
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:6px;">'
                '📈 Biểu đồ Chuỗi Thời Gian 12 Tháng Đối Chiếu Qua Các Năm:'
                '</div>',
                unsafe_allow_html=True,
            )

            chon = st.pills(
                "Chọn chỉ số viễn thám:",
                list(CH.keys()),
                default=list(CH.keys())[0],
                key=f"pills_so_sanh_thang_{nam}",
                label_visibility="collapsed",
            )
            if not chon:
                chon = list(CH.keys())[0]

            cot, don_vi_chon, col_chinh = CH[chon]

            f = go.Figure()
            colors_year = {2026: "#0F172A", 2025: "#0284C7", 2024: "#94A3B8"}
            styles_year = {2026: dict(width=3.5), 2025: dict(width=2.5), 2024: dict(width=1.8, dash="dot")}

            for y in years:
                q = dl[(dl.huyen == vung) & (dl.year == y)].sort_values("month")
                if cot not in q.columns:
                    continue
                col_line = colors_year.get(y, "#64748B")
                style_line = styles_year.get(y, dict(width=2))
                y_series = q[cot] * (100 if cot == "sm_rootzone" else 1)
                
                f.add_scatter(
                    x=[f"T{int(m)}" for m in q.month],
                    y=y_series,
                    name=f"Năm {y} {'(Khảo sát)' if y == nam else ''}".strip(),
                    mode="lines+markers",
                    line=dict(color=col_line, **style_line),
                    marker=dict(size=8 if y == nam else 5),
                    text=[f"{v:.1f} {don_vi_chon}".strip() for v in y_series],
                    hoverinfo="name+x+text",
                )

            # Vùng highlight tháng then chốt vụ mùa
            f.add_vrect(x0=2.5, x1=4.5, fillcolor="#FEF3C7", opacity=0.15, line_width=0, annotation_text="Trỗ bông xuân", annotation_position="top left", annotation_font_size=10)
            f.add_vrect(x0=7.5, x1=8.5, fillcolor="#FEE2E2", opacity=0.15, line_width=0, annotation_text="Lũ tiểu mãn", annotation_position="top left", annotation_font_size=10)

            f.update_layout(
                height=320,
                margin=dict(l=8, r=8, t=18, b=8),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.14, x=0),
                xaxis=dict(gridcolor="#F1F5F9", showgrid=True),
                yaxis=dict(gridcolor="#F1F5F9", showgrid=True, title=dict(text=don_vi_chon, font=dict(size=11))),
            )
            ve(f, che_do="tuong_tac")

        if len(diem):
            with st.container(border=True):
                st.markdown(
                    f'<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:6px;">🌾 Mức Khuyến Nghị Cây Trồng Tại Tháng {thang} Qua Các Năm (Yên Thành)</div>',
                    unsafe_allow_html=True,
                )
                q = diem[(diem.huyen == vung) & (diem.month == thang)].pivot(index="cay", columns="year", values="muc")
                q.index.name = "Cây trồng"
                try:
                    st.dataframe(q, width="stretch")
                except TypeError:
                    st.dataframe(q, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: ĐỐI CHIẾU CÙNG NGÀY QUA CÁC NĂM (DAY-OF-YEAR COMPARISON 2018–2026)
    # -------------------------------------------------------------------------
    with tab_ngay:
        df_daily = _tai_daily_power()
        if df_daily.empty:
            st.error("Chưa có chuỗi số liệu thời tiết viễn thám từng ngày (data/raw/power/power_Yen_Thanh.csv).")
        else:
            min_date = df_daily["date_dt"].dt.date.min()
            max_date = df_daily["date_dt"].dt.date.max()

            key_d_ss = "date_pick_so_sanh"
            if key_d_ss not in st.session_state or not isinstance(st.session_state[key_d_ss], datetime.date):
                st.session_state[key_d_ss] = datetime.date(2026, 4, 15)

            with st.container(border=True):
                st.markdown(
                    '<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
                    '🔍 Chọn Ngày Mốc Khảo Sát Để Đối Chiếu Đa Năm (2018–2026):'
                    '</div>'
                    '<div style="font-size:11.5px; color:#64748B; margin-bottom:8px;">'
                    'Xem cùng một ngày lịch (ví dụ ngày 15/04 hoặc 22/06) đã diễn biến thời tiết, nhiệt độ và mưa như thế nào qua tất cả các năm lịch sử.'
                    '</div>',
                    unsafe_allow_html=True,
                )

                c_d1, c_d2 = st.columns([4.0, 8.0], gap="small")
                with c_d1:
                    ngay_moc = st.date_input(
                        "Ngày mốc đối chiếu:",
                        value=st.session_state[key_d_ss],
                        min_value=min_date,
                        max_value=max_date,
                        key="widget_date_pick_so_sanh",
                        format="DD/MM/YYYY",
                        label_visibility="collapsed",
                    )
                    if ngay_moc:
                        st.session_state[key_d_ss] = ngay_moc
                with c_d2:
                    st.markdown('<div style="font-size:11px; font-weight:750; color:#475569; margin-bottom:3px;">⚡ ĐIỂM MỐC THỜI TIẾT CỰC ĐOAN:</div>', unsafe_allow_html=True)
                    sb1, sb2, sb3 = st.columns(3, gap="small")
                    with sb1:
                        if st.button("🌸 Trỗ lúa xuân (15/04)", key="btn_ss_xuan", use_container_width=True):
                            st.session_state[key_d_ss] = datetime.date(2026, 4, 15)
                            st.rerun()
                    with sb2:
                        if st.button("🔥 Đỉnh hạn 2019 (22/06)", key="btn_ss_han", use_container_width=True):
                            st.session_state[key_d_ss] = datetime.date(2019, 6, 22)
                            st.rerun()
                    with sb3:
                        if st.button("🌊 Đỉnh lũ 2020 (19/10)", key="btn_ss_lu", use_container_width=True):
                            st.session_state[key_d_ss] = datetime.date(2020, 10, 19)
                            st.rerun()

            cur_moc = st.session_state[key_d_ss]
            d_target = cur_moc.day
            m_target = cur_moc.month

            # Lọc dữ liệu cùng ngày (d_target, m_target) qua các năm
            df_cung_ngay = df_daily[(df_daily["month"] == m_target) & (df_daily["day"] == d_target)].sort_values("year")

            if df_cung_ngay.empty:
                st.warning(f"Không có dữ liệu đối chiếu cho ngày {d_target:02d}/{m_target:02d}.")
            else:
                x_years = [str(y) for y in df_cung_ngay["year"]]
                tmax_vals = df_cung_ngay["T2M_MAX"].tolist()
                mua_vals = [float(v) if pd.notna(v) else 0.0 for v in df_cung_ngay["PRECTOTCORR"]]
                rad_vals = [float(v) if pd.notna(v) else 0.0 for v in df_cung_ngay["ALLSKY_SFC_SW_DWN"]]

                st.markdown(
                    f'<div style="font-size:12.5px; font-weight:800; color:#0F172A; margin:10px 0 6px 0;">'
                    f'📊 Đối Chiếu Cùng Ngày <b style="color:#0F766E;">{d_target:02d}/{m_target:02d}</b> Qua 9 Năm (2018–2026) Tại Yên Thành:'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                c_ss1, c_ss2, c_ss3 = st.columns(3, gap="small")

                with c_ss1, st.container(border=True):
                    st.markdown(
                        '<div style="font-size:13px; font-weight:800; color:#EA580C; margin-bottom:4px;">🌡️ Nhiệt độ Tmax (°C)</div>',
                        unsafe_allow_html=True,
                    )
                    fig_tmax_day = ve_cot_don(x_years, tmax_vals, str(cur_moc.year), "#EA580C", "°C", "{:.1f}")
                    ve(fig_tmax_day, che_do="co_dinh")

                with c_ss2, st.container(border=True):
                    st.markdown(
                        '<div style="font-size:13px; font-weight:800; color:#0284C7; margin-bottom:4px;">🌧️ Lượng mưa ngày (mm)</div>',
                        unsafe_allow_html=True,
                    )
                    fig_mua_day = ve_cot_don(x_years, mua_vals, str(cur_moc.year), "#0284C7", "mm", "{:.1f}")
                    ve(fig_mua_day, che_do="co_dinh")

                with c_ss3, st.container(border=True):
                    st.markdown(
                        '<div style="font-size:13px; font-weight:800; color:#D97706; margin-bottom:4px;">☀️ Bức xạ mặt trời (MJ/m²)</div>',
                        unsafe_allow_html=True,
                    )
                    fig_rad_day = ve_cot_don(x_years, rad_vals, str(cur_moc.year), "#D97706", "MJ", "{:.1f}")
                    ve(fig_rad_day, che_do="co_dinh")

                # Bảng chi tiết
                with st.expander(f"📋 Bảng số liệu chi tiết ngày {d_target:02d}/{m_target:02d} qua 9 năm (2018–2026)", expanded=False):
                    tbl_day = df_cung_ngay[["year", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M"]].copy()
                    tbl_day.columns = ["Năm", "Tmax (°C)", "Tmin (°C)", "Mưa (mm)", "Độ ẩm (%)", "Bức xạ (MJ/m²)", "Tốc độ gió (m/s)"]
                    try:
                        st.dataframe(tbl_day.sort_values("Năm", ascending=False), hide_index=True, width="stretch")
                    except TypeError:
                        st.dataframe(tbl_day.sort_values("Năm", ascending=False), hide_index=True, use_container_width=True)
