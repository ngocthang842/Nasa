"""Trang So sánh giữa các năm — Đối chiếu Khí hậu & Rủi ro Vụ Lúa Yên Thành.
Thiết kế đồ họa trực quan (Visual Cards, Pills & Data Badges - No Walls of Text).
"""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import engine as E
from views.chung import tieu_de, ve


def hien(ctx):
    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang, years = ctx["nam"], ctx.get("thang", 4), ctx["years"]
    vung = "Yên Thành"

    # TIÊU ĐỀ & BANNER THÔNG TIN TRỰC QUAN
    tieu_de(vung, thang, nam, "Đối chiếu Đa năm · Vụ Lúa Yên Thành", len(years) < 2)

    st.markdown(
        f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:8px 12px; margin-bottom:12px; font-size:12px; color:#1E293B; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
          <div>
            <b>📈 Phân tích Xu thế Khí tượng Đa năm:</b> Đối chiếu chuỗi số liệu ({', '.join(map(str, years))}) và chuẩn 11 năm NASA để nhận diện sớm đỉnh nhiệt Gió Lào và bão lũ tháng 9.
          </div>
          <div style="font-weight:750; color:#16A34A; background:#FFFFFF; border:1px solid #BBF7D0; border-radius:999px; padding:2px 10px; font-size:11px;">
            Vựa lúa Yên Thành
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_dot, tab_thang = st.tabs([
        "🌾 Đối chiếu theo Đợt mùa vụ giữa các năm",
        "📈 So sánh chuỗi 12 tháng liên tục"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: ĐỐI CHIẾU THEO ĐỢT MÙA VỤ GIỮA CÁC NĂM
    # -------------------------------------------------------------------------
    with tab_dot:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:6px;">🌾 Chọn Vụ mùa cần đối chiếu đa năm tại Yên Thành</div>',
                unsafe_allow_html=True,
            )

            col_kieu, col_sel = st.columns([1, 1], gap="medium")

            kieu_chia = col_kieu.pills(
                "Phân chia mùa vụ:",
                [
                    "2 vụ lúa chính (Xuân & Hè Thu)",
                    "3 đợt (Xuân, Hè Thu, Vụ Đông)",
                    "Tùy chỉnh khoảng tháng",
                ],
                default="2 vụ lúa chính (Xuân & Hè Thu)",
                key=f"so_sanh_kieu_chia_pills_{E.khoa(vung)}_{nam}",
                label_visibility="collapsed",
            )
            if not kieu_chia:
                kieu_chia = "2 vụ lúa chính (Xuân & Hè Thu)"

            if kieu_chia == "Tùy chỉnh khoảng tháng":
                c_s, c_e = col_sel.columns(2)
                t_start = c_s.selectbox("Từ tháng:", range(1, 13), index=0, format_func=lambda m: f"T{m}")
                t_end = c_e.selectbox("Đến tháng:", range(1, 13), index=4, format_func=lambda m: f"T{m}")
                if t_end < t_start:
                    t_end = t_start
                dot_ss = {
                    "ten": f"Khoảng Tháng {t_start} – Tháng {t_end}",
                    "so_thang": t_end - t_start + 1,
                    "thang_bat_dau": t_start,
                    "thang_ket_thuc": t_end,
                    "dac_trung": f"Chuỗi {t_end - t_start + 1} tháng tự chọn của người dùng.",
                    "icon": "⚙️",
                }
            elif "2 vụ lúa" in kieu_chia:
                cac_dot = [
                    {
                        "ten": "Vụ Lúa Xuân (Tháng 1 – Tháng 5)",
                        "so_thang": 5, "thang_bat_dau": 1, "thang_ket_thuc": 5, "icon": "🌾",
                        "dac_trung": "Vụ lúa chính: Gieo cấy, đẻ nhánh, trỗ bông, thu hoạch hoàn thành trước 25/5.",
                    },
                    {
                        "ten": "Vụ Lúa Hè Thu (Tháng 6 – Tháng 9)",
                        "so_thang": 4, "thang_bat_dau": 6, "thang_ket_thuc": 9, "icon": "☀️",
                        "dac_trung": "Vụ lúa hè thu: Cần xuống giống sớm trước 10/6 để gặt chạy lụt trước ngày 15/9.",
                    },
                ]
                danh_sach_ten = [f"{d['icon']} {d['ten']}" for d in cac_dot]
                dot_chon_idx = col_sel.selectbox(
                    "Chọn vụ để đối chiếu:",
                    range(len(cac_dot)),
                    format_func=lambda i: danh_sach_ten[i],
                    key=f"so_sanh_dot_idx_{E.khoa(vung)}_{nam}",
                    label_visibility="collapsed",
                )
                dot_ss = cac_dot[dot_chon_idx]
            else:
                cac_dot = E.tinh_toan_cac_dot("3 đợt")
                danh_sach_ten = [f"{d['icon']} {d['ten']}" for d in cac_dot]
                dot_chon_idx = col_sel.selectbox(
                    "Chọn vụ để đối chiếu:",
                    range(len(cac_dot)),
                    format_func=lambda i: danh_sach_ten[i],
                    key=f"so_sanh_dot_idx_{E.khoa(vung)}_{nam}",
                    label_visibility="collapsed",
                )
                dot_ss = cac_dot[dot_chon_idx]

            t_start, t_end = dot_ss["thang_bat_dau"], dot_ss["thang_ket_thuc"]

            # BẢNG DỮ LIỆU ĐỐI CHIẾU
            df_dot_ss = E.so_sanh_dot_qua_cac_nam(dl, vung, t_start, t_end)

            if df_dot_ss.empty:
                st.warning("Chưa có đủ dữ liệu để đối chiếu đợt này.")
            else:
                st.write("")
                st.markdown(
                    f'<div style="font-size:13px; font-weight:750; color:#0F172A; margin-bottom:4px;">📊 So sánh 3 Chỉ số Khí tượng Cốt lõi trong {dot_ss["ten"]} qua các năm:</div>',
                    unsafe_allow_html=True,
                )

                # 3 Biểu đồ cột bo góc hiện đại
                fig_dot = make_subplots(
                    rows=1,
                    cols=3,
                    subplot_titles=(
                        f"🔥 Nắng nóng ≥35°C ({dot_ss['so_thang']} tháng)",
                        f"🌧️ Tổng Mưa ({dot_ss['so_thang']} tháng)",
                        f"🌡️ Tmax Trung bình ({dot_ss['so_thang']} tháng)",
                    ),
                )

                nam_str = [str(y) for y in df_dot_ss["nam"]]

                fig_dot.add_trace(
                    go.Bar(
                        x=nam_str,
                        y=df_dot_ss["nong35_tong"],
                        name="Ngày ≥35°C",
                        marker=dict(
                            color=["#0F172A" if y == nam else "#CBD5E1" for y in df_dot_ss["nam"]],
                            cornerradius=4,
                        ),
                        text=df_dot_ss["nong35_tong"],
                        textposition="outside",
                    ),
                    row=1, col=1,
                )

                fig_dot.add_trace(
                    go.Bar(
                        x=nam_str,
                        y=df_dot_ss["mua_tong_mm"],
                        name="Mưa (mm)",
                        marker=dict(
                            color=["#0284C7" if y == nam else "#BAE6FD" for y in df_dot_ss["nam"]],
                            cornerradius=4,
                        ),
                        text=[f"{v:.0f}" for v in df_dot_ss["mua_tong_mm"]],
                        textposition="outside",
                    ),
                    row=1, col=2,
                )

                fig_dot.add_trace(
                    go.Bar(
                        x=nam_str,
                        y=df_dot_ss["tmax_tb"],
                        name="Tmax TB (°C)",
                        marker=dict(
                            color=["#F97316" if y == nam else "#FED7AA" for y in df_dot_ss["nam"]],
                            cornerradius=4,
                        ),
                        text=[f"{v:.1f}°" for v in df_dot_ss["tmax_tb"]],
                        textposition="outside",
                    ),
                    row=1, col=3,
                )

                fig_dot.update_layout(
                    height=280,
                    margin=dict(l=8, r=8, t=28, b=8),
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                ve(fig_dot, che_do="co_dinh")

                # Bảng chi tiết gọn gàng bên dưới
                with st.expander("📋 Xem Bảng Số liệu Chi tiết Đa năm", expanded=False):
                    df_hien_thi = df_dot_ss.copy()
                    df_hien_thi.columns = [
                        "Năm", "Số tháng", "Tmax TB (°C)", "Tmax Đỉnh (°C)",
                        "Số ngày ≥35°C (Gió Lào)", "Tổng Mưa (mm)", "Cán cân Nước (mm)", "Ẩm đất TB (%)",
                    ]
                    try:
                        st.dataframe(df_hien_thi.set_index("Năm"), width="stretch")
                    except TypeError:
                        st.dataframe(df_hien_thi.set_index("Năm"), use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 2: SO SÁNH CHUỖI 12 THÁNG
    # -------------------------------------------------------------------------
    with tab_thang:
        CH = {
            "🌡️ Nhiệt độ Tmax": "tmax",
            "🌧️ Lượng mưa GPM": "mua_mm",
            "🔥 Gió Lào ≥35°C": "nong35",
            "💧 Độ ẩm ruộng SMAP": "sm_rootzone",
            "🌿 Sinh khối NDVI": "ndvi",
            "⚖️ Cán cân ẩm ròng": "nuoc_con_lai_mm",
        }
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:6px;">📈 Biểu đồ Đường Chuỗi Thời gian 12 Tháng tại Yên Thành</div>',
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

            cot = CH[chon]

            f = go.Figure()
            colors_year = {2026: "#0F172A", 2025: "#0284C7", 2024: "#94A3B8"}
            for y in years:
                q = dl[(dl.huyen == vung) & (dl.year == y)].sort_values("month")
                if cot not in q.columns:
                    continue
                col_line = colors_year.get(y, "#64748B")
                f.add_scatter(
                    x=[f"T{int(m)}" for m in q.month],
                    y=q[cot],
                    name=f"Năm {y}",
                    mode="lines+markers",
                    line=dict(width=3.5 if y == nam else 2, color=col_line),
                    marker=dict(size=8 if y == nam else 5),
                )
            f.update_layout(
                height=320,
                margin=dict(l=8, r=8, t=8, b=8),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.12),
                xaxis=dict(gridcolor="#F1F5F9"),
                yaxis=dict(gridcolor="#F1F5F9"),
            )
            ve(f, che_do="tuong_tac")

        if len(diem):
            with st.container(border=True):
                st.markdown(
                    f'<div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">🌾 Mức khuyến nghị cây trồng tại Tháng {thang} qua các năm (Yên Thành)</div>',
                    unsafe_allow_html=True,
                )
                q = diem[(diem.huyen == vung) & (diem.month == thang)].pivot(index="cay", columns="year", values="muc")
                q.index.name = "Cây trồng"
                try:
                    st.dataframe(q, width="stretch")
                except TypeError:
                    st.dataframe(q, use_container_width=True)
