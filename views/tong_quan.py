"""Trang Tổng quan: AgTech Command Center Vựa lúa Huyện Yên Thành (Nghệ An).

Kiến trúc Trung tâm Tác nghiệp Viễn thám & Điều hành Nông nghiệp Thông minh:
- Tầng 0: Thanh Lối tắt Điều hướng Nhanh (Quick Navigation Hub đến Luân canh, Dự báo 2027, Bản đồ vệ tinh).
- Tầng 1: Master Timeline Mùa vụ Cốt Lõi (3 Vụ Mùa Chuẩn Yên Thành & 12 Tháng Sinh Thái, loại bỏ tạo đợt thủ công rườm rà).
- Tầng 2: Thẻ Mệnh Lệnh Nông Vụ Khẩn Cấp & Cảnh Báo Thiên Tai Tức Thời (Real-time Live Alert).
- Tầng 3: 5 Thẻ Hero KPI Khí hậu & Viễn thám NASA (Tmax, Mưa GPM, Gió Lào, Ẩm đất SMAP, Sinh khối NDVI).
- Tầng 4: Trung tâm Tác nghiệp Cân đối (Bản đồ số hóa 4 cụm xã : Cockpit Radar Telemetry & 3 Mệnh Lệnh Nông Dân).
- Tầng 5: Analytics Lab (3 Biểu đồ chuỗi đa năm đồng bộ, bo góc hiện đại).
"""
import calendar
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import engine as E
from views.ban_do import hien_ban_do
from views.chung import kpi_the, kpi_the_dot, ve

# 3 ĐỢT MÙA VỤ CHUẨN NÔNG HỌC YÊN THÀNH (CỐ ĐỊNH CHUẨN XỨ NGHỆ)
DEFAULT_DOTS = [
    {
        "id": "dot_1",
        "ten": "Vụ Chiêm Xuân",
        "thangs": [1, 2, 3, 4, 5],
        "cay": "Lúa",
        "mau": "#16A34A",
        "ic": "🌾",
        "mota": "Vụ lúa chính số 1 Yên Thành: Gieo mạ chống rét T1, trỗ rộ T4 né gió Lào, thu hoạch dứt điểm T5.",
        "nang_suat_tiem_nang": "68–72 tạ/ha",
    },
    {
        "id": "dot_2",
        "ten": "Vụ Hè Thu",
        "thangs": [6, 7, 8, 9],
        "cay": "Lúa",
        "mau": "#D97706",
        "ic": "☀️",
        "mota": "Vụ lúa chạy lụt Kênh Vách Bắc: Cấy cực nhanh trước 10/6, chống hạn T7, gặt dứt điểm trước 15/9 né lũ.",
        "nang_suat_tiem_nang": "54–58 tạ/ha",
    },
    {
        "id": "dot_3",
        "ten": "Vụ Đông: Cày Phơi Ải",
        "thangs": [10, 11, 12],
        "cay": "Cày phơi ải đất",
        "mau": "#0284C7",
        "ic": "🚜",
        "mota": "Cày lật sâu 18–22 cm phơi nỏ ruộng diệt 85–90% mầm bệnh đạo ôn, đón nước sông Lam thau chua T12.",
        "nang_suat_tiem_nang": "Hoàn nguyên đất",
    },
]

# ICON & GIAI ĐOẠN SINH THÁI 12 THÁNG LÚA YÊN THÀNH
ICON_THANG = {
    1: "🌱", 2: "🌿", 3: "🌾", 4: "🌸", 5: "✨",
    6: "🌱", 7: "🌿", 8: "🌾", 9: "🌊",
    10: "🚜", 11: "☀️", 12: "💧",
}

TEN_GIAI_DOAN = {
    1: "Gieo mạ & Cấy xuân (Chống rét)",
    2: "Đẻ nhánh rộ lúa xuân (Giữ nước nông)",
    3: "Làm đòng lúa xuân (Bón đón đòng)",
    4: "Trỗ bông rộ lúa xuân (Chống táp gió Lào)",
    5: "Chín & Thu hoạch rộ lúa xuân",
    6: "Cấy hè thu cực nhanh (Né lụt)",
    7: "Đẻ nhánh hè thu (Chống hạn gió Lào)",
    8: "Làm đòng & Trỗ bông hè thu",
    9: "Gặt chạy lũ tiểu mãn (Trước 15/9)",
    10: "Cày lật đất phơi ải (Diệt mầm bệnh)",
    11: "Phơi nỏ ruộng & Nạo vét kênh mương",
    12: "Lấy nước sông Lam đón vụ Chiêm Xuân",
}

# 3 MỆNH LỆNH NÔNG VỤ KHẨN CẤP THEO TỪNG THÁNG CHO BÀ CON NÔNG DÂN
VIEC_CAN_LAM = {
    1: [
        ("💧 Việc 1: Giữ ấm mạ non", "Che phủ nilon trắng 100% diện tích mạ, duy trì rãnh nước ấm chân luống chống rét đậm.", "#16A34A", "🟢"),
        ("🛡️ Việc 2: Phòng chống rét", "Tuyệt đối KHÔNG bón đạm urê khi nhiệt độ ngày đêm dưới 15°C (gây chết mạ).", "#EF4444", "🔴"),
        ("🌾 Việc 3: Chuẩn bị ruộng cấy", "Lấy nước sông Lam qua Ba Ra Đô Lương để bừa ngấu đất, bón lót phân chuồng ủ hoai.", "#0284C7", "🔵"),
    ],
    2: [
        ("💧 Việc 1: Điều tiết nước nông", "Duy trì mực nước nông 2–3 cm trên mặt ruộng để kích thích rễ bén nhanh và đẻ nhánh khỏe.", "#16A34A", "🟢"),
        ("🌾 Việc 2: Bón thúc đợt 1", "Bón thúc đẻ nhánh kết hợp sục bùn làm cỏ sục khí cho rễ phát triển mạnh.", "#0284C7", "🔵"),
        ("🛡️ Việc 3: Diệt ốc bươu vàng", "Bắt ốc bươu vàng và đánh bả chuột đầu bờ bảo vệ dảnh non mới cấy.", "#F59E0B", "🟡"),
    ],
    3: [
        ("🌾 Việc 1: Bón đón đòng", "Bón phân đón đòng (tăng hàm lượng Kali, giảm đạm) khi phát hiện tim đèn nhú 1–2 mm.", "#0284C7", "🔵"),
        ("💧 Việc 2: Tháo cạn phơi ruộng", "Rút nước phơi ruộng nứt chân chim 5–7 ngày để hãm dảnh vô hiệu, giúp rễ ăn sâu chống đổ.", "#16A34A", "🟢"),
        ("🛡️ Việc 3: Phòng trừ đạo ôn lá", "Kiểm tra kỹ vết chấm kim đạo ôn lá trong thời tiết nồm ẩm sương mù.", "#EF4444", "🔴"),
    ],
    4: [
        ("💧 Việc 1: Bơm nước chống táp bông", "Dâng nước mặt ruộng 3–5 cm làm mát gốc lúa, hạ nhiệt khi gặp gió Lào Tây Nam nắng nóng.", "#16A34A", "🟢"),
        ("🛡️ Việc 2: Phun trừ đạo ôn cổ bông", "Phun phòng bệnh đạo ôn cổ bông và rầy nâu lứa 2 ngay khi ruộng lúa trỗ lẹt xẹt 3–5%.", "#EF4444", "🔴"),
        ("🌾 Việc 3: Tuyệt đối dừng bón đạm", "Không rải đạm urê lúc trỗ; chỉ bổ sung phân bón lá vi lượng Kali/Silic chống rụng hạt.", "#F59E0B", "🟡"),
    ],
    5: [
        ("💧 Việc 1: Tháo kiệt nước khô ruộng", "Tháo kiệt nước mặt ruộng trước ngày gặt 7–10 ngày để cứng chân ruộng cho máy gặt liên hợp.", "#16A34A", "🟢"),
        ("🌾 Việc 2: Thu hoạch nhanh gọn", "Huy động máy gặt thu hoạch khi ruộng lúa chín 85–90% để tránh mưa dông làm gãy đổ.", "#0284C7", "🔵"),
        ("🌾 Việc 3: Cày lật gối vụ Hè Thu", "Gặt đến đâu cho máy cày vùi rơm rạ đến đó, lấy nước Ba Ra làm đất gieo cấy lúa hè thu ngay.", "#F59E0B", "🟡"),
    ],
    6: [
        ("🌾 Việc 1: Cấy lúa hè thu cực nhanh", "Hoàn thành gieo cấy hè thu trước ngày 10/6 để kịp thời gian né lũ tiểu mãn tháng 9.", "#EF4444", "🔴"),
        ("💧 Việc 2: Mở nước Ba Ra hồi sinh", "Mở hết công suất cống Kênh chính cấp nước dưỡng mạ hè thu bén rễ hồi xanh.", "#16A34A", "🟢"),
        ("🌾 Việc 3: Chọn giống cực ngắn ngày", "Cơ cấu giống ngắn ngày: Khang Dân 18, BT7, Đài Thơm 8 chống chịu nhiệt độ cao.", "#0284C7", "🔵"),
    ],
    7: [
        ("💧 Việc 1: Chống hạn gió Lào", "Luân phiên dẫn nước Kênh chính, không để ruộng bị nứt nẻ khô kiệt trong đợt nắng nóng.", "#16A34A", "🟢"),
        ("🛡️ Việc 2: Phun trừ sâu cuốn lá", "Theo dõi rầy lưng trắng và sâu cuốn lá nhỏ lứa 4, phun trừ khi mật độ vượt ngưỡng.", "#F59E0B", "🟡"),
        ("🌾 Việc 3: Bón thúc sớm đợt 2", "Bón thúc đợt 2 sớm (đủ đạm, lân, kali) để lúa đẻ nhánh tập trung trước 15/7.", "#0284C7", "🔵"),
    ],
    8: [
        ("💧 Việc 1: Đảm bảo nước trỗ hè thu", "Duy trì mực nước 5 cm làm mát bông lúa, chống táp phấn khi trỗ gặp gió Tây Nam.", "#16A34A", "🟢"),
        ("🛡️ Việc 2: Phòng bệnh bạc lá vi khuẩn", "Phun thuốc phòng bệnh bạc lá, đốm sọc vi khuẩn sau các trận mưa dông chiều.", "#EF4444", "🔴"),
        ("🌊 Việc 3: Gia cố bờ vùng bờ thửa", "Kiểm tra hệ thống cống rãnh nội đồng, sẵn sàng phương án tiêu úng khi có mưa bão lớn.", "#0284C7", "🔵"),
    ],
    9: [
        ("🌾 Việc 1: Gặt chạy lụt khẩn cấp", "Thu hoạch toàn bộ lúa hè thu trước ngày 15–20/9 theo phương châm 'Xanh nhà hơn già đồng'.", "#EF4444", "🔴"),
        ("🌊 Việc 2: Mở cống Kênh Vách Bắc", "Khơi thông dòng chảy Kênh Vách Bắc, vận hành trạm bơm tiêu thoát nước ra biển.", "#0284C7", "🔵"),
        ("🌾 Việc 3: Phơi sấy thóc khẩn trương", "Đưa lúa vào lò sấy nông sản tập trung, tránh mưa bão làm nảy mầm hạt thóc.", "#16A34A", "🟢"),
    ],
    10: [
        ("🌾 Việc 1: Cày lật đất phơi ải", "Cày sâu 18–22 cm phơi khô nỏ ruộng lúa 30–45 ngày nhằm diệt mầm nấm bệnh lưu cữu.", "#16A34A", "🟢"),
        ("🌱 Việc 2: Rải vôi khử chua", "Bón 20–25 kg vôi bột/sào để hạ phèn và khử độc chất hữu cơ rơm rạ trong đất.", "#0284C7", "🔵"),
        ("🍂 Việc 3: Rút cạn nước phơi ải", "Nạo vét rãnh thoát nước, tạo điều kiện cho đất ruộng khô nứt chân chim phá vỡ tầng yếm khí.", "#16A34A", "🟢"),
    ],
    11: [
        ("🌾 Việc 1: Tiếp tục phơi ải đất", "Giữ ruộng khô nỏ, tận dụng ánh nắng hanh heo tiêu diệt bào tử đạo ôn và ấu trùng rầy.", "#16A34A", "🟢"),
        ("💧 Việc 2: Nạo vét Kênh Ba Ra", "Phát động toàn dân ra quân nạo vét bùn đất Kênh chính và hệ thống cống nội đồng.", "#0284C7", "🔵"),
        ("🍂 Việc 3: Kiểm tra đất nỏ ải", "Đánh giá tầng đất canh tác đã oxy hóa giải phóng Fe2+, H2S để chuẩn bị đón nước đổ ải.", "#16A34A", "🟢"),
    ],
    12: [
        ("🌾 Việc 1: Chuẩn bị giống lúa xuân", "Chuẩn bị giống lúa thuần chất lượng cao: ST25, J02, TBR225, Bắc Thịnh, ngâm ủ đúng kỹ thuật.", "#0284C7", "🔵"),
        ("💧 Việc 2: Lấy nước đổ ải đầu vụ", "Mở cống Ba Ra Đô Lương lấy nước phù sa sông Lam vào đồng để bừa dập đất.", "#16A34A", "🟢"),
        ("🛡️ Việc 3: Làm mạ che phủ nilon", "Gieo mạ vụ xuân từ cuối tháng 12, che phủ nilon trắng 100% diện tích chống rét.", "#EF4444", "🔴"),
    ],
}


def hop_thoai_tao_dot(nam, dl, vung):
    """Trợ lý tạo đợt canh tác (Hỗ trợ tương thích ngược cho unit test và module phụ)."""
    return DEFAULT_DOTS


def ve_dong_ho_rui_ro(w, muc, mau):
    """Vẽ đồng hồ bán nguyệt đo mức độ rủi ro thời tiết vụ lúa Yên Thành."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=w,
        number={"suffix": "%", "font": {"size": 28, "color": "#0F172A", "family": "Be Vietnam Pro"}},
        title={"text": f"<b>{muc.upper()}</b>", "font": {"size": 13, "color": mau, "family": "Be Vietnam Pro"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickwidth": 1, "tickcolor": "#CBD5E1"},
            "bar": {"color": mau, "thickness": 0.35},
            "bgcolor": "#F8FAFC",
            "borderwidth": 1,
            "bordercolor": "#E2E8F0",
            "steps": [
                {"range": [0, 35], "color": "rgba(34, 197, 94, 0.15)"},
                {"range": [35, 55], "color": "rgba(245, 158, 11, 0.15)"},
                {"range": [55, 100], "color": "rgba(239, 68, 68, 0.15)"},
            ],
            "threshold": {
                "line": {"color": "#DC2626", "width": 3},
                "thickness": 0.8,
                "value": 55,
            },
        },
    ))
    fig.update_layout(
        height=145,
        margin=dict(l=15, r=15, t=30, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


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


def hien(ctx):
    dl, diem, nam_df = ctx["dl"], ctx["diem"], ctx["nam_df"]
    nam, years = ctx["nam"], ctx["years"]
    vung = "Yên Thành"

    # LỌC DUY NHẤT DỮ LIỆU HUYỆN YÊN THÀNH
    chuoi = dl[(dl.year == nam) & (dl.huyen == vung)].sort_values("month")
    co_thang = sorted(chuoi.month.unique()) if not chuoi.empty else list(range(1, 13))

    # =========================================================================
    # TẦNG 0: THANH LỐI TẮT ĐIỀU HƯỚNG NHANH (QUICK NAVIGATION HUB)
    # =========================================================================
    with st.container(border=True):
        col_hdr_left, col_hdr_right = st.columns([6.5, 3.5], gap="small")
        with col_hdr_left:
            st.markdown(
                f"""
                <div style="padding:2px 0;">
                  <div style="font-size:11px; font-weight:750; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">🛰️ VIỄN THÁM NÔNG NGHIỆP NASA · VỰA LÚA XỨ NGHỆ</div>
                  <div style="font-size:22px; font-weight:800; color:#0F172A; letter-spacing:-0.4px; line-height:1.2; margin-top:2px;">🌾 Huyện Yên Thành · Trung Tâm Giám Sát Nông Vụ {nam}</div>
                  <div style="font-size:12px; color:#475569; margin-top:2px;">Hệ thống Thủy nông Ba Ra Đô Lương & Giám sát Viễn thám NASA MODIS, SMAP, GPM</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_hdr_right:
            # Lối tắt chuyển trang mượt mà (sử dụng chuyen_trang_den an toàn)
            st.markdown("<div style='font-size:11px; font-weight:750; color:#64748B; text-transform:uppercase; margin-bottom:4px;'>Lối tắt nhanh:</div>", unsafe_allow_html=True)
            c_nav1, c_nav2 = st.columns(2, gap="small")
            with c_nav1:
                if st.button("🌾 Lập Luân Canh", key="btn_quick_luan_canh", use_container_width=True, help="Chuyển đến module Kế hoạch Luân canh & Sức khỏe Đất"):
                    st.session_state["chuyen_trang_den"] = "🌾  Kế hoạch Luân canh & Sức khỏe Đất"
                    st.rerun()
            with c_nav2:
                if st.button("🎯 Dự Báo 2027", key="btn_quick_du_bao_2027", use_container_width=True, help="Chuyển đến module Thời vụ Gieo cấy & Dự báo Năng suất 2027"):
                    st.session_state["chuyen_trang_den"] = "🎯  Thời vụ & Dự báo Năng suất 2027"
                    st.rerun()

        st.markdown("<hr style='margin:10px 0 12px 0; border-color:#F1F5F9;'>", unsafe_allow_html=True)

        # =====================================================================
        # TẦNG 1: BỘ CHỌN MÙA VỤ CHUẨN XỨ NGHỆ, 12 THÁNG & CHỌN NGÀY CỤ THỂ
        # =====================================================================
        col_mode_lbl, col_mode_ctrl = st.columns([5.5, 4.5], gap="small")
        with col_mode_ctrl:
            che_do_xem = st.segmented_control(
                "Chế độ khảo sát:",
                options=["🌾 3 Vụ Mùa Chuẩn", "📅 Theo 12 Tháng", "📆 Theo Ngày Cụ Thể"],
                default="🌾 3 Vụ Mùa Chuẩn",
                key=f"seg_che_do_khao_sat_{nam}",
                label_visibility="collapsed",
            ) if hasattr(st, "segmented_control") else st.radio("Chế độ khảo sát:", ["🌾 3 Vụ Mùa Chuẩn", "📅 Theo 12 Tháng", "📆 Theo Ngày Cụ Thể"], horizontal=True, key=f"rad_che_do_{nam}", label_visibility="collapsed")

        # ---------------------------------------------------------------------
        # CHẾ ĐỘ 1: THEO 3 VỤ MÙA CHUẨN XỨ NGHỆ (YÊN THÀNH STANDARD)
        # ---------------------------------------------------------------------
        if che_do_xem == "🌾 3 Vụ Mùa Chuẩn":
            options_dot = [f"{d['ic']} {d['ten']} (T{min(d['thangs'])}–T{max(d['thangs'])})" for d in DEFAULT_DOTS]
            
            dot_label_chon = st.pills(
                "Chọn vụ mùa chuẩn Yên Thành:",
                options=options_dot,
                default=options_dot[0],
                key=f"pills_dot_canh_tac_{nam}",
                label_visibility="collapsed",
            )
            if not dot_label_chon:
                dot_label_chon = options_dot[0]

            idx_dot = options_dot.index(dot_label_chon)
            cur_dot = DEFAULT_DOTS[idx_dot]
            thangs_dot = cur_dot["thangs"]

            # RENDER DÒNG THỜI GIAN 12 THÁNG TRỰC QUAN (HIGHLIGHT CÁC THÁNG TRONG VỤ)
            ribbon_boxes = ""
            for m in range(1, 13):
                ic = ICON_THANG.get(m, "")
                if m in thangs_dot:
                    bg_m = "#EFF6FF" if cur_dot["mau"] == "#0284C7" else ("#FEF3C7" if cur_dot["mau"] == "#D97706" else "#DCFCE7")
                    border_m = f"border:2px solid {cur_dot['mau']};"
                    color_m = cur_dot["mau"]
                    badge_m = f'<div style="font-size:9.5px; font-weight:800; color:{cur_dot["mau"]};">ĐANG XEM</div>'
                else:
                    bg_m = "#F8FAFC"
                    border_m = "border:1px dashed #CBD5E1;"
                    color_m = "#94A3B8"
                    badge_m = '<div style="font-size:9.5px; color:#94A3B8;">—</div>'

                ribbon_boxes += f"""
                <div style="flex:1 1 0; background:{bg_m}; {border_m} border-radius:8px; padding:6px 2px; text-align:center; min-width:48px;">
                  <div style="font-size:12px; font-weight:800; color:{color_m};">T{m}</div>
                  <div style="font-size:14px; margin:2px 0;">{ic}</div>
                  {badge_m}
                </div>
                """

            st.markdown(
                f"""
                <div style="display:flex; gap:6px; overflow-x:auto; padding:4px 0 8px 0;">
                  {ribbon_boxes}
                </div>
                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid {cur_dot['mau']}; border-radius:8px; padding:8px 14px; font-size:12px; color:#1E293B; margin-top:2px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                  <div>
                    <b>📌 {cur_dot['ten']}:</b> Gồm <b>{len(thangs_dot)} tháng</b> (Tháng {min(thangs_dot)} → Tháng {max(thangs_dot)}) · Cây trồng chủ lực: <b style="color:{cur_dot['mau']};">{cur_dot['cay']}</b> — <i>{cur_dot['mota']}</i>
                  </div>
                  <div style="font-size:11.5px; font-weight:750; color:{cur_dot['mau']}; background:#FFFFFF; border:1px solid {cur_dot['mau']}; border-radius:999px; padding:2px 12px;">
                    {cur_dot['ic']} Tiềm năng: {cur_dot['nang_suat_tiem_nang']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            thang = 4 if 4 in thangs_dot else (8 if 8 in thangs_dot else thangs_dot[len(thangs_dot)//2])

        # ---------------------------------------------------------------------
        # CHẾ ĐỘ 2: THEO 12 THÁNG CHI TIẾT
        # ---------------------------------------------------------------------
        elif che_do_xem == "📅 Theo 12 Tháng":
            thang_khoi_tao = ctx.get("thang", 4)
            if thang_khoi_tao not in co_thang:
                thang_khoi_tao = 4 if 4 in co_thang else co_thang[0]

            thang = st.pills(
                "Chọn tháng:",
                options=co_thang,
                default=thang_khoi_tao,
                format_func=lambda m: f"T{m} {ICON_THANG.get(m, '')}",
                label_visibility="collapsed",
                key=f"pills_thang_master_{nam}",
            )
            if not thang:
                thang = thang_khoi_tao

            vu_ten = "Vụ Chiêm Xuân (Vụ chính)" if thang <= 5 else ("Vụ Hè Thu (Chống hạn & gặt chạy lũ)" if thang <= 9 else "Vụ Đông / Cày phơi ải đất")
            gd_ten = TEN_GIAI_DOAN.get(thang, "")
            st.markdown(
                f'<div style="font-size:11.5px; color:#475569; margin-top:4px;">'
                f'📌 Đang chọn <b>Tháng {thang}</b> · <b>{vu_ten}</b> — Giai đoạn sinh thái: <b style="color:#0F172A;">{gd_ten}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ---------------------------------------------------------------------
        # CHẾ ĐỘ 3: THEO NGÀY CỤ THỂ (DAILY LOOKUP & TELEMETRY)
        # ---------------------------------------------------------------------
        else:
            df_daily = _tai_daily_power()
            if not df_daily.empty:
                min_date = df_daily["date_dt"].dt.date.min()
                max_date = df_daily["date_dt"].dt.date.max()
            else:
                min_date = datetime.date(2018, 1, 1)
                max_date = datetime.date(2026, 11, 15)

            key_d_tq = f"date_pick_tongquan_{nam}"
            cur_d_init = datetime.date(nam if nam <= 2026 else 2026, 4, 15)
            if cur_d_init > max_date:
                cur_d_init = max_date
            if cur_d_init < min_date:
                cur_d_init = min_date

            if key_d_tq not in st.session_state or not isinstance(st.session_state[key_d_tq], datetime.date):
                st.session_state[key_d_tq] = cur_d_init

            col_pick, col_fast = st.columns([4.2, 7.8], gap="small")
            with col_pick:
                st.markdown('<div style="font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;">📆 Chọn ngày giám sát viễn thám:</div>', unsafe_allow_html=True)
                ngay_chon = st.date_input(
                    "Ngày giám sát:",
                    value=st.session_state[key_d_tq],
                    min_value=min_date,
                    max_value=max_date,
                    key=f"widget_{key_d_tq}",
                    format="DD/MM/YYYY",
                    label_visibility="collapsed",
                )
                if ngay_chon:
                    st.session_state[key_d_tq] = ngay_chon

            with col_fast:
                st.markdown('<div style="font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;">⚡ Lối tắt sự kiện nông học / thời tiết:</div>', unsafe_allow_html=True)
                cf1, cf2, cf3 = st.columns(3, gap="small")
                with cf1:
                    if st.button("🌸 Trỗ xuân (15/04)", key="btn_tq_xuan", use_container_width=True):
                        st.session_state[key_d_tq] = datetime.date(nam if nam <= 2026 else 2026, 4, 15)
                        st.rerun()
                with cf2:
                    if st.button("🔥 Gió Lào (22/06)", key="btn_tq_han", use_container_width=True):
                        st.session_state[key_d_tq] = datetime.date(nam if nam <= 2026 else 2026, 6, 22)
                        st.rerun()
                with cf3:
                    if st.button("🌊 Mưa lũ (19/10)", key="btn_tq_lu", use_container_width=True):
                        st.session_state[key_d_tq] = datetime.date(nam if nam <= 2026 else 2026, 10, 19)
                        st.rerun()

            sel_date_tq = st.session_state[key_d_tq]
            thang = sel_date_tq.month

            # Trích xuất số liệu telemetry thực đo ngày
            tele_str = ""
            if not df_daily.empty:
                r_day = df_daily[df_daily["date_dt"].dt.date == sel_date_tq]
                if not r_day.empty:
                    r0 = r_day.iloc[0]
                    tmax_d = float(r0.get("T2M_MAX", 0))
                    tmin_d = float(r0.get("T2M_MIN", 0))
                    mua_d = float(r0.get("PRECTOTCORR", 0)) if pd.notna(r0.get("PRECTOTCORR")) else 0.0
                    rh_d = float(r0.get("RH2M", 70)) if pd.notna(r0.get("RH2M")) else 70.0
                    rad_d = float(r0.get("ALLSKY_SFC_SW_DWN", 15)) if pd.notna(r0.get("ALLSKY_SFC_SW_DWN")) else 15.0
                    tele_str = (
                        f'Tmax: <b style="color:#DC2626;">{tmax_d:.1f}°C</b> · '
                        f'Tmin: <b style="color:#0284C7;">{tmin_d:.1f}°C</b> · '
                        f'Mưa: <b style="color:#0284C7;">{mua_d:.1f} mm</b> · '
                        f'Ẩm RH: <b style="color:#16A34A;">{rh_d:.0f}%</b> · '
                        f'Bức xạ: <b style="color:#D97706;">{rad_d:.1f} MJ/m²</b>'
                    )

            vu_ten = "Vụ Chiêm Xuân (Vụ chính)" if thang <= 5 else ("Vụ Hè Thu (Chống hạn & gặt chạy lũ)" if thang <= 9 else "Vụ Đông / Cày phơi ải đất")
            gd_ten = TEN_GIAI_DOAN.get(thang, "")
            st.markdown(
                f'<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:6px 12px; margin-top:4px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; font-size:11.5px; gap:8px;">'
                f'  <div>📌 Đang giám sát: <b style="color:#0F766E; font-size:12.5px;">Ngày {sel_date_tq.strftime("%d/%m/%Y")}</b> · <b>{vu_ten}</b> — Giai đoạn: <b>{gd_ten}</b></div>'
                f'  <div style="color:#334155;">{"🛰️ Telemetry Ngày: " + tele_str if tele_str else ""}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    ctx["thang"] = thang
    ctx["vung"] = vung

    if chuoi.empty or thang not in set(chuoi.month):
        st.warning(f"Chưa có chuỗi số liệu tháng {thang} cho huyện Yên Thành.")
        return

    r = chuoi[chuoi.month == thang].iloc[0]
    ctx["r"] = r

    # =========================================================================
    # TẦNG 2: THẺ MỆNH LỆNH NÔNG VỤ KHẨN CẤP & CẢNH BÁO THIÊN TAI TỨC THỜI
    # =========================================================================
    nong35_cur = int(r.get("nong35", 0)) if pd.notna(r.get("nong35")) else 0
    mua_cur = float(r.get("mua_mm", 80.0)) if pd.notna(r.get("mua_mm")) else 80.0
    tmax_cur = float(r.get("tmax", 30.0)) if pd.notna(r.get("tmax")) else 30.0
    sm_cur = float(r.get("sm_rootzone", 0.28)) if pd.notna(r.get("sm_rootzone")) else 0.28

    if thang in [4, 6, 7] and (nong35_cur >= 5 or tmax_cur >= 35.0):
        # CẢNH BÁO GIÓ LÀO
        st.markdown(
            f"""
            <div style="background:#FEF2F2; border:1.5px solid #F87171; border-left:6px solid #DC2626; border-radius:10px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div>
                <div style="font-size:13px; font-weight:800; color:#DC2626; display:flex; align-items:center; gap:6px;">
                  <span>🔥</span> CẢNH BÁO THỜI TIẾT CỰC ĐOAN: NẮNG NÓNG GIÓ LÀO TÂY NAM (Tháng {thang}/{nam})
                </div>
                <div style="font-size:12px; color:#450A0A; margin-top:3px;">
                  Ghi nhận <b>{nong35_cur} ngày</b> nhiệt độ ≥35°C (Đỉnh nhiệt <b>{tmax_cur:.1f}°C</b>). Nguy cơ táp hoa, khô phấn hoa lúa làm lép hạt hàng loạt.
                </div>
              </div>
              <div style="background:#FFFFFF; border:1px solid #DC2626; border-radius:8px; padding:6px 12px; font-size:12px; font-weight:750; color:#DC2626;">
                ⚡ MỆNH LỆNH: Dâng nước đệm 3–5 cm làm mát gốc ruộng
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif thang in [9, 10] and mua_cur >= 300.0:
        # CẢNH BÁO BÃO LŨ
        st.markdown(
            f"""
            <div style="background:#EFF6FF; border:1.5px solid #60A5FA; border-left:6px solid #2563EB; border-radius:10px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div>
                <div style="font-size:13px; font-weight:800; color:#2563EB; display:flex; align-items:center; gap:6px;">
                  <span>🌊</span> CẢNH BÁO MƯA BÃO & LŨ TIỂU MÃN KÊNH VÁCH BẮC (Tháng {thang}/{nam})
                </div>
                <div style="font-size:12px; color:#1E3A8A; margin-top:3px;">
                  Vũ lượng tích lũy GPM đạt <b>{mua_cur:.0f} mm</b>. Nguy cơ ngập úng nghiêm trọng vùng trũng lòng chảo (Bảo Thành, Vĩnh Thành).
                </div>
              </div>
              <div style="background:#FFFFFF; border:1px solid #2563EB; border-radius:8px; padding:6px 12px; font-size:12px; font-weight:750; color:#2563EB;">
                ⚡ MỆNH LỆNH: Gặt chạy lụt trước 15/9 · Vận hành trạm bơm tiêu
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif thang in [1, 2] and tmax_cur < 20.0:
        # CẢNH BÁO RÉT ĐẬM
        st.markdown(
            f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-left:6px solid #16A34A; border-radius:10px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div>
                <div style="font-size:13px; font-weight:800; color:#16A34A; display:flex; align-items:center; gap:6px;">
                  <span>❄️</span> CẢNH BÁO RÉT ĐẬM ĐẦU VỤ CHIÊM XUÂN (Tháng {thang}/{nam})
                </div>
                <div style="font-size:12px; color:#14532D; margin-top:3px;">
                  Nhiệt độ ngày đêm thấp. Cây mạ non rất nhạy cảm với rét buốt và sương muối.
                </div>
              </div>
              <div style="background:#FFFFFF; border:1px solid #16A34A; border-radius:8px; padding:6px 12px; font-size:12px; font-weight:750; color:#16A34A;">
                ⚡ MỆNH LỆNH: Che phủ nilon trắng 100% · Không bón đạm urê
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # THỜI TIẾT TỐI ƯU
        st.markdown(
            f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:5px solid #0F766E; border-radius:10px; padding:8px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
              <div style="font-size:12px; color:#0F172A;">
                ✅ <b>Tình trạng môi trường viễn thám NASA ổn định:</b> Nhiệt độ <b>{tmax_cur:.1f}°C</b> · Độ ẩm rễ SMAP <b>{sm_cur*100:.1f}%</b> · Vũ lượng <b>{mua_cur:.0f} mm</b>. Ruộng lúa sinh trưởng thuận lợi.
              </div>
              <div style="font-size:11.5px; color:#0F766E; font-weight:750; background:#CCFBF1; padding:2px 10px; border-radius:999px;">
                💧 Nguồn nước Ba Ra Đô Lương: Đủ ẩm tự chảy
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # TẦNG 3: 5 THẺ HERO KPI KHÍ HẬU & VIỄN THÁM
    # =========================================================================
    c = st.columns(5)
    
    if che_do_xem == "🌾 3 Vụ Mùa Chuẩn":
        sub_dot = chuoi[chuoi.month.isin(thangs_dot)]
        sub_dot_25 = dl[(dl.year == 2025) & (dl.huyen == vung) & (dl.month.isin(thangs_dot))]
        
        v_tmax = float(sub_dot["tmax"].mean()) if not sub_dot.empty else 30.0
        v_tmax_peak = float(sub_dot["tmax"].max()) if not sub_dot.empty else 35.0
        v_tmax_25 = float(sub_dot_25["tmax"].mean()) if not sub_dot_25.empty else v_tmax
        d_tmax = v_tmax - v_tmax_25
        
        v_mua = float(sub_dot["mua_mm"].sum()) if not sub_dot.empty else 0.0
        v_mua_25 = float(sub_dot_25["mua_mm"].sum()) if not sub_dot_25.empty else v_mua
        d_mua = v_mua - v_mua_25
        
        v_nong = int(sub_dot["nong35"].sum()) if not sub_dot.empty else 0
        v_nong_25 = int(sub_dot_25["nong35"].sum()) if not sub_dot_25.empty else v_nong
        d_nong = v_nong - v_nong_25
        
        v_sm = float(sub_dot["sm_rootzone"].mean() * 100) if not sub_dot.empty else 28.0
        v_sm_25 = float(sub_dot_25["sm_rootzone"].mean() * 100) if not sub_dot_25.empty else v_sm
        d_sm = v_sm - v_sm_25
        
        v_ndvi = float(sub_dot["ndvi"].max()) if not sub_dot.empty else 0.65
        v_ndvi_25 = float(sub_dot_25["ndvi"].max()) if not sub_dot_25.empty else v_ndvi
        d_ndvi = v_ndvi - v_ndvi_25

        th = [
            kpi_the_dot(f"Tmax TB ({len(thangs_dot)}T)", v_tmax, "°C", "#F97316", f"Đỉnh {v_tmax_peak:.1f}°C", d_tmax, "cao", "{:.1f}"),
            kpi_the_dot(f"Tổng Mưa Cả Vụ", v_mua, "mm", "#0EA5E9", f"Tích lũy {len(thangs_dot)}T", d_mua, "cao", "{:.0f}"),
            kpi_the_dot(f"Gió Lào Cả Vụ", v_nong, "ngày", "#EF4444", f"≥35°C ({len(thangs_dot)}T)", d_nong, "cao", "{:.0f}"),
            kpi_the_dot(f"Ẩm Ruộng TB (SMAP)", v_sm, "%", "#10B981", f"Tầng rễ {len(thangs_dot)}T", d_sm, "thap", "{:.0f}"),
            kpi_the_dot(f"NDVI Đỉnh Mùa Vụ", v_ndvi, "", "#84CC16", f"Sinh khối cực đại", d_ndvi, "thap", "{:.2f}"),
        ]
    else:
        th = [
            kpi_the("Nhiệt độ cao nhất", "tmax", "°C", "#F97316", chuoi, thang, "cao", "{:.1f}"),
            kpi_the("Lượng mưa tích lũy", "mua_mm", "mm", "#0EA5E9", chuoi, thang, "cao"),
            kpi_the(f"Nắng nóng ≥{E.NGUONG_NONG}°C (Gió Lào)", "nong35", "ngày", "#EF4444", chuoi, thang, "cao"),
            kpi_the("Độ ẩm ruộng lúa (SMAP)", "sm_rootzone", "%", "#10B981", chuoi, thang, "thap", "{:.0f}", 100),
            kpi_the("Sinh khối lúa (NDVI)", "ndvi", "", "#84CC16", chuoi, thang, "thap", "{:.2f}"),
        ]

    for col, html in zip(c, th):
        col.markdown(html, unsafe_allow_html=True)

    st.write("")

    # =========================================================================
    # TẦNG 4: TRUNG TÂM TÁC NGHIỆP CÂN ĐỐI (BẢN ĐỒ SỐ HÓA : COCKPIT NÔNG HỌC)
    # =========================================================================
    trai, phai = st.columns([6.8, 3.2], gap="medium")

    # CỘT TRÁI: BẢN ĐỒ SỐ HÓA 4 CỤM XÃ YÊN THÀNH
    with trai:
        hien_ban_do(ctx)

    # CỘT PHẢI: COCKPIT NÔNG VỤ & 3 MỆNH LỆNH NÔNG VỤ KHẨN CẤP
    with phai:
        loc_lua = diem[(diem.huyen == vung) & (diem.year == nam) & (diem.month == thang) & (diem.cay == "Lúa")]
        if not loc_lua.empty and pd.notna(loc_lua.iloc[0].get("rui_ro")):
            x = loc_lua.iloc[0]
            w = float(x["rui_ro"])
            muc = x.get("muc", "Nên trồng")
            mau = x.get("mau") or "#22C55E"
        else:
            w = 15.0
            muc = "Cày ải dưỡng ruộng"
            mau = "#5B6B79"

        # KHỐI 1: ĐỒNG HỒ RỦI RO & 3 CHỈ SỐ TELEMETRY KHÍ TƯỢNG
        with st.container(border=True):
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                f'<span class="cap" style="margin:0; font-size:14px;">🧭 Radar Rủi ro Mùa vụ & Telemetry</span>'
                f'<span style="font-size:11px; font-weight:750; color:{mau}; background:#F8FAFC; border:1px solid {mau}; border-radius:999px; padding:2px 8px;">{muc}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            col_gauge, col_telemetry = st.columns([1, 1], gap="small")
            with col_gauge:
                ve(ve_dong_ho_rui_ro(w, muc, mau), che_do="co_dinh")

            with col_telemetry:
                tmax_val = r.get("tmax", 30.0) if pd.notna(r.get("tmax")) else 30.0
                nong35_val = int(r.get("nong35", 0)) if pd.notna(r.get("nong35")) else 0
                sm_val = r.get("sm_rootzone", 0.35) if pd.notna(r.get("sm_rootzone")) else 0.35
                ndvi_val = r.get("ndvi", 0.65) if pd.notna(r.get("ndvi")) else 0.65

                # 1. Nhiệt độ
                if nong35_val >= 5 or tmax_val >= 35.0:
                    d_nhiet = (f"{tmax_val:.1f}°C ({nong35_val}d Lào)", "#FEE2E2", "#DC2626")
                elif tmax_val >= 32.0:
                    d_nhiet = (f"{tmax_val:.1f}°C (Nắng)", "#FEF3C7", "#D97706")
                else:
                    d_nhiet = (f"{tmax_val:.1f}°C (Mát)", "#DCFCE7", "#16A34A")

                # 2. Nước Ba Ra
                if thang == 9:
                    d_nuoc = ("Xả cống Vách Bắc", "#FEF3C7", "#D97706")
                elif sm_val >= 0.25:
                    d_nuoc = (f"Ẩm {sm_val*100:.0f}% (Đủ nước)", "#DCFCE7", "#16A34A")
                else:
                    d_nuoc = (f"Ẩm {sm_val*100:.0f}% (Cần cấp)", "#FEE2E2", "#DC2626")

                # 3. Sinh khối NDVI
                if ndvi_val >= 0.65:
                    d_sinh = (f"NDVI {ndvi_val:.2f} (Khỏe)", "#DCFCE7", "#16A34A")
                elif ndvi_val >= 0.50:
                    d_sinh = (f"NDVI {ndvi_val:.2f} (Phát triển)", "#FEF3C7", "#D97706")
                else:
                    d_sinh = (f"NDVI {ndvi_val:.2f} (Ải)", "#F1F5F9", "#64748B")

                st.markdown(
                    f'<div style="display:flex; flex-direction:column; gap:6px; padding-top:2px;">'
                    f'<div style="background:{d_nhiet[1]}; border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center;">'
                    f'<span style="font-size:11px; font-weight:700; color:{d_nhiet[2]};">🌡️ Nhiệt & Lào:</span>'
                    f'<span style="font-size:11px; font-weight:800; color:{d_nhiet[2]};">{d_nhiet[0]}</span>'
                    f'</div>'
                    f'<div style="background:{d_nuoc[1]}; border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center;">'
                    f'<span style="font-size:11px; font-weight:700; color:{d_nuoc[2]};">💧 Nước Ba Ra:</span>'
                    f'<span style="font-size:11px; font-weight:800; color:{d_nuoc[2]};">{d_nuoc[0]}</span>'
                    f'</div>'
                    f'<div style="background:{d_sinh[1]}; border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center;">'
                    f'<span style="font-size:11px; font-weight:700; color:{d_sinh[2]};">🌿 Sinh khối:</span>'
                    f'<span style="font-size:11px; font-weight:800; color:{d_sinh[2]};">{d_sinh[0]}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # KHỐI 2: 3 MỆNH LỆNH NÔNG VỤ KHẨN CẤP CHO NÔNG DÂN
        with st.container(border=True):
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">'
                f'<span class="cap" style="margin:0; font-size:14px;">⚡ 3 Mệnh Lệnh Nông Vụ Khẩn Cấp (Tháng {thang})</span>'
                f'<span style="font-size:10.5px; font-weight:750; color:#0F172A; background:#F1F5F9; border-radius:999px; padding:2px 8px;">Nhiệm vụ nông dân</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            cac_viec = VIEC_CAN_LAM.get(thang, VIEC_CAN_LAM[4])
            for tieu_de_viec, noi_dung_viec, mau_viec, ic_viec in cac_viec:
                st.markdown(
                    f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid {mau_viec}; border-radius:8px; padding:7px 10px; margin-bottom:5px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">'
                    f'<div style="display:flex; align-items:center; gap:6px;">'
                    f'<span style="font-size:12px;">{ic_viec}</span>'
                    f'<span style="font-size:12.5px; font-weight:800; color:#0F172A;">{tieu_de_viec}</span>'
                    f'</div>'
                    f'<div style="font-size:11.5px; color:#334155; margin-top:2px; line-height:1.4;">'
                    f'{noi_dung_viec}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Thẻ giống lúa chủ lực
            st.markdown(
                f'<div style="margin-top:6px; padding-top:5px; border-top:1px dashed #E2E8F0; display:flex; align-items:center; gap:5px; flex-wrap:wrap;">'
                f'<span style="font-size:11px; font-weight:750; color:#64748B;">🌾 Giống chủ lực:</span>'
                f'<span style="background:#F1F5F9; border:1px solid #CBD5E1; color:#0F172A; font-size:10.5px; font-weight:700; border-radius:6px; padding:1px 6px;">ST25</span>'
                f'<span style="background:#F1F5F9; border:1px solid #CBD5E1; color:#0F172A; font-size:10.5px; font-weight:700; border-radius:6px; padding:1px 6px;">J02</span>'
                f'<span style="background:#F1F5F9; border:1px solid #CBD5E1; color:#0F172A; font-size:10.5px; font-weight:700; border-radius:6px; padding:1px 6px;">TBR225</span>'
                f'<span style="background:#F1F5F9; border:1px solid #CBD5E1; color:#0F172A; font-size:10.5px; font-weight:700; border-radius:6px; padding:1px 6px;">Bắc Thịnh</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TẦNG 5: ANALYTICS LAB (3 BIỂU ĐỒ ĐA NĂM ĐỒNG BỘ)
    # =========================================================================
    st.write("")
    with st.expander("📊 Mở rộng: Phân tích Xu hướng Khí tượng & Lịch sử Gió Lào Yên Thành (3 Biểu đồ Chuyên sâu)", expanded=False):
        a, b, c3 = st.columns(3, gap="medium")

        # Biểu đồ 1: Mưa và Tmax 12 tháng tại Yên Thành
        with a, st.container(border=True):
            st.markdown('<p class="cap" style="font-size:13.5px; margin-bottom:4px;">🌧️ Mưa & Nhiệt độ 12 tháng tại Yên Thành</p>', unsafe_allow_html=True)
            f = make_subplots(specs=[[{"secondary_y": True}]])
            f.add_bar(x=chuoi.month, y=chuoi.mua_mm, name="Mưa (mm)", marker=dict(color="#38BDF8", cornerradius=4))
            if "tmax" in chuoi.columns:
                f.add_scatter(
                    x=chuoi.month, y=chuoi.tmax, name="Tmax (°C)", mode="lines+markers",
                    line=dict(color="#F97316", width=2.5), secondary_y=True,
                )
            f.add_vrect(x0=thang - 0.5, x1=thang + 0.5, fillcolor="#0F172A", opacity=0.08, line_width=0)
            f.update_xaxes(dtick=1, tickprefix="T", showgrid=False)
            f.update_layout(
                height=250, margin=dict(l=6, r=6, t=20, b=6),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.15, x=0),
            )
            ve(f, che_do="co_dinh")

        # Biểu đồ 2: Số ngày nắng nóng gió Lào >= 35°C tại Yên Thành
        with b, st.container(border=True):
            st.markdown(f'<p class="cap" style="font-size:13.5px; margin-bottom:4px;">🔥 Ngày gió Lào ≥{E.NGUONG_NONG}°C qua các năm</p>', unsafe_allow_html=True)
            n = nam_df[(nam_df.huyen == vung) & (nam_df.nguong == E.NGUONG_NONG)].sort_values("nam") if len(nam_df) else nam_df
            if n is None or getattr(n, "empty", True):
                st.caption("Chưa có dữ liệu gió Lào Yên Thành.")
            else:
                g = go.Figure(go.Bar(
                    x=n.nam.astype(str), y=n.so_ngay,
                    marker=dict(
                        color=["#0F172A" if y == nam else "#CBD5E1" for y in n.nam],
                        cornerradius=4,
                    ),
                    text=n.so_ngay, textposition="outside",
                ))
                g.update_layout(
                    height=250, margin=dict(l=6, r=6, t=20, b=6),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
                    xaxis=dict(showgrid=False),
                )
                ve(g, che_do="co_dinh")

        # Biểu đồ 3: Độ xanh sinh thái lúa (NDVI) & Cán cân nước ruộng lúa Yên Thành
        with c3, st.container(border=True):
            st.markdown(f'<p class="cap" style="font-size:13.5px; margin-bottom:4px;">🌿 Sinh khối Lúa (NDVI) & Cán cân ẩm ({nam})</p>', unsafe_allow_html=True)
            f3 = make_subplots(specs=[[{"secondary_y": True}]])
            if "ndvi" in chuoi.columns:
                f3.add_scatter(
                    x=[f"T{m}" for m in chuoi.month], y=chuoi.ndvi, name="NDVI lúa",
                    mode="lines+markers", line=dict(color="#16A34A", width=2.5),
                )
            if "nuoc_con_lai_mm" in chuoi.columns:
                f3.add_bar(
                    x=[f"T{m}" for m in chuoi.month], y=chuoi.nuoc_con_lai_mm, name="Cán cân ẩm (mm)",
                    marker=dict(
                        color=["#0EA5E9" if v >= 0 else "#EF4444" for v in chuoi.nuoc_con_lai_mm],
                        cornerradius=4,
                    ),
                    secondary_y=True,
                )
            f3.update_layout(
                height=250, margin=dict(l=6, r=6, t=20, b=6),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.15, x=0),
                xaxis=dict(showgrid=False),
            )
            ve(f3, che_do="co_dinh")
