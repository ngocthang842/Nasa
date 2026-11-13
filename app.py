"""Cửa vào. Chỉ việc chọn trang và bộ lọc. Nội dung từng trang nằm trong pages/."""
import streamlit as st

import engine as E
from views import cay_vung, du_lieu, luan_canh, so_sanh, tong_quan
from views.chung import CSS

st.set_page_config(page_title="RotaNA", page_icon="🌾", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

TRANG = {
    "Tổng quan": tong_quan.hien,
    "Cây theo vùng": cay_vung.hien,
    "Luân canh": luan_canh.hien,
    "So sánh các năm": so_sanh.hien,
    "Dữ liệu": du_lieu.hien,
}


@st.cache_data(show_spinner=False)
def tai():
    d = E.doc_thang()
    diem = E.bang_diem(d) if len(d) else d
    return d, diem, E.doc_nam(), E.doc_tb()


dl, diem, nam_df, tb_df = tai()

with st.sidebar:
    st.markdown("### RotaNA")
    st.caption("Nghệ An")
    trang = st.radio("Trang", list(TRANG), label_visibility="collapsed")
    st.divider()
    if dl.empty:
        st.error("Không thấy CSV trong data/processed.")
        st.stop()
    years = sorted(dl.year.unique())
    nam = st.selectbox("Năm", years, index=len(years) - 1)
    co = sorted(dl[dl.year == nam].month.unique())
    thang = st.select_slider("Tháng", options=co, value=4 if 4 in co else co[-1], format_func=lambda m: f"Tháng {m}")
    huyens = sorted(dl.huyen.unique())
    vung = st.selectbox("Vùng", huyens, format_func=lambda h: f"{h} ({E.VUNG[h]})" if h in E.VUNG else h)
    st.caption("Năm có số: " + ", ".join(map(str, years)))

cur = dl[(dl.year == nam) & (dl.month == thang) & (dl.huyen == vung)]
if cur.empty:
    st.warning(f"Chưa có dữ liệu tháng {thang}/{nam} cho {vung}.")
    st.stop()

ctx = dict(dl=dl, diem=diem, nam_df=nam_df, tb_df=tb_df, nam=nam, thang=thang, vung=vung,
           years=years, huyens=huyens, r=cur.iloc[0])
TRANG[trang](ctx)
