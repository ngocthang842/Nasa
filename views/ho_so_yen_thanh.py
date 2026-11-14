"""Hồ sơ Nông nghiệp & Dữ liệu Chuyên sâu Vựa lúa Huyện Yên Thành (Nghệ An).
Thiết kế đồ họa trực quan (Visual Cards & Badges - No Walls of Text).
"""
import streamlit as st


def hien(ctx):
    # BANNER TIÊU ĐỀ HỒ SƠ YÊN THÀNH
    st.markdown(
        """
        <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:14px; padding:18px 22px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <div style="font-size:11px; font-weight:750; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">
                        🏛️ HỒ SƠ VỰA LÚA TRỌNG ĐIỂM SỐ 1 XỨ NGHỆ
                    </div>
                    <div style="font-size:24px; font-weight:800; color:#0F172A; letter-spacing:-0.5px; margin-top:3px;">
                        Huyện Yên Thành — Trung Tâm Lúa Gạo Chất Lượng Cao
                    </div>
                    <div style="font-size:12.5px; color:#475569; margin-top:3px;">
                        Cánh đồng lớn thâm canh ứng dụng công nghệ viễn thám NASA (MODIS, SMAP, GPM) và thủy nông Ba Ra Đô Lương.
                    </div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:8px 16px; text-align:right;">
                    <div style="font-size:11px; font-weight:700; color:#64748B;">DIỆN TÍCH TỰ NHIÊN</div>
                    <div style="font-size:18px; font-weight:800; color:#0F172A;">549,93 km²</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 THẺ SỐ LIỆU HERO VỀ NÔNG NGHIỆP YÊN THÀNH
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:10px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:11px; font-weight:750; color:#64748B;">🌾 DIỆN TÍCH GIEO CẤY LÚA</div>
                <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">~26.500 ha</div>
                <div style="font-size:11px; color:#16A34A; font-weight:700;">Lớn nhất tỉnh Nghệ An</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #0EA5E9; border-radius:10px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:11px; font-weight:750; color:#64748B;">⚖️ TỔNG SẢN LƯỢNG LÚA</div>
                <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">> 155.000 tấn</div>
                <div style="font-size:11px; color:#0EA5E9; font-weight:700;">Đóng góp 13–15% toàn tỉnh</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #8B5CF6; border-radius:10px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:11px; font-weight:750; color:#64748B;">📊 NĂNG SUẤT BÌNH QUÂN</div>
                <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">65 – 72 tạ/ha</div>
                <div style="font-size:11px; color:#8B5CF6; font-weight:700;">Dẫn đầu đồng bằng xứ Nghệ</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #F59E0B; border-radius:10px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:11px; font-weight:750; color:#64748B;">💧 ĐỘ PHỦ TƯỚI TỰ CHẢY</div>
                <div style="font-size:22px; font-weight:800; color:#0F172A; margin:2px 0;">90 – 95%</div>
                <div style="font-size:11px; color:#D97706; font-weight:700;">Hệ thống Ba Ra Đô Lương</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    cot_trai, cot_phai = st.columns([1, 1], gap="medium")

    with cot_trai:
        # KHỐI 1: ĐẶC ĐIỂM ĐỊA LÝ & THỔ NHƯỠNG (CARD ĐỒ HỌA)
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:10px;">🗺️ Đặc điểm Địa lý & Thổ nhưỡng Ruộng Lúa</div>',
                unsafe_allow_html=True,
            )
            cac_dac_diem = [
                ("Địa hình Lòng chảo Bán sơn địa", "Lòng chảo bằng phẳng được bao bọc bởi dải đồi bát úp phía Tây, tiểu khí hậu đồng ruộng ổn định, che chắn bão biển.", "⛰️", "#0F172A", "Tiểu khí hậu ổn định"),
                ("Thổ nhưỡng Phù sa Sông Dinh & Glây hóa", "Thịt pha sét màu mỡ, tầng canh tác dày >25cm, pH 5.2–6.2, khả năng giữ nước và phân bón tuyệt hảo cho lúa nước.", "🌱", "#16A34A", "Độ phì nhiêu cao"),
                ("Mạng lưới Tiêu thoát Lũ Kênh Vách Bắc", "Trục sông Dinh, sông Đào và Kênh Vách Bắc thoát lũ ra biển Diễn Châu, giải cứu vùng trũng lòng chảo mùa bão lũ tháng 9.", "🌊", "#0284C7", "Trục thoát lũ biển"),
            ]
            for tieu_de_dd, mota_dd, ic_dd, col_dd, tag_dd in cac_dac_diem:
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:3.5px solid {col_dd}; border-radius:8px; padding:8px 12px; margin-bottom:8px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12.5px; font-weight:800; color:#0F172A;">{ic_dd} {tieu_de_dd}</span>
                        <span style="font-size:10.5px; font-weight:750; color:{col_dd}; background:#FFFFFF; border:1px solid #CBD5E1; border-radius:999px; padding:1px 8px;">{tag_dd}</span>
                      </div>
                      <div style="font-size:11.5px; color:#475569; margin-top:3px; line-height:1.4;">{mota_dd}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # KHỐI 2: ĐẠI THỦY NÔNG BA RA ĐÔ LƯƠNG
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:10px;">💧 Đại Thủy nông Ba Ra Đô Lương & Điều tiết Nước</div>',
                unsafe_allow_html=True,
            )
            cac_thuy_loi = [
                ("Cống Đầu Mối Ba Ra Đô Lương", "Công trình đại thủy nông ngăn sông Lam, cung cấp 85–90% nguồn nước tưới phù sa ngọt cho 26.500 ha lúa Yên Thành.", "🌊", "#0284C7", "Đầu mối cấp nước"),
                ("Trục Kênh Chính & Kênh Cấp 1", "Dẫn nước tự chảy qua cống Nam Đàn về các cụm phân phối tại Bảo Thành, Hoa Thành, Tăng Thành không cần trạm bơm.", "💧", "#0284C7", "Tưới tự chảy 95%"),
                ("Hệ thống Hồ Đập Bán sơn địa", "Các hồ chứa nội đồng (Hồ Vực Mấu, đập thủy lợi địa phương) bổ trợ nguồn nước tưới luân phiên cho chân ruộng vàn cao.", "⛰️", "#D97706", "Trữ ẩm hồ đập"),
            ]
            for tieu_de_tl, mota_tl, ic_tl, col_tl, tag_tl in cac_thuy_loi:
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:3.5px solid {col_tl}; border-radius:8px; padding:8px 12px; margin-bottom:8px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12.5px; font-weight:800; color:#0F172A;">{ic_tl} {tieu_de_tl}</span>
                        <span style="font-size:10.5px; font-weight:750; color:{col_tl}; background:#FFFFFF; border:1px solid #CBD5E1; border-radius:999px; padding:1px 8px;">{tag_tl}</span>
                      </div>
                      <div style="font-size:11.5px; color:#475569; margin-top:3px; line-height:1.4;">{mota_tl}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with cot_phai:
        # KHỐI 3: CƠ CẤU MÙA VỤ & GIỐNG LÚA CHỦ LỰC
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:10px;">🌾 Cơ cấu Mùa vụ & Giống Lúa Khuyến nghị</div>',
                unsafe_allow_html=True,
            )
            cac_vu = [
                ("Vụ Chiêm Xuân (T1 – T5)", "Vụ lúa chính số 1. Gieo mạ cuối T12–T1, trỗ rộ 20/4–5/5, thu hoạch dứt điểm trước 25/5.", "🌾", "#16A34A", "ST25, J02, TBR225"),
                ("Vụ Lúa Hè Thu (T6 – T9)", "Vụ mùa chạy lụt né lũ tiểu mãn. Xuống giống trước 10/6, trỗ đầu T8, gặt gọn trước ngày 15/9.", "☀️", "#D97706", "Khang Dân 18, Đài Thơm 8"),
                ("Vụ Đông & Cày Phơi Ải (T10 – T12)", "Cày lật phơi nỏ đất 30–45 ngày diệt mầm nấm bệnh. Xen canh Ngô ngọt, Lạc thu đông chân vàn cao.", "🍂", "#0284C7", "Lạc L14, Ngô NK4300"),
            ]
            for tieu_de_v, mota_v, ic_v, col_v, giong_v in cac_vu:
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:3.5px solid {col_v}; border-radius:8px; padding:8px 12px; margin-bottom:8px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12.5px; font-weight:800; color:#0F172A;">{ic_v} {tieu_de_v}</span>
                        <span style="font-size:10.5px; font-weight:750; color:#0F172A; background:#FFFFFF; border:1px solid #CBD5E1; border-radius:999px; padding:1px 8px;">{giong_v}</span>
                      </div>
                      <div style="font-size:11.5px; color:#475569; margin-top:3px; line-height:1.4;">{mota_v}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # KHỐI 4: 4 NGUỒN VIỄN THÁM VỆ TINH NASA
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:15px; font-weight:800; color:#0F172A; margin-bottom:10px;">🛰️ 4 Nguồn Dữ liệu Viễn thám & Khí tượng NASA</div>',
                unsafe_allow_html=True,
            )
            cac_ve_tinh = [
                ("NASA POWER", "Giám sát nhiệt độ tối cao Tmax, bức xạ mặt trời và nhận diện sớm các đợt gió Lào Tây Nam ≥35°C.", "🌡️", "#DC2626", "Tmax & Gió Lào"),
                ("NASA GPM (IMERG)", "Đo đạc lượng mưa vệ tinh tích lũy độ phân giải cao 0.1°, cảnh báo nguy cơ ngập úng và hạn hán.", "🌧️", "#0284C7", "Radar Mưa Vệ tinh"),
                ("NASA SMAP", "Đo độ ẩm đất tầng mặt (0–5cm) và tầng rễ (0–100cm), xác định lịch tưới dưỡng và tháo cạn phơi ruộng.", "💧", "#10B981", "Độ ẩm Đất Tầng rễ"),
                ("MODIS / Sentinel-2", "Cung cấp chỉ số thực vật NDVI đánh giá sức sống, độ che phủ và sinh khối lúa qua từng tuần.", "🌿", "#16A34A", "Độ xanh Lúa NDVI"),
            ]
            for ten_vt, mota_vt, ic_vt, col_vt, tag_vt in cac_ve_tinh:
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:3.5px solid {col_vt}; border-radius:8px; padding:8px 12px; margin-bottom:8px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12.5px; font-weight:800; color:#0F172A;">{ic_vt} {ten_vt}</span>
                        <span style="font-size:10.5px; font-weight:750; color:{col_vt}; background:#FFFFFF; border:1px solid #CBD5E1; border-radius:999px; padding:1px 8px;">{tag_vt}</span>
                      </div>
                      <div style="font-size:11.5px; color:#475569; margin-top:3px; line-height:1.4;">{mota_vt}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

