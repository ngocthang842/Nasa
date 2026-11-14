"""Trang Kế hoạch Mùa vụ & Thuần Lúa Nước — Vựa lúa Huyện Yên Thành (Nghệ An).
Mô hình chuẩn hóa chuyên canh Thuần Lúa 2 Vụ (Chiêm Xuân & Hè Thu) kết hợp Phơi Ải Vụ Đông:
- Tầng 1: KPI Ribbon 4 Chỉ số Nông học Số hóa Thuần Lúa (Cơ cấu 100% Lúa, Rủi ro khí hậu, Nước Ba Ra, Làm sạch mầm bệnh).
- Tầng 2: Hệ thống 3 Tabs Tinh gọn, vừa khít màn hình, loại bỏ cuộn dọc dài:
  * Tab 1: 🌾 Lập Kế Hoạch 2 Vụ Lúa Thuần & Cơ Cấu Giống Lúa Số Hóa
  * Tab 2: 🧪 Sức Khỏe Đất Lúa & Quy Trình Cày Phơi Ải Hoàn Nguyên
  * Tab 3: 🛰️ Đối Chiếu Khí Tượng & Lưới Rủi Ro Thiên Tai NASA Cho Cây Lúa
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine as E
from views.chung import tieu_de, ve

# Icon chu kỳ nông học 12 tháng lúa Yên Thành
ICON_THANG = {
    1: "🌱", 2: "🌿", 3: "🌾", 4: "🌸", 5: "✨",
    6: "🌱", 7: "🌿", 8: "🌾", 9: "🌊", 10: "🚜", 11: "☀️", 12: "💧"
}

# DANH MỤC GIỐNG LÚA THUẦN CHỦ LỰC VỰA LÚA YÊN THÀNH
GIONG_LUA_XUAN = ["ST25 (Gạo ngon thế giới)", "J02 (Lúa Nhật hạt tròn)", "TBR225 (Năng suất đỉnh)", "Bắc Thịnh (Chống rét tốt)"]
GIONG_LUA_HETHU = ["Khang Dân 18 (Cực ngắn ngày né lũ)", "Đài Thơm 8 (Chịu nhiệt gió Lào)", "BT7 (Chống ngã đổ)", "TBR225"]


def _khoa_session(vung, nam, ma):
    return f"luan_canh_{E.khoa(vung)}_{nam}_{ma}"


def hien(ctx):
    dl, tb_df = ctx["dl"], ctx["tb_df"]
    nam, thang, years = ctx["nam"], ctx.get("thang", 4), ctx["years"]
    vung = "Yên Thành"

    # 1. BỘ QUẢN LÝ NIÊN VỤ KẾ HOẠCH NÔNG NGHIỆP THUẦN LÚA
    key_nam = "filter_nam_thuan_lua"
    if key_nam not in st.session_state:
        st.session_state[key_nam] = nam if nam in years else years[-1]

    # Danh sách năm sắp xếp giảm dần (Năm mới nhất lên đầu để chọn nhanh nhất)
    danh_sach_nam = sorted(years, reverse=True)
    nam_cur = int(st.session_state[key_nam])

    # TIÊU ĐỀ CHUẨN NIÊN VỤ CẢ NĂM (Không để tháng để tránh mâu thuẫn với cơ cấu 2 vụ cả năm)
    tieu_de(vung, None, nam_cur, "KẾ HOẠCH MÙA VỤ & CƠ CẤU 2 VỤ THUẦN LÚA YÊN THÀNH", len(years) < 2)

    # 1.5 BỘ ĐIỀU KHIỂN NIÊN VỤ THÔNG MINH (SEARCHABLE SELECTBOX + ĐIỀU HƯỚNG NHANH CÁC NĂM XA)
    with st.container(border=True):
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([4.4, 5.0, 2.6], gap="small")

        with col_ctrl1:
            idx_nam = danh_sach_nam.index(nam_cur) if nam_cur in danh_sach_nam else 0

            def _dinh_dang_nam(y):
                if y == 2026:
                    return f"🌟 Năm {y} (Niên vụ kế hoạch trọng tâm)"
                elif y >= 2024:
                    return f"📅 Năm {y} (Viễn thám gần đây)"
                else:
                    return f"📜 Năm {y} (Dữ liệu lịch sử đối chiếu)"

            sel_nam = st.selectbox(
                "Chọn hoặc gõ tìm kiếm Năm Niên Vụ:",
                options=danh_sach_nam,
                index=idx_nam,
                format_func=_dinh_dang_nam,
                key="select_nam_luan_canh",
                help="Gõ số năm trực tiếp để tìm kiếm nhanh dù chuỗi dữ liệu có 30-50 năm",
            )
            if sel_nam and sel_nam != nam_cur:
                st.session_state[key_nam] = int(sel_nam)
                st.rerun()

        with col_ctrl2:
            st.markdown("<div style='font-size:11px; font-weight:700; color:#64748B; margin-bottom:5px;'>ĐIỀU HƯỚNG NHANH CÁC NĂM:</div>", unsafe_allow_html=True)
            c_prev, c_curr, c_next = st.columns(3, gap="small")

            # Lùi 1 năm (năm cũ hơn)
            with c_prev:
                nam_truoc = nam_cur - 1
                co_nam_truoc = nam_truoc in years
                if st.button(f"◀️ {nam_truoc if co_nam_truoc else 'Cũ hơn'}", key="btn_luan_canh_nam_truoc", disabled=not co_nam_truoc, use_container_width=True, help="Lùi về năm trước đó"):
                    st.session_state[key_nam] = nam_truoc
                    st.rerun()

            # Nhảy về năm kế hoạch 2026
            with c_curr:
                is_2026 = (nam_cur == 2026)
                if st.button("🌟 2026 Hiện tại", key="btn_luan_canh_2026", disabled=is_2026, use_container_width=True, help="Nhảy ngay về Năm Kế hoạch trọng tâm 2026"):
                    st.session_state[key_nam] = 2026
                    st.rerun()

            # Tiến 1 năm (năm mới hơn)
            with c_next:
                nam_sau = nam_cur + 1
                co_nam_sau = nam_sau in years
                if st.button(f"{nam_sau if co_nam_sau else 'Mới hơn'} ▶️", key="btn_luan_canh_nam_sau", disabled=not co_nam_sau, use_container_width=True, help="Tiến đến năm tiếp theo"):
                    st.session_state[key_nam] = nam_sau
                    st.rerun()

        with col_ctrl3:
            st.markdown("<div style='font-size:11px; font-weight:700; color:#64748B; margin-bottom:5px;'>KHO DỮ LIỆU:</div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background:#F1F5F9; border:1px solid #E2E8F0; border-radius:8px; padding:6px 10px; text-align:center;">
                  <span style="font-size:11px; font-weight:750; color:#0F172A;">🛰️ {len(years)} Năm Vệ Tinh</span>
                  <div style="font-size:10px; color:#64748B;">{min(years)} → {max(years)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    nam = int(st.session_state[key_nam])

    # ĐỊNH HÌNH 3 ĐỢT CHUẨN 2 VỤ LÚA THUẦN + PHƠI ẢI VỤ ĐÔNG
    cac_dot = [
        {
            "ma": "xuan",
            "ten": "Vụ Lúa Chiêm Xuân",
            "thang_bat_dau": 1,
            "thang_ket_thuc": 5,
            "so_thang": 5,
            "cay": "Lúa",
            "icon": "🌾",
            "mau": "#16A34A",
            "khuyen_cao": "Gieo mạ chống rét T1, trỗ rộ T4 né gió Lào, thu hoạch dứt điểm T5.",
        },
        {
            "ma": "hethu",
            "ten": "Vụ Lúa Hè Thu",
            "thang_bat_dau": 6,
            "thang_ket_thuc": 9,
            "so_thang": 4,
            "cay": "Lúa",
            "icon": "☀️",
            "mau": "#D97706",
            "khuyen_cao": "Cấy cực nhanh đầu T6, chống hạn gió Lào T7, gặt trước 15/9 né lũ Kênh Vách Bắc.",
        },
        {
            "ma": "dong_ai",
            "ten": "Cày Ải Phơi Ruộng / Vụ Đông",
            "thang_bat_dau": 10,
            "thang_ket_thuc": 12,
            "so_thang": 3,
            "cay": "Phơi Ải Đất",
            "icon": "🚜",
            "mau": "#0284C7",
            "khuyen_cao": "Cày sâu 18–22 cm phơi khô nỏ đất diệt mầm đạo ôn, đón nước sông Lam T12.",
        },
    ]

    # Kiểm tra và khởi tạo dữ liệu THUẦN LÚA 100% trong session_state
    ke_hoach_nguoi_dung = {}
    danh_gia_cac_dot_map = {}
    for d in cac_dot:
        khoa = _khoa_session(vung, nam, d["ma"])
        if khoa not in st.session_state or not st.session_state[khoa]:
            if d["ma"] in ["xuan", "hethu"]:
                st.session_state[khoa] = [{"cay": "Lúa", "ty_le_pct": 100}]
            else:
                st.session_state[khoa] = []  # Phơi ải đất 100%
        ke_hoach_nguoi_dung[d["ma"]] = st.session_state[khoa]

        df_dg = E.danh_gia_cay_theo_dot(dl, vung, d["thang_bat_dau"], d["thang_ket_thuc"], nam, tb_df)
        danh_gia_cac_dot_map[d["ma"]] = E.danh_gia_to_hop_dot(df_dg, ke_hoach_nguoi_dung[d["ma"]])

    danh_gia_nam = E.danh_gia_ke_hoach_nam(cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map)

    # 2. BỘ 4 THẺ SỐ HÓA KPI THUẦN LÚA YÊN THÀNH
    shi_score = danh_gia_nam.get("diem_suc_khoe_dat", 85)
    rr_tb = danh_gia_nam.get("rui_ro_tb_nam", 30)

    col_k1, col_k2, col_k3, col_k4 = st.columns(4, gap="small")
    with col_k1:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#16A34A; text-transform:uppercase;">🌾 CƠ CẤU MÙA VỤ</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">100% Thuần Lúa</div>
              <div style="font-size:11px; color:#16A34A; font-weight:600;">2 Vụ lúa thâm canh / năm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k2:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #D97706; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#D97706; text-transform:uppercase;">🛡️ RỦI RO THỜI TIẾT KHÍ HẬU</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{rr_tb:.0f}% <small style="font-size:13px; color:#64748B;">({danh_gia_nam['muc_rui_ro_nam']})</small></div>
              <div style="font-size:11px; color:#475569;">Gió Lào T7 & Bão lũ T9 được né tránh</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k3:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #0284C7; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#0284C7; text-transform:uppercase;">💧 NƯỚC BA RA ĐÔ LƯƠNG</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">Tưới tự chảy <small style="font-size:13px; color:#64748B;">(26.500 ha)</small></div>
              <div style="font-size:11px; color:#0284C7; font-weight:600;">Kênh chính cấp đủ cho 2 vụ lúa</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k4:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #8B5CF6; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#8B5CF6; text-transform:uppercase;">🍂 LÀM SẠCH ĐẤT (PHƠI ẢI)</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{shi_score} <small style="font-size:13px; color:#64748B;">/ 100 điểm</small></div>
              <div style="font-size:11px; color:#16A34A; font-weight:600;">Diệt 85–90% mầm bệnh đạo ôn</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 3. HỆ THỐNG 3 TABS THUẦN LÚA CHUYÊN BIỆT
    tab1, tab2, tab3 = st.tabs([
        "🌾 1. Lập Kế Hoạch 2 Vụ Thuần Lúa & Cơ Cấu Giống",
        "🧪 2. Sức Khỏe Đất & Hoàn Nguyên Nhờ Cày Phơi Ải",
        "🛰️ 3. Lưới Khí Tượng & Rủi Ro Thiên Tai Từng Giai Đoạn",
    ])

    with tab1:
        _hien_tab_thuan_lua(dl, vung, nam, cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map)

    with tab2:
        _hien_tab_dat_thuan_lua(danh_gia_nam)

    with tab3:
        _hien_tab_khi_tuong_lua(dl, vung, nam)


# =============================================================================
# TAB 1: KẾ HOẠCH 2 VỤ THUẦN LÚA & CƠ CẤU GIỐNG CHỦ LỰC SỐ HÓA
# =============================================================================

def _hien_tab_thuan_lua(dl, vung, nam, cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map):
    """Tab 1: Bảng ma trận 2 vụ lúa thuần, chọn giống lúa thâm canh và Gantt chart."""
    # BẢNG MA TRẬN 2 VỤ THUẦN LÚA YÊN THÀNH SỐ HÓA
    with st.container(border=True):
        st.markdown(
            """
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <div>
                <div style="font-size:13.5px; font-weight:800; color:#0F172A;">📋 Bảng Ma Trận Cơ Cấu 2 Vụ Thuần Lúa Chuẩn Hóa Yên Thành</div>
                <div style="font-size:11.5px; color:#64748B;">Cơ cấu thuần thục: Lúa Chiêm Xuân (vụ chính) + Lúa Hè Thu (chạy lũ) + Cày ải phơi ruộng vụ đông</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows_table = [
            {
                "Vụ Mùa": "🌾 1. Vụ Lúa Chiêm Xuân",
                "Khung Thời Gian": "Tháng 1 → Tháng 5 (5 tháng)",
                "Cây Trồng & Tỷ Lệ": "🌾 Lúa thuần thâm canh (100% diện tích)",
                "Giống Lúa Khuyến Cáo": "ST25, J02, TBR225, Bắc Thịnh",
                "Năng Suất Kỳ Vọng": "68–72 tạ/ha (Kỷ lục thâm canh)",
                "Biện Pháp Trọng Tâm": "Gieo mạ che phủ nilon T1 chống rét, trỗ rộ T4 né táp gió Lào, gặt T5.",
            },
            {
                "Vụ Mùa": "☀️ 2. Vụ Lúa Hè Thu",
                "Khung Thời Gian": "Tháng 6 → Tháng 9 (4 tháng)",
                "Cây Trồng & Tỷ Lệ": "🌾 Lúa hè thu ngắn ngày (100% diện tích)",
                "Giống Lúa Khuyến Cáo": "Khang Dân 18, Đài Thơm 8, BT7",
                "Năng Suất Kỳ Vọng": "54–58 tạ/ha (Né lụt thành công)",
                "Biện Pháp Trọng Tâm": "Cấy cực nhanh đầu T6, dâng nước làm mát T7, gặt dứt điểm trước 15/9 né bão lũ.",
            },
            {
                "Vụ Mùa": "🚜 3. Phơi Ải Vụ Đông",
                "Khung Thời Gian": "Tháng 10 → Tháng 12 (3 tháng)",
                "Cây Trồng & Tỷ Lệ": "🍂 Cày phơi nỏ ải (100% diện tích)",
                "Giống Lúa Khuyến Cáo": "Nghỉ đất hoàn nguyên độ phì",
                "Năng Suất Kỳ Vọng": "Diệt 90% mầm đạo ôn & sâu rầy",
                "Biện Pháp Trọng Tâm": "Cày sâu 18–22 cm phơi khô ruộng, bón vôi khử chua, đón nước sông Lam T12.",
            },
        ]

        st.dataframe(pd.DataFrame(rows_table), use_container_width=True, hide_index=True)

    # 3 CỘT ĐIỀU CHỈNH GIỐNG LÚA THUẦN CHO TỪNG VỤ
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12.5px; font-weight:750; color:#0F172A; margin-bottom:6px;'>🌾 Lựa Chọn Cơ Cấu Giống Lúa Thuần Từng Vụ:</div>", unsafe_allow_html=True)

    col_x, col_ht, col_ai = st.columns(3, gap="small")

    with col_x, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:12.5px; font-weight:800; color:#16A34A; border-bottom:1px solid #F1F5F9; padding-bottom:4px; margin-bottom:6px;">
              🌾 Vụ Lúa Chiêm Xuân (100% Lúa)
            </div>
            """,
            unsafe_allow_html=True,
        )
        g_xuan = st.selectbox(
            "Giống lúa xuân:",
            GIONG_LUA_XUAN,
            index=0,
            key=f"sel_giong_xuan_{nam}",
            label_visibility="collapsed",
        )
        st.markdown(
            f"""
            <div style="font-size:11.5px; color:#334155; line-height:1.45;">
              • <b>Giống đang chọn:</b> <b style="color:#16A34A;">{g_xuan.split('(')[0].strip()}</b><br>
              • <b>Đặc điểm:</b> Sinh trưởng 125–135 ngày, gạo thơm ngon, chống chịu rét đầu vụ.<br>
              • <b>Tỷ lệ diện tích:</b> <b>100%</b> toàn bộ cánh đồng Yên Thành.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ht, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:12.5px; font-weight:800; color:#D97706; border-bottom:1px solid #F1F5F9; padding-bottom:4px; margin-bottom:6px;">
              ☀️ Vụ Lúa Hè Thu (100% Lúa)
            </div>
            """,
            unsafe_allow_html=True,
        )
        g_ht = st.selectbox(
            "Giống lúa hè thu:",
            GIONG_LUA_HETHU,
            index=0,
            key=f"sel_giong_hethu_{nam}",
            label_visibility="collapsed",
        )
        st.markdown(
            f"""
            <div style="font-size:11.5px; color:#334155; line-height:1.45;">
              • <b>Giống đang chọn:</b> <b style="color:#D97706;">{g_ht.split('(')[0].strip()}</b><br>
              • <b>Đặc điểm:</b> Thời gian sinh trưởng cực ngắn (85–95 ngày), né hoàn toàn lũ tiểu mãn.<br>
              • <b>Tỷ lệ diện tích:</b> <b>100%</b> đồng loạt cấy sớm trước 10/6.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ai, st.container(border=True):
        st.markdown(
            """
            <div style="font-size:12.5px; font-weight:800; color:#0284C7; border-bottom:1px solid #F1F5F9; padding-bottom:4px; margin-bottom:6px;">
              🚜 Vụ Đông: Cày Ải Phơi Ruộng
            </div>
            """,
            unsafe_allow_html=True,
        )
        phuong_an_dong = st.selectbox(
            "Phương án vụ đông:",
            ["Cày lật đất phơi nỏ ải 100%", "Phơi ải 70% + Trồng Ngô ngọt 30%"],
            index=0,
            key=f"sel_phuong_an_dong_{nam}",
            label_visibility="collapsed",
        )
        st.markdown(
            f"""
            <div style="font-size:11.5px; color:#334155; line-height:1.45;">
              • <b>Quy trình:</b> <b style="color:#0284C7;">{phuong_an_dong}</b><br>
              • <b>Mục tiêu cốt lõi:</b> Phơi khô nỏ ruộng để diệt triệt để nấm đạo ôn và sâu đục thân.<br>
              • <b>Hiệu quả:</b> Hoàn nguyên độ phì cho vụ lúa xuân tiếp theo.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # BẢNG ĐỐI CHIẾU & ĐÚC KẾT DỮ LIỆU ĐA NĂM (2018–2026) THUẦN LÚA YÊN THÀNH
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <div>
                <div style="font-size:13px; font-weight:800; color:#0F172A;">
                  📊 Đối Chiếu Chuỗi Số Liệu 9 Năm (2018–2026): Vì Sao Thuần Lúa Là Tối Ưu?
                </div>
                <div style="font-size:11.5px; color:#64748B;">
                  Dữ liệu thực nghiệm NASA POWER & GPM IMERG kết hợp năng suất thực tế tại Yên Thành
                </div>
              </div>
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:3px 8px; font-size:11px; font-weight:750; color:#16A34A;">
                🌟 Năm đang khảo sát: {nam}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        res_2027 = E.du_bao_nang_suat_lua_2027(dl)
        df_ns = res_2027.get("lich_su_nang_suat", pd.DataFrame())
        df_yt = dl[dl.huyen == vung] if not dl.empty else pd.DataFrame()

        rows_da_nam = []
        for idx, r_ns in df_ns.iterrows():
            y = int(r_ns["nam"])
            sub_y = df_yt[df_yt.year == y] if not df_yt.empty else pd.DataFrame()
            nong_ht = int(sub_y[sub_y.month.isin([6, 7, 8])]["nong35"].sum()) if not sub_y.empty and "nong35" in sub_y.columns else 0
            mua_lu = int(sub_y[sub_y.month.isin([9, 10])]["mua_mm"].sum()) if not sub_y.empty and "mua_mm" in sub_y.columns else 0

            nhan_nam = f"🌟 Năm {y} (Đang xem)" if y == nam else (f"🎯 Năm {y} (Dự báo)" if y == 2027 else f"Năm {y}")

            rows_da_nam.append({
                "Năm Khảo Sát": nhan_nam,
                "Lúa Xuân (tạ/ha)": f"{r_ns['xuan']:.1f}",
                "Lúa Hè Thu (tạ/ha)": f"{r_ns['hethu']:.1f}",
                "Cả Năm (tạ/ha)": f"{r_ns['ca_nam']:.1f}",
                "Gió Lào Hè Thu (T6–T8)": f"{nong_ht} ngày" if y <= 2026 else "Mô hình ML",
                "Mưa Lũ T9–T10 (mm)": f"{mua_lu} mm" if y <= 2026 else "Mô hình ML",
                "Đúc Kết Khí Hậu & Nông Học": r_ns.get("ghi_chu", ""),
            })

        st.dataframe(pd.DataFrame(rows_da_nam), use_container_width=True, hide_index=True)

        st.markdown(
            """
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:8px; padding:8px 12px; margin-top:8px; font-size:11.5px; color:#334155; line-height:1.45;">
              💡 <b>Đúc kết Khoa học Nông học từ Chuỗi Số liệu Đa Năm:</b> So sánh 9 năm thực tế chứng minh mô hình <b>2 Vụ Thuần Lúa Nước (Xuân & Hè Thu) + Cày Phơi Ải Vụ Đông</b> tại Yên Thành đem lại hiệu quả vượt trội so với luân canh hoa màu:
              <br>1. <b>Né tuyệt đối táp hoa lúa do Gió Lào:</b> Lúa vụ Xuân trổ rộ vào cuối Tháng 4, chín và gặt gọn trong Tháng 5, trước khi đỉnh gió Lào bùng nổ (Tháng 6–7 có năm lên tới 10–11 ngày <i>T<sub>max</sub> ≥ 35°C</i>).
              <br>2. <b>Né triệt để ngập úng mùa lũ:</b> Lúa vụ Hè Thu dùng giống cực ngắn ngày (Khang Dân 18, Đài Thơm 8) gặt trước 15/9, né trọn vẹn đỉnh mưa lũ Tháng 9–10 (lên đến 800–1.150 mm) gây ngập lụt lòng chảo Yên Thành.
              <br>3. <b>Hoàn nguyên độ phì đất:</b> Vụ đông cày phơi ải trong điều kiện mùa đông rét muộn giúp đất nghỉ ngơi, tiêu diệt 85–90% nguồn nấm bệnh đạo ôn cho vụ sau.
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# TAB 2: SỨC KHỎE ĐẤT & HOÀN NGUYÊN NHỜ CÀY PHƠI ẢI VỤ ĐÔNG
# =============================================================================

def _hien_tab_dat_thuan_lua(danh_gia_nam):
    """Tab 2: Đánh giá khoa học sức khỏe đất trong canh tác thuần lúa."""
    col_box1, col_box2 = st.columns([1, 1], gap="medium")

    with col_box1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:8px;">
                  🧪 Bảng Chỉ Tiêu Thổ Nhưỡng Ruộng Thuần Lúa Yên Thành
                </div>
                """,
                unsafe_allow_html=True,
            )
            data_soil = [
                {"Chỉ Tiêu": "🍂 Cày phơi ải vụ đông", "Định Lượng": "30–45 ngày phơi nỏ", "Ý Nghĩa Nông Học": "Cực kỳ quan trọng để cắt mầm nấm đạo ôn cổ bông"},
                {"Chỉ Tiêu": "💧 Nước tưới Ba Ra Đô Lương", "Định Lượng": "Tự chảy 26.500 ha", "Ý Nghĩa Nông Học": "Cung cấp đủ nước ngọt phù sa sông Lam"},
                {"Chỉ Tiêu": "🦠 Tỷ lệ diệt trừ sâu bệnh", "Định Lượng": "Giảm 85–90%", "Ý Nghĩa Nông Học": "Nhờ phơi ải đất kết hợp rải vôi bột khử chua"},
                {"Chỉ Tiêu": "🌾 Năng suất cả năm", "Định Lượng": "122–128 tạ/ha/năm", "Ý Nghĩa Nông Học": "Tổng sản lượng 2 vụ lúa cao nhất Nghệ An"},
                {"Chỉ Tiêu": "🧪 Độ pH đất lúa", "Định Lượng": "5.2 – 5.8", "Ý Nghĩa Nông Học": "Thổ nhưỡng phù sa cổ thích hợp lúa thuần"},
            ]
            st.dataframe(pd.DataFrame(data_soil), use_container_width=True, hide_index=True)

    with col_box2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:8px;">
                  🌾 3 Nguyên Tắc Vàng Giữ Đất Bền Vững Cho 2 Vụ Thuần Lúa
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div style="display:flex; flex-direction:column; gap:8px; font-size:12px;">
                  <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:8px 12px;">
                    <b style="color:#16A34A;">1. Cày lật đất phơi ải sâu 18–22 cm:</b><br>
                    Sau khi gặt lúa hè thu, khẩn trương cày lật đất phơi nỏ ải vụ đông để phá vỡ tầng đế cày, giải phóng khí độc yếm khí và diệt sạch bào tử nấm.
                  </div>
                  <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #0284C7; border-radius:8px; padding:8px 12px;">
                    <b style="color:#0284C7;">2. Bón vôi và phân chuồng hoai mục đầu vụ:</b><br>
                    Rải 20–25 kg vôi bột/sào vào tháng 12 trước khi đổ ải lấy nước sông Lam để khử chua và kích thích vi sinh vật có ích.
                  </div>
                  <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #D97706; border-radius:8px; padding:8px 12px;">
                    <b style="color:#D97706;">3. Rút nước phơi ruộng nứt chân chim:</b><br>
                    Ở giai đoạn cuối đẻ nhánh (cuối T2 và giữa T7), rút cạn nước 5–7 ngày để rễ lúa ăn sâu, chống đổ ngã khi gặp mưa dông và gió Lào.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:12px; color:#1E293B;">
          <b>🌾 Kết luận Nông học Yên Thành:</b> Canh tác 2 vụ thuần lúa là thế mạnh truyền thống số 1 của vựa lúa Yên Thành. Chỉ cần tuân thủ nghiêm ngặt lịch cày ải phơi ruộng vụ đông và gặt trước 15/9 né lũ Kênh Vách Bắc, đất ruộng sẽ duy trì độ phì bền vững và năng suất luôn dẫn đầu toàn tỉnh.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# TAB 3: LƯỚI KHÍ TƯỢNG & RỦI RO THIÊN TAI TỪNG GIAI ĐOẠN CÂY LÚA
# =============================================================================

def _hien_tab_khi_tuong_lua(dl, vung, nam):
    """Tab 3: Chuẩn hóa 12 tháng khí tượng viễn thám phục vụ cây lúa nước."""
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:8px;">
              🛰️ Lưới Rủi Ro Khí Tượng NASA Chuẩn Hóa Cho 2 Vụ Thuần Lúa Yên Thành
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_yt = dl[(dl.year == nam) & (dl.huyen == vung)].sort_values("month")
        rows = []
        for m in range(1, 13):
            sub_m = df_yt[df_yt.month == m]
            r = sub_m.iloc[0] if not sub_m.empty else pd.Series()
            tmax = float(r.get("tmax", 30.0)) if pd.notna(r.get("tmax")) else 30.0
            nong = int(r.get("nong35", 0)) if pd.notna(r.get("nong35")) else 0
            mua = float(r.get("mua_mm", 80.0)) if pd.notna(r.get("mua_mm")) else 80.0
            sm = float(r.get("sm_rootzone", 0.28)) if pd.notna(r.get("sm_rootzone")) else 0.28
            ndvi = float(r.get("ndvi", 0.65)) if pd.notna(r.get("ndvi")) else 0.65

            if m in [1, 2]:
                gd = "🌱 Gieo mạ & Cấy xuân"
                rr = "❄️ Rét đậm hại mạ non" if tmax < 20 else "🟢 Thuận lợi đẻ nhánh"
            elif m in [3, 4]:
                gd = "🌾 Làm đòng & Trỗ bông xuân"
                rr = "🔥 Gió Lào T4 táp phấn hoa" if nong >= 5 else "🟢 Nắng ấm quang hợp tốt"
            elif m == 5:
                gd = "✨ Chín & Gặt lúa xuân"
                rr = "🌾 Cần tháo cạn nước đưa máy gặt"
            elif m in [6, 7]:
                gd = "🌱 Cấy & Đẻ nhánh hè thu"
                rr = "🔥 Đỉnh nắng hạn gió Lào Tây Nam" if nong >= 7 else "🟡 Cần dâng nước làm mát"
            elif m == 8:
                gd = "🌾 Trỗ bông lúa hè thu"
                rr = "🌾 Trỗ hè thu cần nước tưới đệm"
            elif m in [9, 10]:
                gd = "🌊 Gặt hè thu né lụt & Cày ải"
                rr = "🌊 MƯA LŨ KÊNH VÁCH BẮC (>300mm)" if mua >= 300 else "🟡 Mưa dông rải rác"
            else:
                gd = "🚜 Phơi khô nỏ ruộng vụ đông"
                rr = "🚜 Hanh khô lý tưởng diệt mầm nấm"

            rows.append({
                "Tháng": f"Tháng {m}",
                "Giai Đoạn Lúa Nước": gd,
                "Tmax (°C)": f"{tmax:.1f}",
                "Gió Lào ≥35°C": f"{nong} ngày",
                "Mưa GPM (mm)": f"{mua:.0f}",
                "Độ Ẩm Ruộng (SMAP)": f"{sm*100:.0f}%",
                "Sinh Khối NDVI": f"{ndvi:.2f}",
                "Mệnh Lệnh Khuyến Cáo": rr,
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
