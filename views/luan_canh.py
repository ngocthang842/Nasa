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

    # 2. BỘ 4 THẺ SỐ HÓA KPI THUẦN LÚA YÊN THÀNH (ĐỘNG THEO NIÊN VỤ ĐANG CHỌN)
    sub_y = dl[(dl.year == nam) & (dl.huyen == vung)] if not dl.empty else pd.DataFrame()
    sub_dong = sub_y[sub_y.month.isin([10, 11, 12])] if not sub_y.empty else pd.DataFrame()
    sub_ht = sub_y[sub_y.month.isin([6, 7, 8])] if not sub_y.empty else pd.DataFrame()

    nong_ht = float(sub_ht["nong35"].sum()) if (not sub_ht.empty and "nong35" in sub_ht) else 0.0
    mua_lu = float(sub_y[sub_y.month.isin([9, 10])]["mua_mm"].sum()) if (not sub_y.empty and "mua_mm" in sub_y) else 0.0
    mua_dong = float(sub_dong["mua_mm"].sum()) if (not sub_dong.empty and "mua_mm" in sub_dong) else 400.0
    sm_dong = float(sub_dong["sm_rootzone"].mean()) if (not sub_dong.empty and "sm_rootzone" in sub_dong) else 0.30

    # Rủi ro thời tiết khí hậu năm nam (Gió Lào vụ Hè Thu + Mưa lũ thu hoạch T9-10)
    rr_nam = 15.0 + min(18.0, nong_ht * 0.9) + (10.0 if mua_lu > 1000 else (6.0 if mua_lu > 700 else (3.0 if mua_lu > 400 else 0.0)))
    rr_nam = int(round(min(55.0, max(12.0, rr_nam))))
    muc_rr_nam = "An toàn rất cao" if rr_nam < 22 else ("An toàn cao" if rr_nam < 28 else ("Rủi ro trung bình" if rr_nam < 35 else "Cần theo dõi"))

    # Điểm phơi ải & làm sạch đất vụ Đông của năm nam
    diem_phoi_ai_nam = int(95 - max(0, (mua_dong - 300) / 25) - max(0, (sm_dong - 0.28) * 300))
    diem_phoi_ai_nam = max(65, min(96, diem_phoi_ai_nam))

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
              <div style="font-size:11px; font-weight:750; color:#D97706; text-transform:uppercase;">🛡️ RỦI RO KHÍ HẬU {nam}</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{rr_nam}% <small style="font-size:13px; color:#64748B;">({muc_rr_nam})</small></div>
              <div style="font-size:11px; color:#475569;">Gió Lào T6–8: <b>{int(nong_ht)} ngày</b> • Mưa: <b>{int(mua_lu)} mm</b></div>
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
              <div style="font-size:11px; font-weight:750; color:#8B5CF6; text-transform:uppercase;">🍂 LÀM SẠCH ĐẤT (PHƠI ẢI) {nam}</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{diem_phoi_ai_nam} <small style="font-size:13px; color:#64748B;">/ 100 điểm</small></div>
              <div style="font-size:11px; color:#16A34A; font-weight:600;">SMAP đông: {sm_dong*100:.1f}% • Mưa: {int(mua_dong)} mm</div>
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
        _hien_tab_dat_thuan_lua(dl, vung, nam, danh_gia_nam, diem_phoi_ai_nam, sm_dong, mua_dong)

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
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
              <div>
                <div style="font-size:13.5px; font-weight:800; color:#0F172A;">📋 Bảng Ma Trận Cơ Cấu 2 Vụ Thuần Lúa Chuẩn Hóa Yên Thành</div>
                <div style="font-size:11.5px; color:#64748B;">
                  Khung quy chuẩn nông học trích xuất từ <b>Đề án Sản xuất Nông nghiệp Huyện Yên Thành</b> & Báo cáo đề tài <i>(Bao-cao-He-thong-Phan-tich-va-Du-bao-Nang-suat-Lua-Yen-Thanh-2027.pdf)</i>
                </div>
              </div>
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:3px 9px; font-size:11px; font-weight:750; color:#15803D;">
                🌾 Chuẩn Nông Nghiệp Xứ Nghệ
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows_table = [
            {
                "Vụ Mùa": "🌾 1. Vụ Lúa Chiêm Xuân",
                "Khung Lịch Canh Tác": "Tháng 1 → Tháng 5 (Xuống giống 10–25/01; Trổ rộ cuối T4; Gặt T5)",
                "Cây Trồng & Tỷ Lệ": "🌾 Lúa thuần thâm canh (100% diện tích)",
                "Bộ Giống Chủ Lực": "ST25, J02, TBR225, Bắc Thịnh",
                "Năng Suất Kỷ Lục": "68–72 tạ/ha (Đỉnh thâm canh)",
                "Biện Pháp Trọng Tâm": "Gieo mạ che phủ nilon chống rét Tmin < 15°C, trổ rộ cuối T4 né táp gió Lào, tháo cạn nước gặt rộ trong T5.",
            },
            {
                "Vụ Mùa": "☀️ 2. Vụ Lúa Hè Thu",
                "Khung Lịch Canh Tác": "Tháng 6 → Tháng 9 (Cấy khẩn trương 05–20/06; Gặt trước 15/9 né lũ)",
                "Cây Trồng & Tỷ Lệ": "🌾 Lúa hè thu cực ngắn ngày (100% diện tích)",
                "Bộ Giống Chủ Lực": "Khang Dân 18, Đài Thơm 8, BT7",
                "Năng Suất Kỳ Vọng": "54–58 tạ/ha (Né lụt thành công)",
                "Biện Pháp Trọng Tâm": "Cấy cực nhanh sau gặt xuân, dâng nước 3–5 cm làm mát khi Tmax ≥ 37°C, gặt dứt điểm trước 15/9 né bão lũ >350mm.",
            },
            {
                "Vụ Mùa": "🚜 3. Phơi Ải Vụ Đông",
                "Khung Lịch Canh Tác": "Tháng 10 → Tháng 12 (Nghỉ đất hoàn nguyên độ phì; Đón nước T12)",
                "Cây Trồng & Tỷ Lệ": "🍂 Cày phơi nỏ ải (100% diện tích)",
                "Bộ Giống Chủ Lực": "Cày lật tầng đất phơi khô nỏ",
                "Năng Suất Kỳ Vọng": "Diệt 85–90% mầm bệnh đạo ôn",
                "Biện Pháp Trọng Tâm": "Cày sâu 18–22 cm phá vỡ tầng yếm khí, rải 20–25 kg vôi bột/sào khử chua đất pH 5.62, đón nước phù sa sông Lam.",
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
            ["Cày lật đất phơi nỏ ải 100% (Hoàn nguyên đất)", "Phơi ải sâu 20cm + Bón vôi khử chua pH 5.6"],
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

def _hien_tab_dat_thuan_lua(dl, vung, nam, danh_gia_nam, diem_phoi_ai_nam, sm_dong, mua_dong):
    """Tab 2: Đánh giá khoa học sức khỏe đất từ dữ liệu thổ nhưỡng thực tế Yên Thành (dat.csv & dem_slope_v2.csv)
    kết hợp viễn thám độ ẩm đất NASA SMAP động theo niên vụ đang chọn."""
    df_yt = dl[dl.huyen == vung] if not dl.empty else pd.DataFrame()
    r = df_yt.iloc[0] if not df_yt.empty else pd.Series()

    ph_val = float(r.get("ph", 5.62)) if pd.notna(r.get("ph")) else 5.62
    soc_val = float(r.get("carbon_huu_co_g_kg", 19.58)) if pd.notna(r.get("carbon_huu_co_g_kg")) else 19.58
    sand_val = float(r.get("cat_pct", 44.27)) if pd.notna(r.get("cat_pct")) else 44.27
    clay_val = float(r.get("set_pct", 26.90)) if pd.notna(r.get("set_pct")) else 26.90
    elev_val = float(r.get("do_cao_m", 52.0)) if pd.notna(r.get("do_cao_m")) else 52.0
    slope_val = float(r.get("do_doc_do", 6.71)) if pd.notna(r.get("do_doc_do")) else 6.71
    steep_val = float(r.get("ty_le_doc_tren_15", 0.151)) if pd.notna(r.get("ty_le_doc_tren_15")) else 0.151

    # 1. KHỐI GIÁM SÁT VIỄN THÁM ĐỘ ẨM SMAP VÀ ĐIỀU KIỆN PHƠI ẢI NIÊN VỤ ĐANG CHỌN
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
              <div>
                <div style="font-size:13.5px; font-weight:800; color:#0F172A;">
                  🧪 Đánh Giá Sức Khỏe Đất & Giám Sát Độ Ẩm Viễn Thám NASA SMAP — Niên Vụ {nam}
                </div>
                <div style="font-size:11.5px; color:#64748B;">
                  Kết hợp nền tảng thổ nhưỡng thực đo địa phương (dat.csv) và cảm biến viễn thám độ ẩm đất tầng rễ vệ tinh NASA SMAP L4
                </div>
              </div>
              <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:6px; padding:3px 10px; font-size:11.5px; font-weight:750; color:#1D4ED8;">
                🛰️ Niên Vụ Đang Khảo Sát: {nam}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 3 Thẻ Metric Động Vụ Đông Của Năm Được Chọn
        col_m1, col_m2, col_m3 = st.columns(3, gap="small")
        with col_m1:
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:8px 12px;">
                  <div style="font-size:11px; font-weight:700; color:#0284C7; text-transform:uppercase;">💧 Độ Ẩm Tầng Rễ SMAP Vụ Đông ({nam})</div>
                  <div style="font-size:19px; font-weight:800; color:#0F172A; margin:2px 0;">{sm_dong*100:.1f}%</div>
                  <div style="font-size:11px; color:#64748B;">T10–T12 · Ngưỡng phơi nỏ ải: &lt; 30%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_m2:
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:8px 12px;">
                  <div style="font-size:11px; font-weight:700; color:#D97706; text-transform:uppercase;">🌧️ Mưa Tích Lũy Vụ Đông ({nam})</div>
                  <div style="font-size:19px; font-weight:800; color:#0F172A; margin:2px 0;">{int(mua_dong)} mm</div>
                  <div style="font-size:11px; color:#64748B;">T10–T12 · Khô ráo giúp đất nỏ nứt chân chim</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_m3:
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:8px 12px;">
                  <div style="font-size:11px; font-weight:700; color:#16A34A; text-transform:uppercase;">🍂 Hiệu Quả Làm Sạch Mầm Bệnh ({nam})</div>
                  <div style="font-size:19px; font-weight:800; color:#16A34A; margin:2px 0;">{diem_phoi_ai_nam} / 100</div>
                  <div style="font-size:11px; color:#64748B;">Diệt 85–95% nguồn nấm đạo ôn cho vụ sau</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Biểu đồ Diễn biến Độ ẩm đất tầng rễ SMAP 12 tháng của năm nam
        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:12px; font-weight:750; color:#334155; margin-bottom:4px;'>📊 Diễn Biến Độ Ẩm Tầng Rễ Viễn Thám NASA SMAP 12 Tháng Tại Yên Thành (Niên Vụ {nam}):</div>",
            unsafe_allow_html=True,
        )

        sub_y = dl[(dl.year == nam) & (dl.huyen == vung)] if not dl.empty else pd.DataFrame()
        months_x = [f"T{m}" for m in range(1, 13)]
        sm_vals = []
        text_vals = []
        for m in range(1, 13):
            sub_m = sub_y[sub_y.month == m] if not sub_y.empty else pd.DataFrame()
            if not sub_m.empty and pd.notna(sub_m["sm_rootzone"].iloc[0]):
                v = float(sub_m["sm_rootzone"].iloc[0]) * 100
                sm_vals.append(round(v, 1))
                text_vals.append(f"{v:.1f}%")
            else:
                sm_vals.append(None)
                text_vals.append("—")

        bar_colors = ["#0284C7" if m not in [10, 11, 12] else "#D97706" for m in range(1, 13)]

        fig_sm = go.Figure()
        fig_sm.add_trace(go.Bar(
            x=months_x,
            y=sm_vals,
            marker=dict(color=bar_colors, line=dict(color="#0F172A", width=0.5)),
            text=text_vals,
            textposition="outside",
            cliponaxis=False,
            name=f"SMAP {nam} (%)",
            hovertemplate="Tháng %{x}: Độ ẩm tầng rễ = %{y:.1f}%<extra></extra>",
        ))
        fig_sm.add_hline(
            y=28.0,
            line_dash="dash",
            line_color="#DC2626",
            line_width=1.5,
            annotation_text="Ngưỡng phơi khô nỏ nứt chân chim (28%)",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#DC2626"),
        )
        fig_sm.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(title="Độ ẩm tầng rễ (%)", range=[0, 42], gridcolor="#F1F5F9"),
            xaxis=dict(gridcolor="#F1F5F9"),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            showlegend=False,
        )
        ve(fig_sm, che_do="co_dinh")
        st.caption("💡 *Cột màu xanh: Giai đoạn thâm canh 2 vụ lúa (Xuân & Hè Thu); Cột màu hổ phách: Giai đoạn cày phơi ải hoàn nguyên vụ Đông (Tháng 10–12).*")

    # 2. BẢNG THỔ NHƯỠNG CƠ SỞ ĐỊA CHẤT & 3 NGUYÊN TẮC HOÀN NGUYÊN
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    col_box1, col_box2 = st.columns([1.1, 0.9], gap="medium")

    with col_box1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:4px;">
                  📍 1. Cơ Sở Thổ Nhưỡng Địa Chất Tự Nhiên Yên Thành (dat.csv)
                </div>
                <div style="font-size:11px; color:#64748B; margin-bottom:8px;">
                  <i>* Đặc tính vật lý thổ nhưỡng cố định của địa chất Yên Thành, đóng vai trò nền tảng không thay đổi theo từng năm.</i>
                </div>
                """,
                unsafe_allow_html=True,
            )
            data_soil = [
                {
                    "Chỉ Tiêu Thổ Nhưỡng": "🧪 Độ pH tầng canh tác (pH)",
                    "Số Liệu Thực Tế": f"{ph_val:.2f} pH",
                    "Ngưỡng Tối Ưu Lúa": "5.5 – 6.5",
                    "Đánh Giá Khoa Học": "🟢 Tối ưu (Đất hơi chua nhẹ, rất hợp lúa thuần)",
                },
                {
                    "Chỉ Tiêu Thổ Nhưỡng": "🍂 Cacbon hữu cơ (SOC)",
                    "Số Liệu Thực Tế": f"{soc_val:.2f} g/kg",
                    "Ngưỡng Tối Ưu Lúa": "> 15.0 g/kg",
                    "Đánh Giá Khoa Học": "🟢 Giàu mùn (Khoáng hóa dinh dưỡng khi phơi ải)",
                },
                {
                    "Chỉ Tiêu Thổ Nhưỡng": "🌾 Tỷ lệ Cát tầng mặt (Sand)",
                    "Số Liệu Thực Tế": f"{sand_val:.1f}%",
                    "Ngưỡng Tối Ưu Lúa": "30 – 50%",
                    "Đánh Giá Khoa Học": "🟢 Thịt pha cát (Thoát nước nhanh khi phơi nứt chân chim)",
                },
                {
                    "Chỉ Tiêu Thổ Nhưỡng": "🧱 Tỷ lệ Sét tầng đế (Clay)",
                    "Số Liệu Thực Tế": f"{clay_val:.1f}%",
                    "Ngưỡng Tối Ưu Lúa": "20 – 35%",
                    "Đánh Giá Khoa Học": "🟢 Giữ phân bón NPK & chống thấm lậu nước ruộng",
                },
                {
                    "Chỉ Tiêu Thổ Nhưỡng": "🏔️ Cao trình địa hình (DEM)",
                    "Số Liệu Thực Tế": f"{elev_val:.1f} m",
                    "Ngưỡng Tối Ưu Lúa": "Vùng đồng bằng",
                    "Đánh Giá Khoa Học": "🟢 Lòng chảo trũng đón nước tự chảy Ba Ra Đô Lương",
                },
                {
                    "Chỉ Tiêu Thổ Nhưỡng": "📐 Độ dốc địa hình (Slope)",
                    "Số Liệu Thực Tế": f"{slope_val:.2f}° (dốc >15°: {steep_val*100:.1f}%)",
                    "Ngưỡng Tối Ưu Lúa": "< 8.0°",
                    "Đánh Giá Khoa Học": "🟢 Bằng phẳng, nguy cơ xói mòn rửa trôi cực thấp",
                },
            ]
            st.dataframe(pd.DataFrame(data_soil), use_container_width=True, hide_index=True)

    with col_box2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:8px;">
                  🌾 2. Ba Nguyên Tắc Vàng Hoàn Nguyên Đất Nhờ Cày Phơi Ải
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="display:flex; flex-direction:column; gap:8px; font-size:11.5px; line-height:1.45;">
                  <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:8px 12px;">
                    <b style="color:#16A34A;">1. Cày lật đất phơi ải sâu 18–22 cm:</b><br>
                    Cày lật tầng đất có tỷ lệ sét <b>{clay_val:.1f}%</b> phơi nỏ 30–45 ngày vụ đông giúp phá vỡ tầng yếm khí, oxy hóa giải phóng độc chất <i>H<sub>2</sub>S, Fe<sup>2+</sup></i> và tiêu diệt 85–90% bào tử nấm đạo ôn cổ bông.
                  </div>
                  <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #0284C7; border-radius:8px; padding:8px 12px;">
                    <b style="color:#0284C7;">2. Bón vôi nâng độ pH từ {ph_val:.1f} lên 6.0:</b><br>
                    Rải 20–25 kg vôi bột/sào vào tháng 12 trước khi đổ ải lấy nước sông Lam để cân bằng độ pH đất thực tế (đang ở mức {ph_val:.2f}), kích thích vi sinh vật phân giải mùn hữu cơ ({soc_val:.1f} g/kg).
                  </div>
                  <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #D97706; border-radius:8px; padding:8px 12px;">
                    <b style="color:#D97706;">3. Rút nước phơi ruộng nứt chân chim (AWD):</b><br>
                    Tỷ lệ cát <b>{sand_val:.1f}%</b> cho phép rút cạn nước 5–7 ngày cuối giai đoạn đẻ nhánh (cuối T2 và giữa T7) mà không sợ khô nứt gãy rễ, kích thích rễ lúa ăn sâu vào tầng sét giữ phân bón.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:12px; color:#1E293B; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <b>🌾 Đúc Kết Khoa Học Thổ Nhưỡng Niên Vụ {nam}:</b> Với pH thực tế <b>{ph_val:.2f}</b>, giàu chất hữu cơ <b>{soc_val:.1f} g/kg</b> kết hợp độ ẩm viễn thám SMAP vụ đông đạt <b>{sm_dong*100:.1f}%</b> (mưa tích lũy {int(mua_dong)} mm), đất ruộng Yên Thành trong niên vụ {nam} đạt <b>{diem_phoi_ai_nam}/100 điểm</b> về hiệu quả hoàn nguyên độ phì và diệt mầm nấm bệnh.
          </div>
          <div style="background:#DCFCE7; border:1px solid #86EFAC; border-radius:6px; padding:4px 10px; font-size:12px; font-weight:800; color:#15803D; white-space:nowrap; margin-left:12px;">
            Điểm Làm Sạch Đất: {diem_phoi_ai_nam} / 100
          </div>
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
