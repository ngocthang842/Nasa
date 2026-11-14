"""Trang Kế hoạch Mùa vụ & Luân canh Đa canh — Vựa lúa Huyện Yên Thành (Nghệ An).
Thiết kế Số hóa & Chuẩn hóa Dữ liệu (Digitized & Standardized Dashboard Layout):
- Tầng 1: KPI Ribbon 4 Chỉ số Nông học Số hóa (SHI, Rủi ro khí hậu, Nước tưới, Đạm cố định).
- Tầng 2: Hệ thống 3 Tabs Tinh gọn, vừa khít màn hình, loại bỏ cuộn dọc dài vô tận:
  * Tab 1: 🌾 Lập Kế hoạch Mùa vụ & Bảng Ma trận Cơ cấu Cây trồng Số hóa
  * Tab 2: 🧪 Chỉ số Sức khỏe Đất (Soil Health Index) & So sánh Định lượng
  * Tab 3: 🛰️ Đối chiếu Khí tượng & Rủi ro Thiên tai Viễn thám NASA
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

    # 1. HEADER CHUẨN
    tieu_de(vung, thang, nam, "KẾ HOẠCH MÙA VỤ, LUÂN CANH & SỨC KHỎE ĐẤT YÊN THÀNH", len(years) < 2)

    # Khởi tạo mô hình mùa vụ mặc định
    key_che_do = f"che_do_vu_pills_{E.khoa(vung)}_{nam}"
    if key_che_do not in st.session_state:
        st.session_state[key_che_do] = "2 Vụ Lúa Thuần"

    che_do_hien_tai = st.session_state[key_che_do]

    if "3 Đợt" in che_do_hien_tai or "Luân Canh" in che_do_hien_tai:
        cac_dot = [
            {"ma": "xuan", "ten": "Vụ Xuân Sớm", "thang_bat_dau": 1, "thang_ket_thuc": 4, "so_thang": 4, "cay": "Lúa", "icon": "🌾", "mau": "#16A34A"},
            {"ma": "hethu", "ten": "Vụ Hè Thu Sớm", "thang_bat_dau": 5, "thang_ket_thuc": 8, "so_thang": 4, "cay": "Lúa", "icon": "☀️", "mau": "#D97706"},
            {"ma": "dong", "ten": "Vụ Đông (Lạc/Ngô)", "thang_bat_dau": 9, "thang_ket_thuc": 12, "so_thang": 4, "cay": "Lạc", "icon": "🥜", "mau": "#0284C7"},
        ]
    else:
        cac_dot = [
            {"ma": "xuan", "ten": "Vụ Lúa Chiêm Xuân", "thang_bat_dau": 1, "thang_ket_thuc": 5, "so_thang": 5, "cay": "Lúa", "icon": "🌾", "mau": "#16A34A"},
            {"ma": "hethu", "ten": "Vụ Lúa Hè Thu", "thang_bat_dau": 6, "thang_ket_thuc": 9, "so_thang": 4, "cay": "Lúa", "icon": "☀️", "mau": "#D97706"},
            {"ma": "dong_ai", "ten": "Cày Ải & Vụ Đông", "thang_bat_dau": 10, "thang_ket_thuc": 12, "so_thang": 3, "cay": "Ngô / Phơi Ải", "icon": "🚜", "mau": "#0284C7"},
        ]

    # Kiểm tra dữ liệu kế hoạch người dùng
    ke_hoach_nguoi_dung = {}
    danh_gia_cac_dot_map = {}
    for d in cac_dot:
        khoa = _khoa_session(vung, nam, d["ma"])
        if khoa not in st.session_state:
            # Gán mặc định cây trồng ban đầu
            if d["ma"] == "xuan":
                st.session_state[khoa] = [{"cay": "Lúa", "ty_le_pct": 100}]
            elif d["ma"] == "hethu":
                st.session_state[khoa] = [{"cay": "Lúa", "ty_le_pct": 80}, {"cay": "Lạc", "ty_le_pct": 20}] if "3 Đợt" in che_do_hien_tai else [{"cay": "Lúa", "ty_le_pct": 100}]
            else:
                st.session_state[khoa] = [{"cay": "Lạc", "ty_le_pct": 60}, {"cay": "Ngô", "ty_le_pct": 40}] if "3 Đợt" in che_do_hien_tai else []
        ke_hoach_nguoi_dung[d["ma"]] = st.session_state[khoa]

        df_dg = E.danh_gia_cay_theo_dot(dl, vung, d["thang_bat_dau"], d["thang_ket_thuc"], nam, tb_df)
        danh_gia_cac_dot_map[d["ma"]] = E.danh_gia_to_hop_dot(df_dg, ke_hoach_nguoi_dung[d["ma"]])

    danh_gia_nam = E.danh_gia_ke_hoach_nam(cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map)

    # 2. BỘ 4 THẺ SỐ HÓA KPI NÔNG HỌC CỐT LÕI (STANDARDIZED METRIC RIBBON)
    shi_score = danh_gia_nam.get("diem_suc_khoe_dat", 85)
    rr_tb = danh_gia_nam.get("rui_ro_tb_nam", 32)
    tiet_kiem_nuoc = danh_gia_nam.get("tiet_kiem_nuoc_pct", 20)
    co_cay_dau = danh_gia_nam.get("co_cay_dau", False)
    dam_co_dinh = "+45 kg N/ha" if co_cay_dau else "Chưa có cây họ đậu"

    col_k1, col_k2, col_k3, col_k4 = st.columns(4, gap="small")
    with col_k1:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#16A34A; text-transform:uppercase;">🧪 SỨC KHỎE ĐẤT (SHI)</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{shi_score} <small style="font-size:13px; color:#64748B;">/ 100 điểm</small></div>
              <div style="font-size:11px; color:#16A34A; font-weight:600;">▲ Tốt (Độ phì cao & vi sinh vật)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k2:
        col_rr_clr = "#16A34A" if rr_tb < 35 else ("#D97706" if rr_tb < 55 else "#DC2626")
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid {col_rr_clr}; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:{col_rr_clr}; text-transform:uppercase;">🛡️ RỦI RO THỜI TIẾT BÌNH QUÂN</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{rr_tb:.0f}% <small style="font-size:13px; color:#64748B;">({danh_gia_nam['muc_rui_ro_nam']})</small></div>
              <div style="font-size:11px; color:#475569;">Gió Lào T7 & Bão lũ T9 được kiểm soát</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k3:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #0284C7; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#0284C7; text-transform:uppercase;">💧 TIẾT KIỆM NƯỚC BA RA</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">~{tiet_kiem_nuoc}% <small style="font-size:13px; color:#64748B;">nhu cầu nước</small></div>
              <div style="font-size:11px; color:#0284C7; font-weight:600;">Giảm áp lực cống sông Lam</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k4:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #8B5CF6; border-radius:10px; padding:10px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size:11px; font-weight:750; color:#8B5CF6; text-transform:uppercase;">🍂 ĐẠM HỮU CƠ CỐ ĐỊNH</div>
              <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">{dam_co_dinh}</div>
              <div style="font-size:11px; color:#64748B;">Vi sinh nốt sần Rhizobium tự nhiên</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 3. HỆ THỐNG 3 TABS CHUYÊN MÔN HÓA (LOẠI BỎ CUỘN DÀI)
    tab1, tab2, tab3 = st.tabs([
        "🌾 1. Lập Kế Hoạch 3 Vụ & Cơ Cấu Cây Trồng Số Hóa",
        "🧪 2. Thí Nghiệm Sức Khỏe Đất & So Sánh Định Lượng (SHI)",
        "🛰️ 3. Đối Chiếu Khí Tượng & Lưới Rủi Ro Thiên Tai NASA",
    ])

    with tab1:
        _hien_tab_lap_ke_hoach(dl, vung, nam, tb_df, cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map, danh_gia_nam)

    with tab2:
        _hien_tab_suc_khoe_dat(danh_gia_nam)

    with tab3:
        _hien_tab_doi_chieu_vi_tri_khi_hau(dl, vung, nam, cac_dot)


# =============================================================================
# TAB 1: LẬP KẾ HOẠCH MÙA VỤ & BẢNG MA TRẬN CƠ CẤU CÂY TRỒNG SỐ HÓA
# =============================================================================

def _hien_tab_lap_ke_hoach(dl, vung, nam, tb_df, cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map, danh_gia_nam):
    """Tab 1: Bảng điều khiển cơ cấu mùa vụ số hóa, bảng ma trận và Gantt chart."""
    # Khung chọn mô hình & Ưu tiên nông dân thu nhỏ, không đè vỡ chữ
    with st.container(border=True):
        col_ctrl1, col_ctrl2, col_btn = st.columns([4.2, 4.3, 3.5], gap="small")
        with col_ctrl1:
            st.markdown("<div style='font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;'>🌾 1. Khung Mùa Vụ Thực Tế:</div>", unsafe_allow_html=True)
            kieu_vu = st.selectbox(
                "Mô hình mùa vụ:",
                options=["2 Vụ Lúa Thuần (Xuân T1–T5 & Hè Thu T6–T9)", "3 Đợt Luân Canh Lúa – Màu (Xuân T1–T4, Hè Thu T5–T8, Đông T9–T12)"],
                index=0 if "2 Vụ" in st.session_state.get(f"che_do_vu_pills_{E.khoa(vung)}_{nam}", "") else 1,
                key=f"sel_kieu_vu_box_{nam}",
                label_visibility="collapsed",
            )
            if kieu_vu != st.session_state.get(f"che_do_vu_pills_{E.khoa(vung)}_{nam}", ""):
                st.session_state[f"che_do_vu_pills_{E.khoa(vung)}_{nam}"] = kieu_vu
                st.rerun()

        with col_ctrl2:
            st.markdown("<div style='font-size:11.5px; font-weight:750; color:#0F172A; margin-bottom:4px;'>🎯 2. Mục Tiêu Ưu Tiên Nông Dân:</div>", unsafe_allow_html=True)
            uu_tien = st.selectbox(
                "Ưu tiên:",
                options=[
                    "🧪 Cải tạo đất & Bồi dưỡng độ phì",
                    "💧 Tiết kiệm nước & Chống hạn",
                    "💰 Năng suất & Thu nhập cao",
                    "🛡️ An toàn & Né thiên tai",
                ],
                index=0,
                key=f"sel_prio_box_{nam}",
                label_visibility="collapsed",
            )

        with col_btn:
            st.markdown("<div style='height:21px;'></div>", unsafe_allow_html=True)
            if st.button("✨ AI Đề Xuất Tối Ưu Hóa", type="primary", use_container_width=True, help="Tự động tính toán tỷ lệ % cây trồng tối ưu theo viễn thám NASA"):
                goi_y = E.goi_y_to_hop_toi_uu(dl, vung, nam, cac_dot, uu_tien=uu_tien)
                for d in cac_dot:
                    st.session_state[_khoa_session(vung, nam, d["ma"])] = goi_y.get(d["ma"], [])
                st.toast(f"✅ Đã tối ưu hóa mùa vụ theo: {uu_tien}!", icon="🌾")
                st.rerun()

    # BẢNG MA TRẬN CƠ CẤU MÙA VỤ SỐ HÓA (DIGITIZED ALLOCATION MATRIX)
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
            '  <div>'
            '    <div style="font-size:13.5px; font-weight:800; color:#0F172A;">📋 Bảng Ma Trận Cơ Cấu Mùa Vụ Chuẩn Hóa Yên Thành</div>'
            '    <div style="font-size:11.5px; color:#64748B;">Tổng hợp thời gian, giống cây, tỷ lệ diện tích %, rủi ro khí hậu và giải pháp kỹ thuật</div>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True,
        )

        rows_table = []
        for d in cac_dot:
            cays = ke_hoach_nguoi_dung.get(d["ma"], [])
            dg = danh_gia_cac_dot_map.get(d["ma"], {})
            rr_val = dg.get("rui_ro_to_hop", 35.0)

            cays_str = ", ".join([f"{c['cay']} ({c['ty_le_pct']}%)" for c in cays]) if cays else "🍂 Phơi ải / Nghỉ đất (100%)"
            
            # Đánh giá nước tưới
            if d["ma"] == "xuan":
                nuoc_str = "💧 Đủ nước tự chảy (Ba Ra Đô Lương)"
                khuyen_nghi = "Gieo mạ chống rét T1, trỗ rộ T4 né táp gió Lào, gặt T5."
            elif d["ma"] == "hethu":
                nuoc_str = "⚠️ Cần tưới đệm giữ mát T7"
                khuyen_nghi = "Cấy cực nhanh, gặt trước 15/9 né lũ Kênh Vách Bắc."
            else:
                nuoc_str = "🌾 Không cần cấp nước"
                khuyen_nghi = "Cày sâu phơi nỏ ruộng diệt mầm đạo ôn, xen canh màu."

            rows_table.append({
                "Vụ Mùa": f"{d['icon']} {d['ten']}",
                "Thời Gian": f"T{d['thang_bat_dau']} → T{d['thang_ket_thuc']} ({d['so_thang']} tháng)",
                "Cây Trồng & Tỷ Lệ": cays_str,
                "Rủi Ro Khí Hậu": f"{rr_val:.0f}% ({dg.get('muc', 'Nên trồng')})",
                "Nguồn Nước Ba Ra": nuoc_str,
                "Khuyến Nghị Nông Học": khuyen_nghi,
            })

        df_show = pd.DataFrame(rows_table)
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    # ĐIỀU CHỈNH NHANH TỶ LỆ CÂY TRỒNG TỪNG ĐỢT (GỌN GÀNG THEO TỪNG CỘT)
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12.5px; font-weight:750; color:#0F172A; margin-bottom:6px;'>⚙️ Tùy Chỉnh Cơ Cấu Cây Trồng Từng Vụ (Nhấp để đổi giống & tỷ lệ %):</div>", unsafe_allow_html=True)

    cols_dot = st.columns(len(cac_dot), gap="small")
    for idx_d, (col, d) in enumerate(zip(cols_dot, cac_dot)):
        with col, st.container(border=True):
            st.markdown(
                f'<div style="font-size:12px; font-weight:800; color:{d["mau"]}; border-bottom:1px solid #F1F5F9; padding-bottom:4px; margin-bottom:6px;">'
                f'{d["icon"]} {d["ten"]} (T{d["thang_bat_dau"]}–T{d["thang_ket_thuc"]})'
                f'</div>',
                unsafe_allow_html=True,
            )
            khoa = _khoa_session(vung, nam, d["ma"])
            curr_plan = st.session_state.get(khoa, [])
            
            opt_mode = ["Lúa thuần 100%", "Lúa + Lạc luân canh", "Phơi ải ruộng"]
            idx_m = 0
            if len(curr_plan) == 0:
                idx_m = 2
            elif len(curr_plan) >= 2:
                idx_m = 1

            chon_opt = st.selectbox(
                f"Kiểu canh tác ({d['ma']}):",
                opt_mode,
                index=idx_m,
                key=f"quick_sel_mode_{d['ma']}_{nam}",
                label_visibility="collapsed",
            )

            new_plan = []
            if "Phơi ải" in chon_opt:
                new_plan = []
                st.caption("🍂 Nghỉ đất phơi nỏ diệt nấm bệnh.")
            elif "luân canh" in chon_opt:
                tl_lua = st.slider(f"Tỷ lệ Lúa % ({d['ma']}):", 30, 80, 70, step=10, key=f"sld_lua_{d['ma']}_{nam}")
                tl_lac = 100 - tl_lua
                new_plan = [{"cay": "Lúa", "ty_le_pct": tl_lua}, {"cay": "Lạc", "ty_le_pct": tl_lac}]
                st.caption(f"🌾 Lúa: {tl_lua}% · 🥜 Lạc: {tl_lac}%")
            else:
                new_plan = [{"cay": "Lúa", "ty_le_pct": 100}]
                st.caption("🌾 Chuyên canh lúa 100% diện tích.")

            if new_plan != curr_plan:
                st.session_state[khoa] = new_plan

    # BIỂU ĐỒ GANTT LỊCH 12 THÁNG SỐ HÓA
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div style="font-size:12.5px; font-weight:800; color:#0F172A; margin-bottom:4px;">📊 Biểu Đồ Gantt Phân Bổ Mùa Vụ 12 Tháng Yên Thành</div>', unsafe_allow_html=True)

        gantt_rows = []
        for d in cac_dot:
            cays = st.session_state.get(_khoa_session(vung, nam, d["ma"]), [])
            if not cays:
                gantt_rows.append({
                    "Vụ": d["ten"],
                    "Cây trồng": "🍂 Phơi Ải Đất",
                    "Bắt đầu": d["thang_bat_dau"],
                    "Thời lượng": d["so_thang"],
                    "Tỷ lệ": 100,
                    "Màu": "#94A3B8",
                })
            else:
                for c in cays:
                    gantt_rows.append({
                        "Vụ": d["ten"],
                        "Cây trồng": c["cay"],
                        "Bắt đầu": d["thang_bat_dau"],
                        "Thời lượng": d["so_thang"],
                        "Tỷ lệ": c["ty_le_pct"],
                        "Màu": "#16A34A" if c["cay"] == "Lúa" else ("#D97706" if c["cay"] == "Lạc" else "#0284C7"),
                    })

        fig_gantt = go.Figure()
        for r in gantt_rows:
            fig_gantt.add_trace(go.Bar(
                name=f"{r['Cây trồng']} ({r['Tỷ lệ']}%)",
                y=[r["Vụ"]],
                x=[r["Thời lượng"]],
                base=r["Bắt đầu"] - 1,
                orientation="h",
                marker=dict(color=r["Màu"], line=dict(color="#FFFFFF", width=2), cornerradius=5),
                text=f"<b>{r['Cây trồng']}</b> ({r['Tỷ lệ']}%)",
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#FFFFFF", family="Be Vietnam Pro", size=11, weight=700),
                hovertemplate=f"<b>{r['Vụ']}</b>: {r['Cây trồng']} ({r['Tỷ lệ']}%)<br>Từ Tháng {r['Bắt đầu']} đến Tháng {r['Bắt đầu'] + r['Thời lượng'] - 1}<extra></extra>",
            ))

        fig_gantt.update_layout(
            barmode="stack",
            height=160 + len(cac_dot) * 28,
            margin=dict(l=10, r=10, t=10, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(
                tickvals=list(range(12)),
                ticktext=[f"T{m}" for m in range(1, 13)],
                range=[0, 12],
                gridcolor="#F1F5F9",
                tickfont=dict(size=11, color="#0F172A", weight=600),
            ),
            yaxis=dict(
                autorange="reversed",
                tickfont=dict(size=11, color="#0F172A", weight=600),
            ),
            showlegend=False,
        )
        ve(fig_gantt, che_do="co_dinh")


# =============================================================================
# TAB 2: THÍ NGHIỆM SỨC KHỎE ĐẤT & SO SÁNH ĐỊNH LƯỢNG (SOIL HEALTH INDEX)
# =============================================================================

def _hien_tab_suc_khoe_dat(danh_gia_nam):
    """Tab 2: Định lượng số hóa chỉ số sức khỏe đất (SHI) và so sánh khoa học."""
    shi_val = danh_gia_nam.get("diem_suc_khoe_dat", 85)
    nuoc_val = danh_gia_nam.get("tiet_kiem_nuoc_pct", 20)
    co_dau = danh_gia_nam.get("co_cay_dau", False)
    co_ai = danh_gia_nam.get("co_de_ai", False)

    col_box1, col_box2 = st.columns([1, 1], gap="medium")

    with col_box1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:8px;">
                  🧪 Bảng Chỉ Số Sức Khỏe Đất Định Lượng (Soil Health Scorecard)
                </div>
                """,
                unsafe_allow_html=True,
            )
            data_shi = [
                {"Chỉ Số Đất": "🍂 Carbon Hữu Cơ (SOC)", "Giá Trị Định Lượng": "+28% đến +35%" if co_dau else "Duy trì ổn định", "Đánh Giá Nông Học": "Tích lũy chất mùn hữu cơ từ rễ nốt sần"},
                {"Chỉ Số Đất": "💧 Tiết Kiệm Nước Ba Ra", "Giá Trị Định Lượng": f"Giảm {nuoc_val}% nhu cầu", "Đánh Giá Nông Học": "Giảm áp lực cống lấy nước sông Lam"},
                {"Chỉ Số Đất": "🦠 Cắt Mầm Đạo Ôn & Sâu", "Giá Trị Định Lượng": "Giảm 85–90%" if co_ai else "Cần theo dõi sát", "Đánh Giá Nông Học": "Nhờ cày sâu phơi nỏ đất diệt bào tử"},
                {"Chỉ Số Đất": "🌱 Đạm Vi Sinh Hữu Cơ (N)", "Giá Trị Định Lượng": "+40–60 kg N/ha" if co_dau else "0 kg N", "Đánh Giá Nông Học": "Vi khuẩn Rhizobium cố định đạm khí trời"},
                {"Chỉ Số Đất": "🛡️ Độ Ổn Định Kết Cấu Đất", "Giá Trị Định Lượng": f"{shi_val}/100 điểm", "Đánh Giá Nông Học": "Đất tơi xốp, hệ vi sinh vật hiếu khí mạnh"},
            ]
            st.dataframe(pd.DataFrame(data_shi), use_container_width=True, hide_index=True)

    with col_box2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:8px;">
                  ⚖️ So Sánh Định Lượng: Độc Canh Lúa vs Luân Canh Lúa – Màu
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div style="display:flex; flex-direction:column; gap:8px; font-size:12px;">
                  <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #DC2626; border-radius:8px; padding:9px 12px;">
                    <b style="color:#DC2626;">❌ Nếu Độc Canh Lúa Thuần (2–3 vụ liên tục):</b><br>
                    • Tiêu tốn <b>>12.500 m³ nước/ha</b> suốt chu kỳ.<br>
                    • Đất bị dí nén tầng đế cày, yếm khí, rơm rạ không phân hủy sinh ngộ độc hữu cơ.<br>
                    • Bào tử đạo ôn cổ bông và rầy nâu lưu cữu trong bùn ruộng qua các năm.
                  </div>
                  <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:9px 12px;">
                    <b style="color:#16A34A;">✅ Khi Thực Hiện Luân Canh Lúa – Lạc – Phơi Ải:</b><br>
                    • Tiết kiệm <b>~2.500–3.000 m³ nước/ha</b>, chia sẻ nước cho vùng cuối kênh.<br>
                    • Cố định tự nhiên <b>40–60 kg N/ha</b> tương đương bón 2 bao urê sạch.<br>
                    • Cắt đứt chu kỳ sinh thái của sâu bệnh, đất ruộng tơi xốp, năng suất vụ sau tăng +8–12%.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # KHUYẾN NGHỊ TỔNG KẾT
    st.markdown(
        f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #0F766E; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:12.5px; color:#1E293B;">
          <b>🌾 Khuyến nghị chiến lược cho Nông nghiệp Yên Thành:</b> {danh_gia_nam['khuyen_nghi_tong']}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# TAB 3: ĐỐI CHIẾU KHÍ TƯỢNG & LƯỚI RỦI RO THIÊN TAI VIỄN THÁM NASA
# =============================================================================

def _hien_tab_doi_chieu_vi_tri_khi_hau(dl, vung, nam, cac_dot):
    """Tab 3: Chuẩn hóa dữ liệu viễn thám khí hậu NASA 12 tháng và thiên tai đặc thù."""
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:8px;">
              🛰️ Lưới Rủi Ro Thiên Tai & Ngưỡng An Toàn Sinh Học 12 Tháng Tại Yên Thành
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Bảng dữ liệu chuẩn hóa 12 tháng
        df_yt = dl[(dl.year == nam) & (dl.huyen == vung)].sort_values("month")
        rows_khi_hau = []
        for m in range(1, 13):
            sub_m = df_yt[df_yt.month == m]
            r = sub_m.iloc[0] if not sub_m.empty else pd.Series()
            tmax = float(r.get("tmax", 30.0)) if pd.notna(r.get("tmax")) else 30.0
            nong = int(r.get("nong35", 0)) if pd.notna(r.get("nong35")) else 0
            mua = float(r.get("mua_mm", 80.0)) if pd.notna(r.get("mua_mm")) else 80.0
            sm = float(r.get("sm_rootzone", 0.28)) if pd.notna(r.get("sm_rootzone")) else 0.28
            ndvi = float(r.get("ndvi", 0.65)) if pd.notna(r.get("ndvi")) else 0.65

            if m in [1, 2]:
                gd = "Gieo mạ & cấy lúa xuân"
                rr_txt = "❄️ Nguy cơ rét đậm hại mạ" if tmax < 20 else "🟢 Thuận lợi"
            elif m in [3, 4]:
                gd = "Làm đòng & trỗ bông xuân"
                rr_txt = "🔥 Gió Lào T4 táp bông" if nong >= 5 else "🟢 Tối ưu quang hợp"
            elif m == 5:
                gd = "Chín & gặt lúa xuân"
                rr_txt = "🌾 Cần khô ruộng đưa máy gặt"
            elif m in [6, 7]:
                gd = "Cấy & đẻ nhánh hè thu"
                rr_txt = "🔥 Đỉnh nắng hạn gió Lào" if nong >= 7 else "🟡 Cần dâng nước đệm"
            elif m == 8:
                gd = "Trỗ bông lúa hè thu"
                rr_txt = "🌾 Trỗ hè thu cần nước mát"
            elif m in [9, 10]:
                gd = "Gặt hè thu & tránh lũ"
                rr_txt = "🌊 MƯA BÃO LỚN KÊNH VÁCH BẮC" if mua >= 300 else "🟡 Mưa rải rác"
            else:
                gd = "Cày ải phơi nỏ & vụ đông"
                rr_txt = "🚜 Đất khô nỏ diệt mầm nấm"

            rows_khi_hau.append({
                "Tháng": f"Tháng {m}",
                "Giai Đoạn Nông Học": gd,
                "Tmax (°C)": f"{tmax:.1f}",
                "Gió Lào ≥35°C": f"{nong} ngày",
                "Mưa GPM (mm)": f"{mua:.0f}",
                "Độ Ẩm SMAP": f"{sm*100:.0f}%",
                "Sinh Khối NDVI": f"{ndvi:.2f}",
                "Cảnh Báo Viễn Thám": rr_txt,
            })

        st.dataframe(pd.DataFrame(rows_khi_hau), use_container_width=True, hide_index=True)
