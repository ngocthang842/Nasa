"""Trang Tổng quan: AgTech Command Center Vựa lúa Huyện Yên Thành (Nghệ An).

Kiến trúc 4 Tầng Chuẩn Quốc tế:
- Tầng 1: Master Timeline Mùa vụ (Gộp Header + Slider + Vòng đời sinh thái).
- Tầng 2: 5 Thẻ Hero KPI Khí hậu & Viễn thám (Đầy đủ 100% số liệu).
- Tầng 3: Trung tâm Tác nghiệp Cân đối (Bản đồ số hóa 4 cụm xã : Cockpit Nông vụ).
- Tầng 4: Analytics Lab (3 Biểu đồ đa năm đồng bộ, bo góc hiện đại).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import engine as E
from views.ban_do import hien_ban_do
from views.chung import kpi_the, kpi_the_dot, ve

# DANH SÁCH 3 ĐỢT CANH TÁC MẶC ĐỊNH CHUẨN NÔNG HỌC YÊN THÀNH
DEFAULT_DOTS = [
    {
        "id": "dot_1",
        "ten": "Đợt 1: Vụ Lúa Chiêm Xuân",
        "thangs": [1, 2, 3, 4, 5],
        "cay": "Lúa",
        "mau": "#16A34A",
        "ic": "🌾",
        "mota": "Vụ lúa chính số 1: Gieo mạ chống rét T1, trỗ rộ T4 né táp gió Lào, thu hoạch dứt điểm T5.",
    },
    {
        "id": "dot_2",
        "ten": "Đợt 2: Vụ Lúa Hè Thu",
        "thangs": [6, 7, 8, 9],
        "cay": "Lúa",
        "mau": "#D97706",
        "ic": "☀️",
        "mota": "Vụ lúa chạy lụt: Cấy cực nhanh trước 10/6, chống hạn đỉnh T7, gặt trước 15/9 né lũ Kênh Vách Bắc.",
    },
    {
        "id": "dot_3",
        "ten": "Đợt 3: Phơi Ải & Vụ Đông",
        "thangs": [10, 11, 12],
        "cay": "Ngô",
        "mau": "#0284C7",
        "ic": "🚜",
        "mota": "Cày sâu phơi nỏ ruộng diệt mầm đạo ôn, xen canh Ngô ngọt, Lạc thu đông, đón nước sông Lam T12.",
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
        ("🥬 Việc 3: Trồng cây vụ đông", "Gieo ngô ngọt, lạc thu đông, rau màu trên các chân đất vàn cao để tăng thu nhập.", "#F59E0B", "🟡"),
    ],
    11: [
        ("🌾 Việc 1: Tiếp tục phơi ải đất", "Giữ ruộng khô nỏ, tận dụng ánh nắng hanh heo tiêu diệt bào tử đạo ôn và ấu trùng rầy.", "#16A34A", "🟢"),
        ("💧 Việc 2: Nạo vét Kênh Ba Ra", "Phát động toàn dân ra quân nạo vét bùn đất Kênh chính và hệ thống cống nội đồng.", "#0284C7", "🔵"),
        ("🥬 Việc 3: Chăm sóc rau vụ đông", "Tưới nước đủ ẩm và bón phân hữu cơ sinh học cho diện tích rau màu vụ đông.", "#16A34A", "🟢"),
    ],
    12: [
        ("🌾 Việc 1: Chuẩn bị giống lúa xuân", "Chuẩn bị giống lúa thuần chất lượng cao: ST25, J02, TBR225, Bắc Thịnh, ngâm ủ đúng kỹ thuật.", "#0284C7", "🔵"),
        ("💧 Việc 2: Lấy nước đổ ải đầu vụ", "Mở cống Ba Ra Đô Lương lấy nước phù sa sông Lam vào đồng để bừa dập đất.", "#16A34A", "🟢"),
        ("🛡️ Việc 3: Làm mạ che phủ nilon", "Gieo mạ vụ xuân từ cuối tháng 12, che phủ nilon trắng 100% diện tích chống rét.", "#EF4444", "🔴"),
    ],
}


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
                {"range": [0, 35], "color": "#DCFCE7"},
                {"range": [35, 55], "color": "#FEF3C7"},
                {"range": [55, 100], "color": "#FEE2E2"},
            ],
            "threshold": {"line": {"color": "#0F172A", "width": 3}, "thickness": 0.8, "value": w},
        },
    ))
    fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


@st.dialog("✨ Trợ Lý Thiết Kế Đợt Canh Tác Tự Động (Viễn Thám NASA)", width="large")
def hop_thoai_tao_dot(nam, dl, vung):
    """Cửa sổ Pop-up Modal thông minh: Tự động tạo đợt từ tháng bất kỳ và thẩm định thời tiết nối tiếp."""
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius:12px; padding:12px 16px; margin-bottom:14px; border:1px solid #334155;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:10px;">
              <span style="font-size:22px;">🛰️</span>
              <div>
                <div style="font-size:15px; font-weight:800; color:#F8FAFC; letter-spacing:0.3px;">TRỢ LÝ TỰ ĐỘNG THIẾT KẾ ĐỢT & THẨM ĐỊNH THỜI TIẾT LIÊN TIẾP</div>
                <div style="font-size:11.5px; color:#2DD4BF;">Dữ liệu Vệ tinh NASA (MODIS, SMAP, GPM) · Thủy nông Ba Ra Đô Lương & Vựa lúa Yên Thành</div>
              </div>
            </div>
            <div style="font-size:11px; font-weight:700; color:#94A3B8; background:rgba(255,255,255,0.06); padding:4px 10px; border-radius:999px;">
              Niên vụ: {nam}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:4px;'>1️⃣ Chọn Tháng Bắt Đầu & Cây Trồng (Hệ thống tự tính chu kỳ tối ưu):</div>", unsafe_allow_html=True)
    c_m1, c_m2 = st.columns([6, 6], gap="small")
    with c_m1:
        thang_bd = st.selectbox(
            "Tháng bắt đầu đợt canh tác:",
            options=list(range(1, 13)),
            index=1,  # Tháng 2 mặc định theo yêu cầu của người dùng
            format_func=lambda m: f"Tháng {m} ({ICON_THANG.get(m, '')} {TEN_GIAI_DOAN.get(m, '')[:26]}...)",
            key="dialog_sel_thang_bd",
        )
    with c_m2:
        loai_cay = st.selectbox(
            "Cây trồng chủ lực:",
            options=["Lúa", "Lạc", "Ngô", "Rau màu"],
            index=0,
            key="dialog_sel_loai_cay",
        )

    # Tự động tính tháng kết thúc đề xuất dựa theo chu kỳ sinh học cây trồng tại Yên Thành
    duration_mac_dinh = 4 if loai_cay == "Lúa" else 3
    suggested_end = min(12, thang_bd + duration_mac_dinh)
    
    thang_kt = st.slider(
        f"Tháng kết thúc đợt (Đề xuất tự động: Tháng {thang_bd} → Tháng {suggested_end}):",
        min_value=thang_bd,
        max_value=12,
        value=suggested_end,
        format="Tháng %d",
        key="dialog_slider_thang_kt",
    )

    thangs_dot = list(range(thang_bd, thang_kt + 1))
    so_thang = len(thangs_dot)

    # Hiển thị dải băng tháng trực quan cho đợt này
    ribbon_modal = ""
    for m in range(1, 13):
        ic = ICON_THANG.get(m, "")
        if m in thangs_dot:
            bg = "#DCFCE7" if loai_cay == "Lúa" else "#FEF3C7"
            border = "border:2px solid #16A34A;" if loai_cay == "Lúa" else "border:2px solid #D97706;"
            c_text = "#16A34A" if loai_cay == "Lúa" else "#D97706"
            sub_txt = f"<b style='color:{c_text}; font-size:9px;'>ĐANG TẠO</b>"
        else:
            bg = "#F8FAFC"
            border = "border:1px dashed #CBD5E1;"
            c_text = "#94A3B8"
            sub_txt = "<span style='color:#94A3B8; font-size:9px;'>—</span>"
        ribbon_modal += f"""
        <div style="flex:1 1 0; background:{bg}; {border} border-radius:6px; padding:4px 2px; text-align:center; min-width:38px;">
          <div style="font-size:11px; font-weight:800; color:{c_text};">T{m}</div>
          <div style="font-size:13px;">{ic}</div>
          {sub_txt}
        </div>
        """

    st.markdown(
        f"""
        <div style="display:flex; gap:4px; overflow-x:auto; margin:4px 0 10px 0;">
          {ribbon_modal}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Thẩm định viễn thám NASA cho đợt đang tạo
    st.markdown("<div style='font-size:13.5px; font-weight:800; color:#0F172A; margin:8px 0 4px 0;'>2️⃣ Thẩm Định Khí Hậu & Viễn Thám NASA Cho Đợt Này:</div>", unsafe_allow_html=True)
    sub_dot = dl[(dl.year == nam) & (dl.huyen == vung) & (dl.month.isin(thangs_dot))]
    v_mua = float(sub_dot["mua_mm"].sum()) if not sub_dot.empty else 0.0
    v_tmax_tb = float(sub_dot["tmax"].mean()) if not sub_dot.empty else 30.0
    v_tmax_peak = float(sub_dot["tmax"].max()) if not sub_dot.empty else 35.0
    v_nong = int(sub_dot["nong35"].sum()) if not sub_dot.empty else 0
    v_sm = float(sub_dot["sm_rootzone"].mean() * 100) if not sub_dot.empty else 25.0

    cm1, cm2, cm3, cm4 = st.columns(4)
    with cm1:
        st.metric("🌡️ Tmax Trung Bình", f"{v_tmax_tb:.1f}°C", f"Đỉnh {v_tmax_peak:.1f}°C")
    with cm2:
        st.metric("🌧️ Tổng Mưa GPM", f"{v_mua:.0f} mm", f"{so_thang} tháng tích lũy")
    with cm3:
        st.metric("☀️ Gió Lào ≥35°C", f"{v_nong} ngày", "Nguy cơ táp hoa/hạn")
    with cm4:
        st.metric("💧 Ẩm Ruộng SMAP", f"{v_sm:.0f}%", "Độ ẩm tầng rễ")

    danh_gia_dot = []
    if thang_bd in [1, 2]:
        danh_gia_dot.append("🌱 <b>Đầu vụ (T1–T2):</b> Thời tiết ấm dần, độ ẩm đất tầng rễ 27–28% lý tưởng cho mạ bén rễ và đẻ nhánh rộ.")
    if 4 in thangs_dot or 5 in thangs_dot:
        danh_gia_dot.append(f"🔥 <b>Trỗ bông (T4–T5):</b> Xuất hiện {v_nong} ngày Gió Lào nắng nóng ≥35°C. Cần dâng nước mặt ruộng 3–5 cm làm mát ruộng.")
    if 5 in thangs_dot or 6 in thangs_dot:
        danh_gia_dot.append("🌾 <b>Thu hoạch (T5–T6):</b> Cần chủ động tháo kiệt nước khô ruộng trước 7–10 ngày để đưa máy gặt liên hợp vào đồng.")
    txt_dg_dot = "<br>".join(danh_gia_dot) if danh_gia_dot else "✅ Điều kiện khí tượng và viễn thám NASA ổn định, thuận lợi tổ chức sản xuất."

    st.markdown(
        f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:8px 12px; font-size:12px; color:#1E293B; margin-top:4px; line-height:1.5;">
          <b>🌾 Đánh Giá Nông Học Yên Thành:</b><br>{txt_dg_dot}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Đánh giá chuỗi tháng tiếp theo có ổn không để tạo đợt
    st.markdown("<div style='font-size:13.5px; font-weight:800; color:#0F172A; margin:12px 0 4px 0;'>3️⃣ Thẩm Định Các Tháng Tiếp Theo (Có Ổn Định Để Tạo Đợt Nối Tiếp Không?):</div>", unsafe_allow_html=True)
    thangs_tiep = list(range(thang_kt + 1, 13))
    
    if thangs_tiep:
        sub_tiep = dl[(dl.year == nam) & (dl.huyen == vung) & (dl.month.isin(thangs_tiep))]
        mua_tiep = float(sub_tiep["mua_mm"].sum()) if not sub_tiep.empty else 0.0
        nong_tiep = int(sub_tiep["nong35"].sum()) if not sub_tiep.empty else 0
        tmax_tiep_peak = float(sub_tiep["tmax"].max()) if not sub_tiep.empty else 35.0
        mua_bao = float(sub_tiep[sub_tiep.month.isin([9, 10])]["mua_mm"].sum()) if not sub_tiep.empty and any(m in [9, 10] for m in thangs_tiep) else 0.0
        
        # Đề xuất đợt 2 nối tiếp
        t_bd_2 = thang_kt + 1
        t_kt_2 = 9 if (t_bd_2 <= 9 and 9 in thangs_tiep) else min(12, t_bd_2 + 2)
        thangs_dot_2 = list(range(t_bd_2, t_kt_2 + 1))
        t_bd_3 = t_kt_2 + 1
        thangs_dot_3 = list(range(t_bd_3, 13)) if t_bd_3 <= 12 else []

        st.markdown(
            f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #F59E0B; border-radius:8px; padding:10px 14px; font-size:12px; color:#1E293B; line-height:1.5;">
              <div style="font-weight:750; font-size:13px; color:#92400E; margin-bottom:4px;">
                🛰️ Phân Tích Chuỗi Tháng Kế Tiếp (Tháng {min(thangs_tiep)} → Tháng {max(thangs_tiep)}):
              </div>
              <div>• <b>Tổng mưa dự báo:</b> <b>{mua_tiep:.0f} mm</b> · Đỉnh nhiệt: <b>{tmax_tiep_peak:.1f}°C</b> · Gió Lào: <b>{nong_tiep} ngày</b></div>
              <div style="margin-top:4px;">• <b>Tháng 7–8:</b> Đỉnh nhiệt gió Lào Tây Nam gay gắt, bốc thoát hơi nước lớn. Cần chủ động dẫn nước từ Ba Ra Đô Lương.</div>
              <div style="margin-top:4px;">• <b>Tháng 9–10 (⚠️ MÙA MƯA BÃO LỚN NHẤT NGHỆ AN):</b> Lượng mưa GPM đạt đỉnh <b>{mua_bao:.0f} mm</b>! Vùng trũng lòng chảo Kênh Vách Bắc đối mặt nguy cơ ngập úng nghiêm trọng.</div>
              <div style="margin-top:4px;">• <b>💡 KẾT LUẬN & ĐỀ XUẤT ĐỢT TIẾP THEO:</b>
                {"Bắt buộc phải gặt dứt điểm vụ lúa trước ngày 15–20/9 để né lũ! Đề xuất cơ cấu giống lúa cực ngắn ngày (<90 ngày) cho Đợt 2 (Tháng " + str(t_bd_2) + " → Tháng " + str(t_kt_2) + ")." if any(m in [9, 10] for m in thangs_tiep) else "Điều kiện khí hậu ổn định, thuận lợi tổ chức canh tác liên tục."}
              </div>
            </div>
            <div style="display:flex; gap:8px; align-items:center; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:8px 12px; font-size:12px; margin-top:8px;">
              <div style="flex:1;">
                <b>🌾 Đợt 1 (Đang tạo):</b> Tháng {thang_bd} → Tháng {thang_kt} ({loai_cay})
              </div>
              <div style="color:#64748B;">➔</div>
              <div style="flex:1;">
                <b>☀️ Đợt 2 (Gợi ý nối tiếp):</b> Tháng {t_bd_2} → Tháng {t_kt_2} (Lúa Hè Thu né lụt)
              </div>
              {f'<div style="color:#64748B;">➔</div><div style="flex:1;"><b>🚜 Đợt 3:</b> Tháng {t_bd_3} → Tháng 12 (Phơi ải / Vụ Đông)</div>' if thangs_dot_3 else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(f"Đợt này đã kéo dài trọn vẹn đến hết tháng 12 của năm {nam}.")

    # 4. Nút bấm hành động
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns([1, 1], gap="small")
    
    with c_btn1:
        ten_dot_1 = f"Đợt {len(st.session_state['danh_sach_dot'])+1}: Vụ {loai_cay} (T{thang_bd}–T{thang_kt})"
        if st.button(f"✅ Lưu & Kích Hoạt Đợt Này (T{thang_bd} → T{thang_kt})", type="primary", use_container_width=True, key="dialog_btn_save_single"):
            new_dot = {
                "id": f"dot_{len(st.session_state['danh_sach_dot'])+1}_{np.random.randint(100, 999)}",
                "ten": ten_dot_1,
                "thangs": thangs_dot,
                "cay": loai_cay,
                "mau": "#16A34A" if loai_cay == "Lúa" else ("#D97706" if loai_cay == "Lạc" else "#0284C7"),
                "ic": "🌾" if loai_cay == "Lúa" else ("🥜" if loai_cay == "Lạc" else ("🌽" if loai_cay == "Ngô" else "🥬")),
                "mota": f"Đợt canh tác tự động từ Tháng {thang_bd} đến Tháng {thang_kt}. Tối ưu theo viễn thám NASA.",
            }
            st.session_state["danh_sach_dot"].append(new_dot)
            st.session_state[f"pills_dot_canh_tac_{nam}"] = f"{new_dot['ic']} {new_dot['ten']} (T{min(new_dot['thangs'])}–T{max(new_dot['thangs'])})"
            st.toast(f"✅ Đã tạo và kích hoạt '{new_dot['ten']}'!", icon="🌾")
            st.rerun()

    with c_btn2:
        if thangs_tiep:
            if st.button("✨ Tự Động Tạo Cả Chuỗi Đợt Cả Năm", type="secondary", use_container_width=True, key="dialog_btn_save_chain"):
                dot1 = {
                    "id": f"dot_c1_{np.random.randint(100, 999)}",
                    "ten": f"Đợt 1: Vụ {loai_cay} (T{thang_bd}–T{thang_kt})",
                    "thangs": thangs_dot,
                    "cay": loai_cay,
                    "mau": "#16A34A",
                    "ic": "🌾",
                    "mota": f"Vụ lúa chính: Gieo cấy T{thang_bd}, trỗ rộ và thu hoạch dứt điểm T{thang_kt}.",
                }
                dot2 = {
                    "id": f"dot_c2_{np.random.randint(100, 999)}",
                    "ten": f"Đợt 2: Vụ Lúa Hè Thu (T{t_bd_2}–T{t_kt_2})",
                    "thangs": thangs_dot_2,
                    "cay": "Lúa",
                    "mau": "#D97706",
                    "ic": "☀️",
                    "mota": f"Vụ lúa chạy lụt: Gieo cấy nhanh T{t_bd_2}, gặt trước 15/9 né lũ bão Kênh Vách Bắc.",
                }
                new_list = [dot1, dot2]
                if thangs_dot_3:
                    dot3 = {
                        "id": f"dot_c3_{np.random.randint(100, 999)}",
                        "ten": f"Đợt 3: Phơi Ải & Vụ Đông (T{t_bd_3}–T12)",
                        "thangs": thangs_dot_3,
                        "cay": "Ngô",
                        "mau": "#0284C7",
                        "ic": "🚜",
                        "mota": f"Cày phơi nỏ ruộng diệt mầm đạo ôn, xen canh ngô đông, đón nước sông Lam T12.",
                    }
                    new_list.append(dot3)
                
                st.session_state["danh_sach_dot"] = new_list
                st.session_state[f"pills_dot_canh_tac_{nam}"] = f"{dot1['ic']} {dot1['ten']} (T{min(dot1['thangs'])}–T{max(dot1['thangs'])})"
                st.toast("✨ Đã tạo chuỗi đợt canh tác cả năm chuẩn viễn thám NASA!", icon="🚀")
                st.rerun()

    # 5. Danh sách đợt hiện có & Khôi phục mặc định
    with st.expander(f"📋 Quản lý danh sách các đợt hiện có ({len(st.session_state['danh_sach_dot'])} đợt)", expanded=False):
        for idx, d in enumerate(st.session_state["danh_sach_dot"]):
            c_d1, c_d2 = st.columns([8.5, 1.5])
            with c_d1:
                st.markdown(f"• **{d['ic']} {d['ten']}**: Tháng {min(d['thangs'])} → Tháng {max(d['thangs'])} ({d['cay']}) — *{d['mota']}*")
            with c_d2:
                if len(st.session_state["danh_sach_dot"]) > 1:
                    if st.button("🗑️", key=f"del_dot_in_dialog_{idx}", help=f"Xóa {d['ten']}"):
                        st.session_state["danh_sach_dot"].pop(idx)
                        st.rerun()
        if st.button("⟲ Khôi phục 3 đợt chuẩn mùa vụ Yên Thành", key="dialog_reset_defaults", use_container_width=True):
            st.session_state["danh_sach_dot"] = list(DEFAULT_DOTS)
            st.rerun()


def hien(ctx):
    dl, diem, nam_df = ctx["dl"], ctx["diem"], ctx["nam_df"]
    nam, years = ctx["nam"], ctx["years"]
    vung = "Yên Thành"

    # LỌC DUY NHẤT DỮ LIỆU HUYỆN YÊN THÀNH
    chuoi = dl[(dl.year == nam) & (dl.huyen == vung)].sort_values("month")
    co_thang = sorted(chuoi.month.unique()) if not chuoi.empty else list(range(1, 13))

    # Khởi tạo danh sách các đợt canh tác trong session_state nếu chưa có
    if "danh_sach_dot" not in st.session_state:
        st.session_state["danh_sach_dot"] = list(DEFAULT_DOTS)

    danh_sach_dot = st.session_state["danh_sach_dot"]

    # =========================================================================
    # TẦNG 1: BỘ ĐIỀU HƯỚNG MÙA VỤ DUAL-MODE (ĐỢT CANH TÁC & CHI TIẾT TỪNG THÁNG)
    # =========================================================================
    with st.container(border=True):
        col_hdr_left, col_hdr_right = st.columns([6.8, 3.2], gap="small")
        with col_hdr_left:
            st.markdown(
                f"""
                <div style="padding:2px 0;">
                  <div style="font-size:11px; font-weight:750; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">🛰️ VIỄN THÁM NÔNG NGHIỆP NASA · VỰA LÚA XỨ NGHỆ</div>
                  <div style="font-size:21px; font-weight:800; color:#0F172A; letter-spacing:-0.4px; line-height:1.2; margin-top:2px;">🌾 Huyện Yên Thành · Vụ Lúa & Chu Kỳ Canh Tác {nam}</div>
                  <div style="font-size:12px; color:#475569; margin-top:2px;">Hệ thống thủy nông Ba Ra Đô Lương & Giám sát Viễn thám MODIS, SMAP, GPM</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_hdr_right:
            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
            che_do_xem = st.segmented_control(
                "Chế độ khảo sát:",
                options=["🌾 Theo Đợt Canh Tác", "📅 Theo Từng Tháng"],
                default="🌾 Theo Đợt Canh Tác",
                key=f"seg_che_do_khao_sat_{nam}",
                label_visibility="collapsed",
            ) if hasattr(st, "segmented_control") else st.radio("Chế độ khảo sát:", ["🌾 Theo Đợt Canh Tác", "📅 Theo Từng Tháng"], horizontal=True, key=f"rad_che_do_{nam}", label_visibility="collapsed")

        st.markdown("<hr style='margin:8px 0 12px 0; border-color:#F1F5F9;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # NHÁNH 1: XEM THEO ĐỢT CANH TÁC (CROP SEASON BATCHES)
        # ---------------------------------------------------------------------
        if che_do_xem == "🌾 Theo Đợt Canh Tác":
            options_dot = [f"{d['ic']} {d['ten']} (T{min(d['thangs'])}–T{max(d['thangs'])})" for d in danh_sach_dot]
            
            c_pills_dot, c_btn_dialog = st.columns([7.2, 2.8], gap="small")
            with c_pills_dot:
                dot_label_chon = st.pills(
                    "Chọn đợt canh tác:",
                    options=options_dot,
                    default=options_dot[0] if options_dot else None,
                    key=f"pills_dot_canh_tac_{nam}",
                    label_visibility="collapsed",
                )
                if not dot_label_chon and options_dot:
                    dot_label_chon = options_dot[0]

            with c_btn_dialog:
                if st.button("✨ Tự Tạo & Phân Tích Đợt", key="btn_open_dialog_tao_dot", type="primary", use_container_width=True, help="Nhấp để mở pop-up thiết kế đợt tự động từ tháng bất kỳ và thẩm định thời tiết nối tiếp"):
                    hop_thoai_tao_dot(nam, dl, vung)

            # Lấy thông tin đợt đang chọn
            idx_dot = options_dot.index(dot_label_chon) if dot_label_chon in options_dot else 0
            cur_dot = danh_sach_dot[idx_dot]
            thangs_dot = cur_dot["thangs"]

            # RENDER DÒNG THỜI GIAN 12 THÁNG TRỰC QUAN (HIGHLIGHT CÁC THÁNG TRONG ĐỢT)
            ribbon_boxes = ""
            for m in range(1, 13):
                ic = ICON_THANG.get(m, "")
                if m in thangs_dot:
                    # Tháng nằm trong đợt -> Nổi bật màu sắc
                    bg_m = "#EFF6FF" if cur_dot["mau"] == "#0284C7" else ("#FEF3C7" if cur_dot["mau"] == "#D97706" else "#DCFCE7")
                    border_m = f"border:2px solid {cur_dot['mau']};"
                    color_m = cur_dot["mau"]
                    badge_m = f'<div style="font-size:9px; font-weight:800; color:{cur_dot["mau"]};">ĐANG XEM</div>'
                else:
                    # Tháng ngoài đợt -> Chìm nhẹ
                    bg_m = "#F8FAFC"
                    border_m = "border:1px dashed #CBD5E1;"
                    color_m = "#94A3B8"
                    badge_m = '<div style="font-size:9px; color:#94A3B8;">—</div>'

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
                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid {cur_dot['mau']}; border-radius:8px; padding:7px 12px; font-size:12px; color:#1E293B; margin-top:2px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                  <div>
                    <b>📌 {cur_dot['ten']}:</b> Gồm <b>{len(thangs_dot)} tháng</b> (Tháng {min(thangs_dot)} → Tháng {max(thangs_dot)}) · Cây trồng chủ lực: <b style="color:{cur_dot['mau']};">{cur_dot['cay']}</b> — <i>{cur_dot['mota']}</i>
                  </div>
                  <div style="font-size:11px; font-weight:750; color:{cur_dot['mau']}; background:#FFFFFF; border:1px solid {cur_dot['mau']}; border-radius:999px; padding:2px 10px;">
                    {cur_dot['ic']} {cur_dot['cay']} Yên Thành
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # THIẾT LẬP THÁNG ĐẠI DIỆN ĐỂ BẢN ĐỒ VÀ COCKPIT HOẠT ĐỘNG
            thang = 4 if 4 in thangs_dot else (8 if 8 in thangs_dot else thangs_dot[len(thangs_dot)//2])

            # -----------------------------------------------------------------
            # BỘ CÔNG CỤ TÙY BIẾN THỦ CÔNG & MẪU MÙA VỤ
            # -----------------------------------------------------------------
            with st.expander("⚙️ Tùy biến thủ công & Mẫu mùa vụ nhanh", expanded=False):
                st.markdown(
                    '<div style="font-size:14px; font-weight:800; color:#0F172A; margin-bottom:4px;">'
                    '🛠️ Quản Lý & Tự Tạo Đợt Canh Tác Mới (Thêm / Xóa / Tự Chọn Tháng Vào Đợt)'
                    '</div>'
                    '<div style="font-size:12px; color:#64748B; margin-bottom:12px;">'
                    'Tự do chia đợt canh tác và gom nhóm các tháng theo tập quán chân ruộng (ruộng trũng lòng chảo vs ruộng vàn cao Yên Thành).'
                    '</div>',
                    unsafe_allow_html=True,
                )

                col_b1, col_b2, col_b3 = st.columns([4, 3, 5], gap="small")
                with col_b1:
                    ten_moi = st.text_input("Tên đợt vụ mới:", value=f"Đợt {len(danh_sach_dot)+1}: Vụ Mới", key="inp_ten_dot_moi")
                with col_b2:
                    cay_moi = st.selectbox("Cây trồng chủ lực:", ["Lúa", "Lạc", "Ngô", "Rau màu"], index=0, key="sel_cay_dot_moi")
                with col_b3:
                    thangs_moi = st.multiselect(
                        "Chọn các tháng đưa vào đợt này:",
                        options=list(range(1, 13)),
                        default=[5, 6, 7],
                        format_func=lambda m: f"Tháng {m}",
                        key="mul_thangs_dot_moi",
                    )
                
                col_desc, col_btn_add = st.columns([8, 2], gap="small")
                with col_desc:
                    mota_moi = st.text_input("Ghi chú mục tiêu canh tác:", value="Tự chọn chuỗi tháng canh tác tối ưu theo điều kiện thời tiết.", key="inp_mota_dot_moi")
                with col_btn_add:
                    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                    if st.button("➕ Thêm Đợt", key="btn_add_dot_moi", type="primary", use_container_width=True):
                        if not thangs_moi:
                            st.error("Vui lòng chọn ít nhất 1 tháng cho đợt mới!")
                        else:
                            new_dot = {
                                "id": f"dot_{len(danh_sach_dot)+1}_{np.random.randint(100, 999)}",
                                "ten": ten_moi.strip() or f"Đợt {len(danh_sach_dot)+1}",
                                "thangs": sorted(thangs_moi),
                                "cay": cay_moi,
                                "mau": "#16A34A" if cay_moi == "Lúa" else ("#D97706" if cay_moi == "Lạc" else "#0284C7"),
                                "ic": "🌾" if cay_moi == "Lúa" else ("🥜" if cay_moi == "Lạc" else ("🌽" if cay_moi == "Ngô" else "🥬")),
                                "mota": mota_moi.strip(),
                            }
                            st.session_state["danh_sach_dot"].append(new_dot)
                            st.toast(f"✅ Đã thêm '{new_dot['ten']}' vào danh sách đợt!", icon="🌾")
                            st.rerun()

                # CÁC NÚT CÀI ĐẶT MẪU NHANH
                st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
                cp1, cp2, cp3, cp4 = st.columns([3, 3, 3, 3])
                with cp1:
                    if st.button("🌾 2 Vụ Lúa Truyền Thống", key="btn_preset_2vu", use_container_width=True):
                        st.session_state["danh_sach_dot"] = [
                            {"id": "dot_1", "ten": "Đợt 1: Vụ Chiêm Xuân", "thangs": [1, 2, 3, 4, 5], "cay": "Lúa", "mau": "#16A34A", "ic": "🌾", "mota": "Gieo mạ chống rét T1, trỗ rộ T4 né táp gió Lào, gặt dứt điểm T5."},
                            {"id": "dot_2", "ten": "Đợt 2: Vụ Hè Thu", "thangs": [6, 7, 8, 9], "cay": "Lúa", "mau": "#D97706", "ic": "☀️", "mota": "Cấy nhanh né lũ, chống hạn T7, gặt trước 15/9 né ngập lụt Kênh Vách Bắc."},
                            {"id": "dot_3", "ten": "Đợt 3: Phơi Ải / Cải Tạo Đất", "thangs": [10, 11, 12], "cay": "Ngô", "mau": "#0284C7", "ic": "🚜", "mota": "Cày phơi nỏ ruộng diệt mầm đạo ôn, xen canh Ngô ngọt, Lạc thu đông."},
                        ]
                        st.rerun()
                with cp2:
                    if st.button("🔄 3 Đợt Luân Canh Lúa - Màu", key="btn_preset_3vu", use_container_width=True):
                        st.session_state["danh_sach_dot"] = [
                            {"id": "dot_1", "ten": "Đợt 1: Lúa Xuân Sớm", "thangs": [1, 2, 3, 4], "cay": "Lúa", "mau": "#16A34A", "ic": "🌾", "mota": "Cấy giống thuần cực ngắn ngày, thu hoạch cuối tháng 4."},
                            {"id": "dot_2", "ten": "Đợt 2: Lúa Hè Thu Sớm", "thangs": [5, 6, 7, 8], "cay": "Lúa", "mau": "#D97706", "ic": "☀️", "mota": "Gặt trước 30/8 né hoàn toàn bão lũ tháng 9."},
                            {"id": "dot_3", "ten": "Đợt 3: Cây Màu Vụ Đông", "thangs": [9, 10, 11, 12], "cay": "Ngô", "mau": "#7C3AED", "ic": "🌽", "mota": "Trồng Ngô ngọt, Lạc thu đông, rau màu tăng thu nhập."},
                        ]
                        st.rerun()
                with cp3:
                    if len(danh_sach_dot) > 1:
                        if st.button(f"🗑️ Xóa đợt cuối ({danh_sach_dot[-1]['ten'][:12]}...)", key="btn_del_last_dot", use_container_width=True):
                            st.session_state["danh_sach_dot"].pop()
                            st.rerun()
                with cp4:
                    if st.button("⟲ Khôi phục mặc định", key="btn_reset_default_dot", use_container_width=True):
                        st.session_state["danh_sach_dot"] = list(DEFAULT_DOTS)
                        st.rerun()

        # ---------------------------------------------------------------------
        # NHÁNH 2: XEM CHI TIẾT TỪNG THÁNG (T1 ĐẾN T12)
        # ---------------------------------------------------------------------
        else:
            thang_khoi_tao = ctx.get("thang", 4)
            if thang_khoi_tao not in co_thang:
                thang_khoi_tao = 4 if 4 in co_thang else co_thang[0]

            st.markdown(
                '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                '  <span style="font-size:12px; font-weight:750; color:#0F172A;">📅 Chu kỳ 12 Tháng Sinh trưởng của Lúa (Nhấp chọn tháng):</span>'
                '  <span style="font-size:11px; font-weight:700; color:#16A34A; background:#DCFCE7; border-radius:999px; padding:1px 8px;">Soi chi tiết</span>'
                '</div>',
                unsafe_allow_html=True,
            )
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
                f'📌 Đang chọn <b>Tháng {thang}</b> · <b>{vu_ten}</b> — Giai đoạn: <b style="color:#0F172A;">{gd_ten}</b>'
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
    # TẦNG 2: 5 THẺ HERO KPI KHÍ HẬU & VIỄN THÁM (TÍNH THEO ĐỢT HOẶC THEO THÁNG)
    # =========================================================================
    c = st.columns(5)
    
    if che_do_xem == "🌾 Theo Đợt Canh Tác":
        # TÍNH TOÁN TỔNG HỢP VIỄN THÁM CHO TOÀN BỘ CÁC THÁNG TRONG ĐỢT
        sub_dot = chuoi[chuoi.month.isin(thangs_dot)]
        sub_dot_25 = dl[(dl.year == 2025) & (dl.huyen == vung) & (dl.month.isin(thangs_dot))]
        
        # 1. Nhiệt độ TB & Đỉnh cực trị
        v_tmax = float(sub_dot["tmax"].mean()) if not sub_dot.empty else 30.0
        v_tmax_peak = float(sub_dot["tmax"].max()) if not sub_dot.empty else 35.0
        v_tmax_25 = float(sub_dot_25["tmax"].mean()) if not sub_dot_25.empty else v_tmax
        d_tmax = v_tmax - v_tmax_25
        
        # 2. Lượng mưa tích lũy cả đợt
        v_mua = float(sub_dot["mua_mm"].sum()) if not sub_dot.empty else 0.0
        v_mua_25 = float(sub_dot_25["mua_mm"].sum()) if not sub_dot_25.empty else v_mua
        d_mua = v_mua - v_mua_25
        
        # 3. Nắng nóng Gió Lào cả đợt
        v_nong = int(sub_dot["nong35"].sum()) if not sub_dot.empty else 0
        v_nong_25 = int(sub_dot_25["nong35"].sum()) if not sub_dot_25.empty else v_nong
        d_nong = v_nong - v_nong_25
        
        # 4. Độ ẩm đất SMAP TB cả đợt
        v_sm = float(sub_dot["sm_rootzone"].mean() * 100) if not sub_dot.empty else 28.0
        v_sm_25 = float(sub_dot_25["sm_rootzone"].mean() * 100) if not sub_dot_25.empty else v_sm
        d_sm = v_sm - v_sm_25
        
        # 5. Sinh khối NDVI đỉnh đợt
        v_ndvi = float(sub_dot["ndvi"].max()) if not sub_dot.empty else 0.65
        v_ndvi_25 = float(sub_dot_25["ndvi"].max()) if not sub_dot_25.empty else v_ndvi
        d_ndvi = v_ndvi - v_ndvi_25

        th = [
            kpi_the_dot(f"Tmax TB ({len(thangs_dot)}T)", v_tmax, "°C", "#F97316", f"Đỉnh {v_tmax_peak:.1f}°C", d_tmax, "cao", "{:.1f}"),
            kpi_the_dot(f"Tổng Mưa Cả Đợt", v_mua, "mm", "#0EA5E9", f"Tích lũy {len(thangs_dot)}T", d_mua, "cao", "{:.0f}"),
            kpi_the_dot(f"Gió Lào Cả Đợt", v_nong, "ngày", "#EF4444", f"≥35°C ({len(thangs_dot)}T)", d_nong, "cao", "{:.0f}"),
            kpi_the_dot(f"Ẩm Ruộng TB (SMAP)", v_sm, "%", "#10B981", f"Tầng rễ {len(thangs_dot)}T", d_sm, "thap", "{:.0f}"),
            kpi_the_dot(f"NDVI Đỉnh Mùa Vụ", v_ndvi, "", "#84CC16", f"Sinh khối cực đại", d_ndvi, "thap", "{:.2f}"),
        ]
    else:
        # TÍNH TOÁN THEO TỪNG THÁNG ĐƠN LẺ
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
    # TẦNG 3: TRUNG TÂM TÁC NGHIỆP CÂN ĐỐI (BẢN ĐỒ SỐ HÓA : COCKPIT NÔNG HỌC)
    # Tỷ lệ 6.8 : 3.2 tạo bố cục 3 cột hoàn hảo (Bản đồ | Map Sidebar | Cockpit)
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
    # TẦNG 4: ANALYTICS LAB (3 BIỂU ĐỒ ĐA NĂM ĐỒNG BỘ CHIỀU CAO, BO GÓC ĐẸP)
    # TỐI ƯU HÓA UX PROGRESSIVE DISCLOSURE: ĐÓNG GÓI TRONG EXPANDER
    # GIÚP TRANG TỔNG QUAN TINH GỌN, TRÁNH QUÁ TẢI THÔNG TIN, VỪA KHÍT 1 MÀN HÌNH
    # =========================================================================
    st.write("")
    with st.expander("📊 Mở rộng: Phân tích Xu hướng Khí tượng & Lịch sử 10 năm Gió Lào Yên Thành (3 Biểu đồ Chuyên sâu)", expanded=False):
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
            ve(f, che_do="tuong_tac")

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
            ve(f3, che_do="tuong_tac")
