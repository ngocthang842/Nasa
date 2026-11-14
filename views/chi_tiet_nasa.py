"""Các trang chuyên sâu theo từng chỉ số Viễn thám NASA (NDVI, SMAP, GPM, LST, Công thức, API).
Phục vụ điều hướng chuyên nghiệp khớp 100% với Dashboard Hệ thống Phân tích Môi trường NASA (NEDA).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine as E
from views import luan_canh, so_sanh, du_lieu
from views.ban_do import hien_ban_do
from views.ve_tinh import hien_ve_tinh
from views.chung import tieu_de, ve, kpi_the


def _ve_chuoi_thoi_gian_don(df_thang, cot, tieu_de_bieu_do, mau_chinh, don_vi=""):
    """Vẽ biểu đồ đường chuỗi 12 tháng so sánh giữa các năm (2024, 2025, 2026)."""
    fig = go.Figure()
    nam_colors = {2026: mau_chinh, 2025: "#0284C7", 2024: "#94A3B8"}
    nam_styles = {2026: dict(width=3.5), 2025: dict(width=2.2), 2024: dict(width=1.6, dash="dot")}
    
    for y in sorted(df_thang.year.unique()):
        sub = df_thang[df_thang.year == y].sort_values("month")
        if cot not in sub.columns:
            continue
        y_data = sub[cot] * (100 if cot == "sm_rootzone" else 1)
        fig.add_scatter(
            x=[f"T{int(m)}" for m in sub.month],
            y=y_data,
            name=f"Năm {y}",
            mode="lines+markers",
            line=dict(color=nam_colors.get(y, "#64748B"), **nam_styles.get(y, {})),
            marker=dict(size=8 if y == 2026 else 5),
            text=[f"{v:.1f} {don_vi}".strip() for v in y_data],
            hoverinfo="name+x+text",
        )
    fig.update_layout(
        title=dict(text=tieu_de_bieu_do, font=dict(size=13, family="Be Vietnam Pro", weight="bold", color="#0F172A")),
        height=260,
        margin=dict(l=8, r=8, t=32, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.14, x=0),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title=dict(text=don_vi, font=dict(size=11))),
    )
    return fig


# -----------------------------------------------------------------------------
# 1. 🍃 PHÂN TÍCH THẢM THỰC VẬT (NDVI)
# -----------------------------------------------------------------------------
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
        1: ("🌱 Mạ non & Cấy lúa Xuân", "NDVI thấp (0.2–0.3), ruộng ngập nước mạ mới bén."),
        2: ("🌿 Đẻ nhánh rộ", "NDVI tăng nhanh (0.45–0.60), sinh khối lá phát triển mạnh."),
        3: ("🌾 Làm đòng & Ôm bòng", "NDVI đạt đỉnh cao (0.70–0.85), thảm phủ xanh kín mặt ruộng."),
        4: ("🌸 Trỗ bông rộ", "NDVI duy trì mức cao (0.65–0.78), lúa bắt đầu vào mẩy."),
        5: ("✨ Chín vàng & Thu hoạch", "NDVI giảm (0.35–0.50) do lá vàng và gặt rơm rạ."),
        6: ("🌱 Xuống giống Hè Thu", "NDVI thấp (0.2–0.35), cấy chạy lũ tiểu mãn."),
        7: ("🌿 Đẻ nhánh Hè Thu", "NDVI tăng nhanh (0.50–0.65) vượt đỉnh nhiệt gió Lào."),
        8: ("🌾 Làm đòng & Trỗ Hè Thu", "NDVI đạt 0.70–0.80 trước mùa bão."),
        9: ("🌊 Gặt né lũ & Ngập Kênh Vách Bắc", "NDVI giảm nhanh sau khi gặt chạy lũ."),
        10: ("🚜 Cày ải đất & Rau màu vụ đông", "NDVI vùng lúa thấp (0.25), vùng ngô/lạc đạt 0.55."),
        11: ("☀️ Phơi nỏ ruộng vụ đông", "Đất khô ải, chuẩn bị lấy nước."),
        12: ("💧 Lấy nước đổ ải vụ xuân", "Ruộng đầy nước phù sa sông Lam."),
    }
    gd_ten, gd_mota = giai_doan_dict.get(thang, ("Giai đoạn sinh trưởng lúa", "Giám sát viễn thám"))

    c1, c2, c3 = st.columns([3, 5, 4])
    with c1, st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:750; color:#64748B;">CHỈ SỐ NDVI HIỆN TẠI</div>
            <div style="font-size:32px; font-weight:800; color:#16A34A; line-height:1.1;">{cur_ndvi:.2f}</div>
            <div style="font-size:12px; color:#475569; margin-top:4px;"><b>Tháng {thang}/{nam}</b> · Vựa lúa Yên Thành</div>
            <hr style="margin:8px 0; border-color:#E2E8F0;">
            <div style="font-size:12px; color:#1E293B;"><b>{gd_ten}</b></div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">{gd_mota}</div>
            """,
            unsafe_allow_html=True,
        )
    with c2, st.container(border=True):
        fig_ndvi = _ve_chuoi_thoi_gian_don(dl_yt, "ndvi", "Biểu đồ Chuỗi Thời gian 12 Tháng NDVI MODIS", "#16A34A", "NDVI")
        ve(fig_ndvi, che_do="tuong_tac")
    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">🔬 Thang Đo Sức Khỏe Lúa NDVI</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:6px 10px; border-radius:6px;">
                <b>🟢 NDVI > 0.70 (Rất tốt):</b> Lúa trỗ đều, sinh khối khỏe, tán lá che kín đất.
              </div>
              <div style="background:#FEFCE8; border:1px solid #FEF08A; border-left:4px solid #EAB308; padding:6px 10px; border-radius:6px;">
                <b>🟡 NDVI 0.40–0.70 (Trung bình):</b> Giai đoạn mạ/đẻ nhánh non hoặc lúa sắp chín.
              </div>
              <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; padding:6px 10px; border-radius:6px;">
                <b>🔴 NDVI < 0.40 (Thấp / Báo động):</b> Đất phơi ải, ruộng trũng ngập úng hoặc bị táp khô do gió Lào.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Bản đồ vệ tinh phủ lớp NDVI
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:8px;">🛰️ Bản đồ Viễn thám Sinh thái & Phân bố NDVI Lúa Yên Thành</div>',
            unsafe_allow_html=True,
        )
        ctx_sub = dict(ctx)
        ctx_sub["lop_hien_tai"] = "🌿 Sức khỏe Lúa (NDVI)"
        hien_ve_tinh(ctx_sub)


# -----------------------------------------------------------------------------
# 2. 💧 ĐỘ ẨM ĐẤT (SMAP)
# -----------------------------------------------------------------------------
def hien_do_am(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Giám sát Độ Ẩm Đất & Cân bằng Nước Ruộng Lúa (SMAP L-band)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_sm = float(r_thang["sm_rootzone"].iloc[0] * 100) if not r_thang.empty and "sm_rootzone" in r_thang.columns else 28.0

    c1, c2, c3 = st.columns([3, 5, 4])
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
        fig_sm = _ve_chuoi_thoi_gian_don(dl_yt, "sm_rootzone", "Biểu đồ Độ Ẩm Đất Tầng Rễ 12 Tháng (SMAP)", "#0284C7", "%")
        ve(fig_sm, che_do="tuong_tac")
    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">💧 Điều tiết Nước theo Địa hình Yên Thành</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #0284C7; padding:6px 10px; border-radius:6px;">
                <b>Vùng Trũng Lòng Chảo (Bảo Thành, Vĩnh Thành):</b> Nguy cơ ngập úng cao khi mưa lớn dồn về Kênh Vách Bắc.
              </div>
              <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #D97706; padding:6px 10px; border-radius:6px;">
                <b>Vùng Vàn Cao (Mỹ Thành, Tân Thành):</b> Dốc thoải, dễ mất nước khi có gió Lào, cần tích nước hồ đập cục bộ.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:8px;">🛰️ Bản đồ Độ Ẩm Đất Không gian Vệ tinh NASA SMAP</div>',
            unsafe_allow_html=True,
        )
        ctx_sub = dict(ctx)
        ctx_sub["lop_hien_tai"] = "💧 Độ ẩm Ruộng (SMAP)"
        hien_ve_tinh(ctx_sub)


# -----------------------------------------------------------------------------
# 3. 🌧️ LƯỢNG MƯA (GPM)
# -----------------------------------------------------------------------------
def hien_luong_mua(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Giám sát Lượng Mưa Tích Lũy & Bão Lũ (NASA GPM IMERG)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_mua = float(r_thang["mua_mm"].iloc[0]) if not r_thang.empty and "mua_mm" in r_thang.columns else 85.0

    c1, c2, c3 = st.columns([3, 5, 4])
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
        fig_mua = _ve_chuoi_thoi_gian_don(dl_yt, "mua_mm", "Biểu đồ Vũ lượng 12 Tháng Chuỗi Đa Năm (GPM IMERG)", "#0284C7", "mm")
        ve(fig_mua, che_do="tuong_tac")
    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">🌊 Năng Lực Tiêu Úng Kênh Vách Bắc</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:6px 10px; border-radius:6px;">
                <b>Tháng 1–5 (Mùa khô - Chiêm Xuân):</b> Lượng mưa trung bình thấp (40–120 mm/tháng), phụ thuộc nước tưới Ba Ra.
              </div>
              <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; padding:6px 10px; border-radius:6px;">
                <b>Tháng 9–10 (Mùa lũ lớn):</b> Mưa bão dồn dập, lưu lượng nước đổ về vùng lòng chảo Yên Thành cực lớn, cần mở thông các cống tiêu ra biển Diễn Châu.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:8px;">🛰️ Bản đồ Vũ lượng Mưa Vệ tinh GPM IMERG</div>',
            unsafe_allow_html=True,
        )
        ctx_sub = dict(ctx)
        ctx_sub["lop_hien_tai"] = "🌧️ Lượng mưa (GPM)"
        hien_ve_tinh(ctx_sub)


# -----------------------------------------------------------------------------
# 4. 🌡️ NHIỆT ĐỘ BỀ MẶT (LST & TMAX)
# -----------------------------------------------------------------------------
def hien_nhiet_do(ctx):
    dl = ctx["dl"]
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Giám sát Nhiệt độ Bề mặt LST & Gió Lào Tây Nam (NASA POWER)", False)

    dl_yt = dl[dl.huyen == vung]
    r_thang = dl_yt[(dl_yt.year == nam) & (dl_yt.month == thang)]
    cur_tmax = float(r_thang["tmax"].iloc[0]) if not r_thang.empty and "tmax" in r_thang.columns else 32.5
    cur_nong = int(r_thang["nong35"].iloc[0]) if not r_thang.empty and "nong35" in r_thang.columns else 5

    c1, c2, c3 = st.columns([3, 5, 4])
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
        fig_tmax = _ve_chuoi_thoi_gian_don(dl_yt, "tmax", "Biểu đồ Nhiệt độ Tmax 12 Tháng Đối Chiếu Đa Năm", "#EA580C", "°C")
        ve(fig_tmax, che_do="tuong_tac")
    with c3, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:6px;">🛡️ Mệnh Lệnh Canh Tác Chống Nóng</div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px;">
              <div style="background:#FFF7ED; border:1px solid #FFEDD5; border-left:4px solid #EA580C; padding:6px 10px; border-radius:6px;">
                <b>Giữ Mực Nước Đệm 3–5 cm:</b> Dâng nước làm mát gốc lúa, điều hòa nhiệt vi khí hậu ruộng đồng khi gió Lào thổi mạnh.
              </div>
              <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444; padding:6px 10px; border-radius:6px;">
                <b>Tuyệt Đối Không Phun Thuốc Buổi Trưa:</b> Phun phòng đạo ôn và sâu bệnh vào sáng sớm hoặc chiều mát để tránh bay hơi và cháy lá.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown(
            '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:8px;">🛰️ Bản đồ Nhiệt độ & Bức xạ Vệ tinh NASA POWER</div>',
            unsafe_allow_html=True,
        )
        ctx_sub = dict(ctx)
        ctx_sub["lop_hien_tai"] = "🌡️ Nhiệt & Gió Lào"
        hien_ve_tinh(ctx_sub)


# -----------------------------------------------------------------------------
# 5. ƒx CÔNG THỨC & THUẬT TOÁN
# -----------------------------------------------------------------------------
def hien_cong_thuc_thuat_toan(ctx):
    nam, thang = ctx["nam"], ctx.get("thang", 4)
    vung = "Yên Thành"
    tieu_de(vung, thang, nam, "Công thức Viễn thám & Thuật toán Ra Quyết định Mùa Vụ", False)

    tab_ct, tab_lc, tab_ss = st.tabs([
        "🧮 Bảng Công thức Viễn thám NASA",
        "🌾 Thuật toán Tối ưu hóa Luân canh Cây trồng",
        "📈 Thuật toán Phân tích Đối chiếu Đa năm"
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

    with tab_lc:
        luan_canh.hien(ctx)

    with tab_ss:
        so_sanh.hien(ctx)


# -----------------------------------------------------------------------------
# 6. 📥 TẢI DỮ LIỆU API
# -----------------------------------------------------------------------------
def hien_tai_du_lieu_api(ctx):
    du_lieu.hien(ctx)
