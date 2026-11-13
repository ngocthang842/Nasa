"""So sánh các năm."""
import plotly.graph_objects as go
import streamlit as st

from views.chung import tieu_de, ve


def hien(ctx):
    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang, vung, years = ctx["nam"], ctx["thang"], ctx["vung"], ctx["years"]
    tieu_de(vung, thang, nam, "So sánh năm", len(years) < 2)
    CH = {
        "Nhiệt độ cao nhất": "tmax", "Mưa": "mua_mm", "Ngày ≥ 35°C": "nong35",
        "Độ ẩm đất": "sm_rootzone", "NDVI": "ndvi", "Cân bằng nước": "nuoc_con_lai_mm",
    }
    with st.container(border=True):
        st.markdown('<p class="cap">Một năm, theo tháng</p>', unsafe_allow_html=True)
        chon = st.radio("Chỉ số", list(CH), horizontal=True, label_visibility="collapsed")
        cot = CH[chon]
        f = go.Figure()
        for y in years:
            q = dl[(dl.huyen == vung) & (dl.year == y)].sort_values("month")
            if cot not in q.columns:
                continue
            f.add_scatter(
                x=[f"T{int(m)}" for m in q.month], y=q[cot], name=str(y), mode="lines+markers",
                line=dict(width=3, color="#0C6B52" if y == nam else "#94A3B8"),
            )
        f.update_layout(height=380, margin=dict(l=8, r=8, t=8, b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        legend=dict(orientation="h", y=1.08))
        ve(f)
        if len(years) < 2:
            st.caption(f"Hiện mới có năm {years[0]}. Thêm năm sau sẽ là một đường nữa trên cùng biểu đồ này.")
    if len(diem):
        with st.container(border=True):
            st.markdown(f'<p class="cap">Mức cây ở tháng {thang}</p>', unsafe_allow_html=True)
            q = diem[(diem.huyen == vung) & (diem.month == thang)].pivot(index="cay", columns="year", values="muc")
            q.index.name = "Cây"
            st.dataframe(q, use_container_width=True)