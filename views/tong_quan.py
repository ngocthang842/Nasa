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
from views.chung import kpi_the, ve

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


def hien(ctx):
    dl, diem, nam_df = ctx["dl"], ctx["diem"], ctx["nam_df"]
    nam, years = ctx["nam"], ctx["years"]
    vung = "Yên Thành"

    # LỌC DUY NHẤT DỮ LIỆU HUYỆN YÊN THÀNH
    chuoi = dl[(dl.year == nam) & (dl.huyen == vung)].sort_values("month")
    co_thang = sorted(chuoi.month.unique()) if not chuoi.empty else list(range(1, 13))

    thang_khoi_tao = ctx.get("thang", 4)
    if thang_khoi_tao not in co_thang:
        thang_khoi_tao = 4 if 4 in co_thang else co_thang[0]

    # =========================================================================
    # TẦNG 1: MASTER COMMAND HEADER & TIMELINE MÙA VỤ 12 THÁNG (GỘP GỌN GÀNG)
    # =========================================================================
    with st.container(border=True):
        c_ttl, c_pills = st.columns([4, 6], gap="medium")
        with c_ttl:
            st.markdown(
                f'<div style="padding:2px 0;">'
                f'<div style="font-size:10.5px; font-weight:750; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">🛰️ VIỄN THÁM NÔNG NGHIỆP NASA · VỰA LÚA XỨ NGHỆ</div>'
                f'<div style="font-size:22px; font-weight:800; color:#0F172A; letter-spacing:-0.4px; line-height:1.2; margin-top:2px;">🌾 Huyện Yên Thành · Vụ Lúa {nam}</div>'
                f'<div style="font-size:12px; color:#475569; margin-top:3px;">Hệ thống thủy nông Ba Ra Đô Lương & Giám sát Viễn thám MODIS, SMAP, GPM</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c_pills:
            st.markdown(
                '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                '  <span style="font-size:11.5px; font-weight:700; color:#0F172A;">📅 Chu kỳ 12 Tháng Sinh trưởng của Lúa:</span>'
                '  <span style="font-size:10.5px; font-weight:700; color:#16A34A; background:#DCFCE7; border-radius:999px; padding:1px 8px;">Nhấp chọn tháng</span>'
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
    # TẦNG 2: 5 THẺ HERO KPI KHÍ HẬU & VIỄN THÁM (ĐẦY ĐỦ 100% SỐ LIỆU)
    # =========================================================================
    c = st.columns(5)
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
