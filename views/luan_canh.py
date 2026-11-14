"""Trang luân canh."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine as E
from views.chung import tieu_de, ve


def _g(r, k, mac=0):
    if k not in r or pd.isna(r[k]):
        return mac
    return r[k]


def hien(ctx):
    r = ctx["r"]
    thang, vung, nam = ctx["thang"], ctx["vung"], ctx["nam"]
    tieu_de(vung, thang, nam, "Luân canh", len(ctx["years"]) < 2)
    with st.container(border=True):
        st.markdown(f'<p class="cap">Gợi ý tháng {thang}</p>', unsafe_allow_html=True)
        loi = []
        if _g(r, "muc_kho_nong") >= 1 or _g(r, "nuoc_con_lai_mm", 0) < 0:
            loi.append("Nắng nóng hoặc thiếu nước. Lúa đang đứng thì giữ mực nước ruộng khoảng 3–5 cm. Hết nước tưới thì cân nhắc vụ chịu hạn (vừng đen) thay vì để ruộng trống.")
        if _g(r, "nhanh2_xoi_mon"):
            loi.append("Mưa trên đất dốc. Che phủ gốc, trồng xen hoặc làm rãnh ngang để đất khỏi trôi.")
        if _g(r, "nhanh3_ung_ngap") or _g(r, "mua_mm", 0) >= 300:
            loi.append("Dễ úng. Xẻ rãnh thoát quanh bờ trước mưa lớn. Đừng gieo vụ mới những ngày này.")
        if not loi:
            loi.append("Tháng này ít tín hiệu thời tiết xấu. Làm đất và xuống giống theo lịch địa phương.")
        for dong in loi:
            st.success(dong) if "ít tín hiệu" in dong else st.warning(dong)
        st.caption("Gợi ý để tham khảo. Cán bộ khuyến nông địa phương mới chốt được lịch xuống giống.")
    with st.container(border=True):
        st.markdown('<p class="cap">Chọn kịch bản theo việc bạn ưu tiên</p>', unsafe_allow_html=True)
        a, b, c = st.columns(3)
        w = [
            a.slider("Tiết kiệm nước", 0.0, 1.0, .33),
            b.slider("Đất khỏe hơn", 0.0, 1.0, .33),
            c.slider("Thu nhập", 0.0, 1.0, .34),
        ]
        tong = sum(w) or 1
        kq = pd.DataFrame([
            dict(kb=k, diem=round(sum(v[col] * x / tong for col, x in zip(("nuoc", "dat", "kt"), w)), 1))
            for k, v in E.KICH_BAN.items()
        ]).sort_values("diem")
        st.success(f"Hợp với lựa chọn của bạn: {kq.iloc[-1].kb} – {kq.iloc[-1].diem}/100")
        f = go.Figure(go.Bar(x=kq.diem, y=kq.kb, orientation="h", marker_color="#0C6B52"))
        f.update_xaxes(range=[0, 100])
        f.update_layout(height=260, margin=dict(l=8, r=8, t=8, b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        ve(f)
        st.caption("Điểm nước, đất, tiền của từng kịch bản lấy từ thiết kế RotaNA. Thanh trượt chỉ đổi trọng số, không đổi số liệu thời tiết.")