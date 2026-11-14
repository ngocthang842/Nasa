"""Trang Kế hoạch Mùa vụ & Luân canh Đa canh — Vựa lúa Huyện Yên Thành (Nghệ An).

Kiến trúc Đồ họa Hóa AgTech (Visual & Card-Based Design):
- Khối 1: Header & 3 Thẻ Trạng thái Mùa vụ Đồ họa (Loại bỏ hoàn toàn đoạn văn chữ).
- Khối 2: 3 Card Mô hình Mùa vụ Tương tác (2 vụ lúa thuần, 3 đợt luân canh lúa-màu, tùy chỉnh chân ruộng).
- Khối 3: Timeline Gantt 12 Tháng tích hợp Dải Cảnh báo Thiên tai NASA (Gió Lào táp phấn & Lũ tiểu mãn).
- Khối 4: Thẻ Đồ họa Tác nghiệp Từng Đợt (Thanh đo an toàn khí hậu, chọn nhanh giống cây trồng, phân bổ tỷ lệ %).
- Khối 5: Bảng điểm Nông học Cả năm & Biểu đồ Gantt Lịch Canh tác Đa màu sắc.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine as E
from views.chung import tieu_de, ve


def _khoa_session(vung, nam, ma):
    return f"luan_canh_{E.khoa(vung)}_{nam}_{ma}"


def hien(ctx):
    dl, tb_df = ctx["dl"], ctx["tb_df"]
    nam, thang, years = ctx["nam"], ctx.get("thang", 4), ctx["years"]
    vung = "Yên Thành"

    # 1. HEADER & 3 THẺ TỔNG QUAN MÙA VỤ ĐỒ HỌA (LOẠI BỎ TƯỜNG CHỮ)
    tieu_de(vung, thang, nam, "Kế hoạch Mùa vụ & Luân canh Đa canh", len(years) < 2)

    ls_df = E.lay_du_lieu_lich_su(dl, vung, nam)
    nam_ls = sorted(ls_df.year.unique())
    so_nam_ls = len(nam_ls)

    # 3 Thẻ Infographic tóm tắt chu kỳ 3 vụ lúa trong năm tại Yên Thành
    st.markdown(
        """
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin:2px 0 14px 0;">
          <div style="flex:1; min-width:240px; background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:8px 12px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size:12px; font-weight:800; color:#16A34A; display:flex; align-items:center; gap:5px;">
              <span>🌾</span> VỤ LÚA CHIÊM XUÂN (T1 – T5)
            </div>
            <div style="font-size:11.5px; color:#334155; margin-top:3px; line-height:1.35;">
              Vụ chính số 1 Yên Thành · Né rét mạ T1 · Năng suất đỉnh cao 70–75 tạ/ha
            </div>
          </div>
          <div style="flex:1; min-width:240px; background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #D97706; border-radius:8px; padding:8px 12px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size:12px; font-weight:800; color:#D97706; display:flex; align-items:center; gap:5px;">
              <span>☀️</span> VỤ LÚA HÈ THU (T6 – T9)
            </div>
            <div style="font-size:11.5px; color:#334155; margin-top:3px; line-height:1.35;">
              Chạy đua né Gió Lào Tây Nam · Gặt chạy lũ tiểu mãn trước ngày 15/9
            </div>
          </div>
          <div style="flex:1; min-width:240px; background:#F0F9FF; border:1px solid #BAE6FD; border-left:4px solid #0284C7; border-radius:8px; padding:8px 12px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size:12px; font-weight:800; color:#0284C7; display:flex; align-items:center; gap:5px;">
              <span>🍂</span> CÀY ẢI / VỤ ĐÔNG (T10 – T12)
            </div>
            <div style="font-size:11.5px; color:#334155; margin-top:3px; line-height:1.35;">
              Phơi khô nỏ đất diệt mầm nấm bệnh · Xen canh Ngô ngọt, Lạc thu đông
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # 2. KHỐI THIẾT KẾ MÔ HÌNH VỤ MÙA TRỰC QUAN & DẢI TIMELINE GANTT 12 THÁNG
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
            '  <div>'
            '    <div style="font-size:16px; font-weight:800; color:#0F172A;">🛠️ Chọn Mô hình Canh tác Vựa lúa Yên Thành</div>'
            '    <div style="font-size:11.5px; color:#64748B;">Lựa chọn cơ cấu vụ lúa theo điều kiện chân ruộng hoặc để AI tự động phân bổ theo khí hậu NASA</div>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:13px; font-weight:800; color:#0F172A; margin:4px 0 2px 0;">'
            '🎯 Mục tiêu Ưu tiên của Nông dân (Farmer Priorities):'
            '</div>'
            '<div style="font-size:11.5px; color:#64748B; margin-bottom:8px;">'
            'Chọn mục tiêu ưu tiên để hệ thống AI tự động đề xuất phương án luân canh và cơ cấu cây trồng phù hợp nhất'
            '</div>',
            unsafe_allow_html=True,
        )

        c_prio, c_btn_prio = st.columns([7.2, 2.8], gap="small")
        with c_prio:
            uu_tien_nong_dan = st.segmented_control(
                "Ưu tiên của nông dân:",
                options=[
                    "🧪 Cải tạo đất & Bồi dưỡng độ phì",
                    "💧 Tiết kiệm nước & Chống hạn",
                    "💰 Năng suất & Thu nhập cao",
                    "🛡️ An toàn & Né thiên tai",
                ],
                default="🧪 Cải tạo đất & Bồi dưỡng độ phì",
                key=f"seg_farmer_priority_{E.khoa(vung)}_{nam}",
                label_visibility="collapsed",
            ) if hasattr(st, "segmented_control") else st.selectbox(
                "Ưu tiên của nông dân:",
                [
                    "🧪 Cải tạo đất & Bồi dưỡng độ phì",
                    "💧 Tiết kiệm nước & Chống hạn",
                    "💰 Năng suất & Thu nhập cao",
                    "🛡️ An toàn & Né thiên tai",
                ],
                index=0,
                key=f"sel_farmer_priority_{E.khoa(vung)}_{nam}",
            )
            if not uu_tien_nong_dan:
                uu_tien_nong_dan = "🧪 Cải tạo đất & Bồi dưỡng độ phì"

        with c_btn_prio:
            btn_auto = st.button(
                "✨ Gợi ý theo Ưu tiên (NASA AI)",
                help="Hệ thống tự động phân tích dữ liệu viễn thám NASA và thổ nhưỡng Yên Thành để tối ưu hóa mùa vụ theo đúng ưu tiên bạn đã chọn",
                type="primary",
                use_container_width=True,
            )

        st.markdown("<hr style='border-color:#F1F5F9; margin:8px 0 10px 0;'>", unsafe_allow_html=True)

        col_che_do = st.container()
        with col_che_do:
            st.markdown(
                '<div style="font-size:12.5px; font-weight:750; color:#334155; margin-bottom:4px;">'
                '🌾 Chọn khung mùa vụ thực tế:'
                '</div>',
                unsafe_allow_html=True,
            )
            che_do_dot = st.pills(
                "Chọn mô hình mùa vụ:",
                [
                    "🌾 2 Vụ Lúa thuần (Xuân T1–T5 & Hè Thu T6–T9)",
                    "🌟 3 Đợt Luân canh Lúa – Cây Đông (Xuân T1–T4, Hè Thu T5–T8, Đông T9–T12)",
                    "⚙️ Tự do tùy chỉnh chân ruộng",
                ],
                default="🌾 2 Vụ Lúa thuần (Xuân T1–T5 & Hè Thu T6–T9)",
                key=f"che_do_chia_dot_pills_{E.khoa(vung)}_{nam}",
                label_visibility="collapsed",
            )
            if not che_do_dot:
                che_do_dot = "🌾 2 Vụ Lúa thuần (Xuân T1–T5 & Hè Thu T6–T9)"

        # Xử lý cấu trúc các đợt canh tác
        if "2 Vụ Lúa" in che_do_dot:
            cac_dot = [
                {
                    "ten": "Đợt 1: Vụ Lúa Xuân (Tháng 1 – Tháng 5)",
                    "ma": "xuan",
                    "so_thang": 5,
                    "thang_bat_dau": 1,
                    "thang_ket_thuc": 5,
                    "icon": "🌾",
                    "mau": "#16A34A",
                    "dac_trung": "Vụ lúa chính số 1: năng suất đỉnh cao 70–75 tạ/ha, nguồn nước Ba Ra ổn định.",
                },
                {
                    "ten": "Đợt 2: Vụ Lúa Hè Thu (Tháng 6 – Tháng 9)",
                    "ma": "hethu",
                    "so_thang": 4,
                    "thang_bat_dau": 6,
                    "thang_ket_thuc": 9,
                    "icon": "☀️",
                    "mau": "#F59E0B",
                    "dac_trung": "Vụ hè thu né thiên tai: Gieo cấy cực nhanh, trỗ trước gió Lào, gặt trước 15/9 né lụt.",
                },
                {
                    "ten": "Đợt 3: Để ải đất / Phơi ruộng (Tháng 10 – Tháng 12)",
                    "ma": "dong_ai",
                    "so_thang": 3,
                    "thang_bat_dau": 10,
                    "thang_ket_thuc": 12,
                    "icon": "🍂",
                    "mau": "#0EA5E9",
                    "dac_trung": "Nghỉ đất sau 2 vụ lúa liên tiếp: cày ải phơi nỏ diệt mầm đạo ôn, sâu đục thân, rầy nâu.",
                },
            ]
        elif "3 Đợt Luân canh" in che_do_dot:
            cac_dot = E.tinh_toan_cac_dot("3 đợt")
        else:
            # Tự do tùy chỉnh số đợt và khoảng tháng
            st.markdown('<hr style="border-color:#E2E8F0; margin:10px 0 12px 0;">', unsafe_allow_html=True)
            col_so_dot, col_note = st.columns([1, 3])
            so_dot_custom = col_so_dot.selectbox(
                "Số lượng đợt trong năm:",
                [2, 3, 4],
                index=1,
                format_func=lambda x: f"{x} đợt canh tác",
                key=f"so_dot_custom_{E.khoa(vung)}_{nam}",
            )
            col_note.caption(
                "💡 Bạn có thể tự chọn tháng bắt đầu và kết thúc cho từng đợt theo đặc thù ruộng trũng hoặc ruộng vàn cao bán sơn địa."
            )

            cac_dot = []
            mau_sac = ["#16A34A", "#F59E0B", "#0EA5E9", "#8B5CF6"]
            icons = ["🌾", "☀️", "🥬", "❄️"]

            cols_custom = st.columns(so_dot_custom)
            for i in range(so_dot_custom):
                with cols_custom[i]:
                    st.markdown(
                        f'<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:6px 10px; margin-bottom:6px;">'
                        f'  <b style="color:{mau_sac[i]}; font-size:12px;">{icons[i]} Đợt {i+1}</b>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    ten_mac_dinh = f"Đợt {i+1}"
                    ten_dot_inp = st.text_input(
                        f"Tên đợt {i+1}:",
                        value=ten_mac_dinh,
                        key=f"custom_name_{i}_{E.khoa(vung)}_{nam}",
                        label_visibility="collapsed",
                    )

                    if so_dot_custom == 2:
                        val_start, val_end = (1, 6) if i == 0 else (7, 12)
                    elif so_dot_custom == 3:
                        val_start, val_end = (1, 5) if i == 0 else ((6, 9) if i == 1 else (10, 12))
                    else:
                        val_start, val_end = (i * 3 + 1, (i + 1) * 3)

                    c_start, c_end = st.columns(2)
                    t_start = c_start.selectbox(
                        "Bắt đầu:",
                        range(1, 13),
                        index=val_start - 1,
                        key=f"custom_start_{i}_{E.khoa(vung)}_{nam}",
                        format_func=lambda m: f"T{m}",
                    )
                    t_end = c_end.selectbox(
                        "Kết thúc:",
                        range(1, 13),
                        index=max(val_end - 1, t_start - 1),
                        key=f"custom_end_{i}_{E.khoa(vung)}_{nam}",
                        format_func=lambda m: f"T{m}",
                    )

                    if t_end < t_start:
                        t_end = t_start

                    so_thang = t_end - t_start + 1
                    cac_dot.append({
                        "ten": f"{ten_dot_inp} (Tháng {t_start} – Tháng {t_end})",
                        "ma": f"dot_{i+1}",
                        "so_thang": so_thang,
                        "thang_bat_dau": t_start,
                        "thang_ket_thuc": t_end,
                        "icon": icons[i],
                        "mau": mau_sac[i],
                        "dac_trung": f"Đợt {i+1} gồm {so_thang} tháng (từ tháng {t_start} đến tháng {t_end}).",
                    })

        # Xử lý nút bấm tự động gợi ý cơ cấu cây theo ưu tiên của nông dân
        if btn_auto:
            goi_y_auto = E.goi_y_to_hop_toi_uu(dl, vung, nam, cac_dot, uu_tien=uu_tien_nong_dan)
            for d in cac_dot:
                st.session_state[_khoa_session(vung, nam, d["ma"])] = goi_y_auto.get(d["ma"], [])
            st.toast(f"✅ Đã tối ưu hóa mùa vụ theo ưu tiên: {uu_tien_nong_dan}!", icon="🌾")
            st.rerun()

        # DẢI TIMELINE GANTT 12 THÁNG & BĂNG CẢNH BÁO THIÊN TAI NASA
        st.write("")
        st.markdown(
            '<div style="font-size:12px; font-weight:750; text-transform:uppercase; letter-spacing:0.06em; color:#64748B; margin-bottom:6px;">'
            '📅 Dải Tiến trình 12 Tháng & Lưới Rủi ro Thiên tai NASA:'
            '</div>',
            unsafe_allow_html=True,
        )

        # BĂNG CẢNH BÁO THỜI TIẾT THIÊN TAI THEO MÙA TRÊN ĐẦU TIMELINE
        st.markdown(
            """
            <div style="display:flex; margin-bottom:6px; font-size:10.5px; font-weight:750; gap:3px;">
              <div style="flex:4; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:3px 4px; text-align:center; color:#475569;">
                🌱 Khung Thuận lợi Vụ Xuân (T1–T4)
              </div>
              <div style="flex:3; background:#FEF2F2; border:1px solid #FECACA; border-radius:4px; padding:3px 4px; text-align:center; color:#DC2626;">
                🔥 VÙNG NGUY CƠ GIÓ LÀO ≥35°C (T5–T7)
              </div>
              <div style="flex:1; background:#FFFBEB; border:1px solid #FDE68A; border-radius:4px; padding:3px 4px; text-align:center; color:#D97706;">
                🌾 Trỗ T8
              </div>
              <div style="flex:2; background:#F0F9FF; border:1px solid #BAE6FD; border-radius:4px; padding:3px 4px; text-align:center; color:#0369A1;">
                🌊 BÃO LŨ VÁCH BẮC (T9–T10)
              </div>
              <div style="flex:2; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:3px 4px; text-align:center; color:#64748B;">
                🍂 Phơi ải T11–T12
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 12 Ô THÁNG TRỰC QUAN KẾT NỐI LIỀN MẠCH
        timeline_cols = st.columns(12)
        for m in range(1, 13):
            dot_so_huu = None
            for d in cac_dot:
                if d["thang_bat_dau"] <= m <= d["thang_ket_thuc"]:
                    dot_so_huu = d
                    break

            with timeline_cols[m - 1]:
                if dot_so_huu:
                    bg_col = dot_so_huu["mau"]
                    txt_col = "#FFFFFF"
                    label = f"{dot_so_huu['icon']}"
                else:
                    bg_col = "#F1F5F9"
                    txt_col = "#94A3B8"
                    label = "—"

                st.markdown(
                    f'<div style="background:{bg_col}; color:{txt_col}; border-radius:6px; padding:5px 2px; text-align:center; box-shadow:0 1px 2px rgba(0,0,0,0.06);">'
                    f'  <div style="font-size:11px; font-weight:800;">T{m}</div>'
                    f'  <div style="font-size:10px; margin-top:1px;">{label}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Chú giải các đợt dạng thẻ badge gọn gàng
        st.write("")
        legend_html = " ".join([
            f'<span style="display:inline-flex; align-items:center; gap:5px; margin-right:14px; font-size:12px; color:#334155;">'
            f'  <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{d["mau"]};"></span>'
            f'  <b>{d["icon"]} {d["ten"]}</b> ({d["so_thang"]} tháng)'
            f'</span>'
            for d in cac_dot
        ])
        st.markdown(f'<div style="background:#F8FAFC; border-radius:8px; padding:6px 12px; border:1px solid #E2E8F0;">{legend_html}</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. CHI TIẾT TỪNG ĐỢT & LỰA CHỌN CÂY TRỒNG VỰA LÚA (THẺ TÁC NGHIỆP ĐỒ HỌA)
    # -------------------------------------------------------------------------
    st.write("")
    st.markdown(
        '<div style="margin-bottom:8px;">'
        '  <div style="font-size:16px; font-weight:800; color:#0F172A;">📊 Phân tích Khí hậu Lịch sử & Chọn Cây trồng cho Từng Đợt</div>'
        '  <div style="font-size:11.5px; color:#64748B;">Bấm vào từng đợt bên dưới để xem đối chiếu dữ liệu viễn thám và điều chỉnh cơ cấu giống</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    tab_titles = [f"{d['icon']} {d['ten']}" for d in cac_dot]
    tabs = st.tabs(tab_titles)

    ke_hoach_nguoi_dung = {}
    danh_gia_cac_dot_map = {}

    for tab, d in zip(tabs, cac_dot):
        with tab:
            ma_dot = d["ma"]
            t_start, t_end = d["thang_bat_dau"], d["thang_ket_thuc"]

            # Phân tích khí hậu lịch sử của đợt từ engine
            kh = E.phan_tich_khi_hau_dot(dl, vung, t_start, t_end, nam, tb_df)

            # THANH ĐO AN TOÀN KHÍ HẬU NASA CHO ĐỢT CANH TÁC
            tmax_tb = kh["tmax_tb"]
            nong35_tb = kh["nong35_tong_tb"]
            mua_tb = kh["mua_tong_tb"]
            sm_tb = kh["sm_tb"]

            # Đánh giá rủi ro nhanh
            if nong35_tb >= 10 or tmax_tb >= 34.0:
                muc_an_toan = "Cảnh giác Gió Lào táp bông"
                col_at = "#DC2626"
                bg_at = "#FEF2F2"
                ic_at = "🔥"
            elif mua_tb >= 400:
                muc_an_toan = "Cảnh giác Mưa bão ngập úng"
                col_at = "#0284C7"
                bg_at = "#F0F9FF"
                ic_at = "🌊"
            else:
                muc_an_toan = "Khí hậu Thuận lợi cho Lúa"
                col_at = "#16A34A"
                bg_at = "#F0FDF4"
                ic_at = "🟢"

            st.markdown(
                f"""
                <div style="background:{bg_at}; border:1px solid #E2E8F0; border-left:4px solid {col_at}; border-radius:8px; padding:8px 12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                  <div>
                    <span style="font-size:12.5px; font-weight:800; color:{col_at};">{ic_at} Đánh giá Khí hậu NASA: {muc_an_toan}</span>
                    <span style="font-size:11.5px; color:#475569; margin-left:8px;">(Tháng {t_start} – Tháng {t_end})</span>
                  </div>
                  <div style="font-size:11px; color:#334155; display:flex; gap:12px;">
                    <span>🌡️ Tmax TB: <b>{tmax_tb:.1f}°C</b></span>
                    <span>🔥 Nắng nóng: <b>{nong35_tb:.0f} ngày</b></span>
                    <span>🌧️ Mưa tích lũy: <b>{mua_tb:.0f} mm</b></span>
                    <span>💧 Ẩm đất SMAP: <b>{sm_tb*100:.0f}%</b></span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # BỐ CỤC 2 CỘT: XẾP HẠNG THÍCH HỢP & TÙY CHỌN CƠ CẤU CANH TÁC
            col_trai, col_phai = st.columns([1, 1], gap="medium")

            # CỘT TRÁI: XẾP HẠNG THÍCH HỢP TỪ DỮ LIỆU LỊCH SỬ NASA
            with col_trai, st.container(border=True):
                st.markdown(
                    f'<div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:2px;">📈 Xếp hạng Cây trồng từ Lịch sử NASA ({so_nam_ls} năm)</div>'
                    f'<div style="font-size:11px; color:#64748B; margin-bottom:8px;">Đánh giá rủi ro khí hậu trong chuỗi Tháng {t_start}–{t_end} tại Yên Thành:</div>',
                    unsafe_allow_html=True,
                )
                df_dg_dot = E.danh_gia_cay_theo_dot(dl, vung, t_start, t_end, nam, tb_df)

                if df_dg_dot.empty:
                    st.caption("Chưa có đủ số liệu lịch sử để chấm điểm cây trồng cho đợt này.")
                else:
                    for _, row in df_dg_dot.iterrows():
                        cay_ten = row["cay"]
                        rui_ro = row["rui_ro_dot"]
                        muc_kn = row["muc_khuyen_nghi"]
                        icon = E.CAY.get(cay_ten, {}).get("icon", "🌱")

                        if "Nên trồng" in muc_kn:
                            mau = "#16A34A"
                            bg_pill = "#F0FDF4"
                        elif "Cân nhắc" in muc_kn:
                            mau = "#D97706"
                            bg_pill = "#FFFBEB"
                        else:
                            mau = "#DC2626"
                            bg_pill = "#FEF2F2"

                        st.markdown(
                            f"""<div style="border:1px solid #E2E8F0; border-left:3.5px solid {mau}; border-radius:8px; padding:7px 10px; margin-bottom:6px; background:#FFFFFF;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                              <span style="font-size:12.5px; font-weight:800; color:#0F172A;">{icon} {cay_ten}</span>
                              <span style="font-size:11px; font-weight:750; color:{mau}; background:{bg_pill}; border:1px solid {mau}; border-radius:999px; padding:1px 8px;">
                                {muc_kn} (Rủi ro {rui_ro:.0f}%)
                              </span>
                            </div>
                            <div style="font-size:11px; color:#64748B; margin-top:2px; line-height:1.35;">
                              {row['ly_do']}
                            </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

            # CỘT PHẢI: BẢNG TÙY CHỌN CƠ CẤU CANH TÁC & PHÂN BỔ DIỆN TÍCH
            with col_phai, st.container(border=True):
                st.markdown(
                    f'<div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:2px;">🌱 Cơ cấu Canh tác & Phân bổ Diện tích</div>'
                    f'<div style="font-size:11px; color:#64748B; margin-bottom:8px;">Chọn chuyên canh lúa hoặc luân canh màu để cắt mầm bệnh:</div>',
                    unsafe_allow_html=True,
                )

                cay_vung_list = list(E.CAY_VUNG.get(vung, []))
                khoa_dot = _khoa_session(vung, nam, ma_dot)
                ke_hoach_hien_tai = st.session_state.get(khoa_dot, [])

                # Chọn phương thức canh tác dạng segmented control gọn gàng
                so_luong_options = [
                    "🌾 Chuyên canh Lúa (100%)",
                    "🌱 Luân canh 2 cây (Lúa + Màu)",
                    "🍂 Để ải đất (Phơi ruộng)",
                ]

                so_cay_cu = len(ke_hoach_hien_tai)
                if so_cay_cu == 0:
                    idx_sl = 2 if ke_hoach_hien_tai == [] and khoa_dot in st.session_state else 0
                elif so_cay_cu == 1:
                    idx_sl = 0
                else:
                    idx_sl = 1

                chon_kieu_trong = st.radio(
                    f"Phương thức ({d['ten']}):",
                    so_luong_options,
                    index=idx_sl,
                    key=f"kieu_trong_opt_{ma_dot}_{E.khoa(vung)}_{nam}",
                    label_visibility="collapsed",
                )

                cay_da_chon = []

                if "Để ải đất" in chon_kieu_trong:
                    st.info("🍂 **Để ải phơi khô nỏ ruộng:** Giúp tiêu diệt mầm mống nấm bệnh đạo ôn và ấu trùng sâu đục thân trong đất.")
                    cay_da_chon = []
                else:
                    so_cay_muc_tieu = 1 if "Chuyên canh" in chon_kieu_trong else 2
                    top_cays = df_dg_dot["cay"].tolist() if not df_dg_dot.empty else cay_vung_list

                    for idx_cay in range(so_cay_muc_tieu):
                        st.markdown(f"<div style='font-size:11.5px; font-weight:750; color:#0F172A; margin-top:4px;'>Cây trồng thứ {idx_cay + 1}:</div>", unsafe_allow_html=True)
                        col_c, col_ty_le = st.columns([3, 2])

                        mac_dinh_cay = (
                            ke_hoach_hien_tai[idx_cay]["cay"]
                            if idx_cay < len(ke_hoach_hien_tai) and ke_hoach_hien_tai[idx_cay]["cay"] in cay_vung_list
                            else (top_cays[idx_cay % len(top_cays)] if top_cays else "Lúa")
                        )
                        c_idx = cay_vung_list.index(mac_dinh_cay) if mac_dinh_cay in cay_vung_list else 0

                        cay_duoc_chon = col_c.selectbox(
                            f"Chọn cây {idx_cay + 1}",
                            cay_vung_list,
                            index=c_idx,
                            key=f"sel_cay_{ma_dot}_{idx_cay}_{E.khoa(vung)}_{nam}",
                            label_visibility="collapsed",
                        )

                        if so_cay_muc_tieu == 1:
                            ty_le = 100
                            col_ty_le.markdown("<div style='margin-top:6px; font-weight:800; color:#16A34A; font-size:12px;'>100% diện tích</div>", unsafe_allow_html=True)
                        else:
                            mac_dinh_tl = ke_hoach_hien_tai[idx_cay]["ty_le_pct"] if idx_cay < len(ke_hoach_hien_tai) else (70 if idx_cay == 0 else 30)
                            ty_le = col_ty_le.slider(
                                f"Tỷ lệ %",
                                10, 90, int(mac_dinh_tl), step=5,
                                key=f"tl_cay_{ma_dot}_{idx_cay}_{E.khoa(vung)}_{nam}",
                                label_visibility="collapsed",
                            )

                        cay_da_chon.append({"cay": cay_duoc_chon, "ty_le_pct": ty_le})

                if cay_da_chon:
                    tong_tl = sum(c["ty_le_pct"] for c in cay_da_chon)
                    if tong_tl > 0:
                        for c in cay_da_chon:
                            c["ty_le_pct"] = round(c["ty_le_pct"] * 100 / tong_tl)

                st.session_state[khoa_dot] = cay_da_chon
                ke_hoach_nguoi_dung[ma_dot] = cay_da_chon

                dg_to_hop = E.danh_gia_to_hop_dot(df_dg_dot, cay_da_chon)
                danh_gia_cac_dot_map[ma_dot] = dg_to_hop

                # Thẻ tổng hợp rủi ro đợt dạng đồ họa
                col_rr_num = '#16A34A' if dg_to_hop['rui_ro_to_hop'] < 40 else ('#D97706' if dg_to_hop['rui_ro_to_hop'] < 60 else '#DC2626')
                st.markdown(
                    f"""<div style="background:#F8FAFC; border-radius:8px; padding:8px 10px; border:1px solid #E2E8F0; margin-top:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                      <span style="font-weight:750; color:#0F172A; font-size:12px;">🛡️ Rủi ro tổ hợp đợt:</span>
                      <span style="font-size:13px; font-weight:800; color:{col_rr_num};">
                        {dg_to_hop['rui_ro_to_hop']:.0f}%
                      </span>
                    </div>
                    <div style="font-size:11px; color:#475569; margin-top:3px; line-height:1.35;">
                      {dg_to_hop['nhan_xet']}
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    # -------------------------------------------------------------------------
    # 4. TỔNG KẾT KẾ HOẠCH NĂM & BIỂU ĐỒ GANTT LỊCH MÙA VỤ ĐA MÀU SẮC
    # -------------------------------------------------------------------------
    st.write("")
    with st.container(border=True):
        st.markdown(
            '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">'
            '  <div>'
            '    <div style="font-size:16px; font-weight:800; color:#0F172A;">📋 Bảng Điểm Nông Học & Lịch Canh Tác Cả Năm</div>'
            '    <div style="font-size:11.5px; color:#64748B;">Tổng hợp rủi ro thiên tai và hiệu quả cải tạo phì nhiêu cho đất lúa Yên Thành</div>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True,
        )

        danh_gia_nam = E.danh_gia_ke_hoach_nam(cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map)

        p1, p2, p3, p4 = st.columns(4)
        with p1, st.container(border=True):
            st.markdown(
                f'<div class="l">Số đợt canh tác</div>'
                f'<div class="v">{danh_gia_nam["so_dot"]} <small>đợt</small></div>'
                f'<div class="d nt">Độ phủ: {danh_gia_nam["so_thang_phu"]}/12 tháng</div>',
                unsafe_allow_html=True,
            )
        with p2, st.container(border=True):
            rr = danh_gia_nam["rui_ro_tb_nam"]
            cls_rr = "dn" if rr < 35 else ("nt" if rr < 60 else "up")
            st.markdown(
                f'<div class="l">Rủi ro bình quân năm</div>'
                f'<div class="v">{rr:.0f} <small>%</small></div>'
                f'<div class="d {cls_rr}">Đánh giá: {danh_gia_nam["muc_rui_ro_nam"]}</div>',
                unsafe_allow_html=True,
            )
        with p3, st.container(border=True):
            st.markdown(
                f'<div class="l">Số loại cây tham gia</div>'
                f'<div class="v">{len(danh_gia_nam["cay_da_dung"])} <small>loại</small></div>'
                f'<div class="d nt">{", ".join(danh_gia_nam["cay_da_dung"]) if danh_gia_nam["cay_da_dung"] else "Chuyên canh lúa"}</div>',
                unsafe_allow_html=True,
            )
        with p4, st.container(border=True):
            st.markdown(
                f'<div class="l">Điểm luân canh & đất</div>'
                f'<div class="v">{danh_gia_nam["diem_luan_canh"]} <small>/100</small></div>'
                f'<div class="d dn">Khả năng bồi dưỡng đất</div>',
                unsafe_allow_html=True,
            )

        # Lời khuyên nông học ngắn gọn 1 câu
        st.markdown(
            f"""<div style="background:#F0FDF4; border-left:4px solid #16A34A; border-radius:8px; padding:10px 14px; margin-top:8px;">
            <b style="color:#16A34A; font-size:13px;">🌾 Khuyến nghị Nông học Vựa lúa Yên Thành:</b>
            <div style="font-size:12px; color:#1E293B; margin-top:3px; line-height:1.45;">
              {danh_gia_nam['khuyen_nghi_tong']}
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # KHỐI SO SÁNH ĐỊNH LƯỢNG SỨC KHỎE ĐẤT & PHỤC HỒI DÀI HẠN (SOIL HEALTH INDEX - SHI)
        shi_val = danh_gia_nam.get("diem_suc_khoe_dat", 85)
        nuoc_val = danh_gia_nam.get("tiet_kiem_nuoc_pct", 20)
        co_dau = danh_gia_nam.get("co_cay_dau", False)
        co_ai = danh_gia_nam.get("co_de_ai", False)

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #BBF7D0; border-radius:12px; padding:14px 18px; margin-top:12px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-size:20px;">🧪</span>
                  <div>
                    <div style="font-size:14px; font-weight:800; color:#0F172A;">ĐÁNH GIÁ SỨC KHỎE ĐẤT & KHẢ NĂNG PHỤC HỒI LÂU DÀI (SOIL HEALTH INDEX)</div>
                    <div style="font-size:11.5px; color:#16A34A; font-weight:700;">Mô phỏng nông học trên thổ nhưỡng Yên Thành (Carbon hữu cơ SOC, N cố định, Nấm bệnh, Nước tưới Ba Ra)</div>
                  </div>
                </div>
                <div style="font-size:12px; font-weight:800; color:#16A34A; background:#DCFCE7; border:1px solid #16A34A; border-radius:999px; padding:2px 10px;">
                  Chỉ số SHI: {shi_val}/100
                </div>
              </div>
              
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-bottom:12px;">
                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:10px;">
                  <div style="font-size:11px; font-weight:750; color:#16A34A;">🍂 CARBON HỮU CƠ (SOC)</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">{'+25% đến +35%' if co_dau else 'Duy trì ổn định'}</div>
                  <div style="font-size:11px; color:#475569;">Bồi đắp sinh khối & nốt sần rễ</div>
                </div>
                <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:10px;">
                  <div style="font-size:11px; font-weight:750; color:#0284C7;">💧 TIẾT KIỆM NƯỚC TƯỚI</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">Tiết kiệm ~{nuoc_val}%</div>
                  <div style="font-size:11px; color:#475569;">Giảm áp lực Ba Ra Đô Lương</div>
                </div>
                <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:10px;">
                  <div style="font-size:11px; font-weight:750; color:#D97706;">🦠 CẮT MẦM ĐẠO ÔN & SÂU</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">{'Giảm 85–90%' if co_ai else 'Cần theo dõi sát'}</div>
                  <div style="font-size:11px; color:#475569;">Nhờ cày lật phơi nỏ ải đất</div>
                </div>
                <div style="background:#FAF5FF; border:1px solid #E9D5FF; border-radius:8px; padding:10px;">
                  <div style="font-size:11px; font-weight:750; color:#7C3AED;">🛡️ KHẢ NĂNG THÍCH ỨNG</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">{danh_gia_nam['muc_rui_ro_nam']}</div>
                  <div style="font-size:11px; color:#475569;">Thích ứng biến đổi khí hậu</div>
                </div>
              </div>

              <div style="display:flex; gap:12px; flex-wrap:wrap; font-size:12px; line-height:1.45; border-top:1px solid #E2E8F0; padding-top:10px;">
                <div style="flex:1; min-width:280px; background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:8px 12px;">
                  <b style="color:#DC2626;">❌ Nếu Độc Canh Lúa thuần (2–3 vụ liên tục):</b><br>
                  Đất ruộng bị dí nén, yếm khí lâu ngày; nấm đạo ôn và ấu trùng sâu đục thân tích tụ trong bùn; tiêu hao >12.000 m³ nước/ha; độ phì nhiêu suy giảm dần qua từng năm.
                </div>
                <div style="flex:1; min-width:280px; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 12px;">
                  <b style="color:#16A34A;">✅ Khi Thực Hiện Luân Canh Lúa – Lạc – Phơi Ải:</b><br>
                  Rễ lạc tiết nốt sần Rhizobium cố định 40–60 kg N/ha hữu cơ tự nhiên; phơi nỏ ruộng vụ đông diệt bào tử nấm; đất tơi xốp, hệ vi sinh vật hiếu khí hồi sinh mạnh mẽ.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown('<div style="font-size:13px; font-weight:800; color:#0F172A; margin-bottom:4px;">📊 Biểu đồ Lịch Mùa vụ 12 tháng tại Yên Thành (Gantt Chart):</div>', unsafe_allow_html=True)

        gantt_rows = []
        for d in cac_dot:
            cays = ke_hoach_nguoi_dung.get(d["ma"], [])
            if not cays:
                gantt_rows.append({
                    "Vụ": d["ten"].split("(")[0].strip(),
                    "Cây trồng": "🍂 Để ải / Phơi ruộng",
                    "Bắt đầu": d["thang_bat_dau"],
                    "Thời lượng": d["so_thang"],
                    "Tỷ lệ": 100,
                    "Màu": "#94A3B8",
                })
            else:
                for c in cays:
                    gantt_rows.append({
                        "Vụ": d["ten"].split("(")[0].strip(),
                        "Cây trồng": c["cay"],
                        "Bắt đầu": d["thang_bat_dau"],
                        "Thời lượng": d["so_thang"],
                        "Tỷ lệ": c["ty_le_pct"],
                        "Màu": d["mau"],
                    })

        if gantt_rows:
            fig_gantt = go.Figure()
            for r in gantt_rows:
                fig_gantt.add_trace(go.Bar(
                    name=f"{r['Cây trồng']} ({r['Tỷ lệ']}%)",
                    y=[r["Vụ"]],
                    x=[r["Thời lượng"]],
                    base=r["Bắt đầu"] - 1,
                    orientation="h",
                    marker=dict(color=r["Màu"], line=dict(color="#FFFFFF", width=2), cornerradius=6),
                    text=f"<b>{r['Cây trồng']}</b> ({r['Tỷ lệ']}%)",
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="#FFFFFF", family="Be Vietnam Pro", size=12),
                    hoverinfo="text",
                    hovertext=f"{r['Vụ']}: {r['Cây trồng']} ({r['Tỷ lệ']}%) từ Tháng {r['Bắt đầu']} đến Tháng {r['Bắt đầu'] + r['Thời lượng'] - 1}",
                ))

            fig_gantt.update_layout(
                barmode="stack",
                height=180 + len(cac_dot) * 35,
                margin=dict(l=10, r=10, t=10, b=25),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    tickvals=list(range(12)),
                    ticktext=[f"Tháng {m}" for m in range(1, 13)],
                    range=[0, 12],
                    gridcolor="#F1F5F9",
                ),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            )
            ve(fig_gantt, che_do="co_dinh")
