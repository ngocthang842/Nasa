from datetime import date
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os

st.set_page_config(page_title="RotaNA", page_icon="🌾", layout="wide")

TEN = {"Yen Thanh": "Yên Thành", "Nghi Loc": "Nghi Lộc", "Con Cuong": "Con Cuông"}
VUNG = {"Yen Thanh": "đồng bằng chuyên lúa", "Nghi Loc": "ven biển, đất pha cát",
        "Con Cuong": "đồi núi"}


@st.cache_data
def tai_du_lieu():
    return pd.read_csv("data/processed/rui_ro_huyen_thang.csv", parse_dates=["thang"])


bang = tai_du_lieu()

# ==========================================
# SIDEBAR: CHỌN HUYỆN, THÁNG VÀ TRỌNG SỐ KỊCH BẢN
# ==========================================
st.sidebar.title("🌾 RotaNA")
huyen = st.sidebar.selectbox("Chọn huyện", list(TEN),
                             format_func=lambda h: f"{TEN[h]} ({VUNG[h]})")
thang = st.sidebar.select_slider("Xem tháng", options=list(range(1, 13)),
                                 value=date.today().month,
                                 format_func=lambda t: f"Tháng {t}")

st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Trọng số ưu tiên")
st.sidebar.caption("Kéo thanh trượt để hệ thống chấm điểm kịch bản luân canh phù hợp với mục tiêu của bạn.")
w_nuoc = st.sidebar.slider("Ưu tiên Tiết kiệm nước", 0.0, 1.0, 0.33)
w_dat = st.sidebar.slider("Ưu tiên Sức khỏe đất", 0.0, 1.0, 0.33)
w_kt = st.sidebar.slider("Ưu tiên Kinh tế", 0.0, 1.0, 0.34)

# Chuẩn hóa trọng số để tổng = 1.0
tong_w = w_nuoc + w_dat + w_kt
if tong_w > 0:
    w_nuoc, w_dat, w_kt = w_nuoc / tong_w, w_dat / tong_w, w_kt / tong_w

d = bang[bang["huyen"] == huyen].sort_values("thang_so").reset_index(drop=True)
hien = d[d["thang_so"] == thang].iloc[0]
doi_nui = bool(d["nhanh2_xoi_mon"].any())

# ==========================================
# PHẦN 1: TIÊU ĐỀ VÀ BẢN ĐỒ RANH GIỚI
# ==========================================
st.title(f"Huyện {TEN[huyen]}: tình hình tháng {thang}")
st.caption("Số liệu vệ tinh NASA năm 2025. Chỉ để tham khảo, cần hỏi thêm cán bộ khuyến nông địa phương.")

st.subheader("🗺️ Bản đồ khu vực nghiên cứu")
geojson_path = "data/raw/ranh_gioi_huyen.geojson"
if os.path.exists(geojson_path):
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    m = folium.Map(location=[19.0, 105.0], zoom_start=9, tiles="CartoDB positron")


    # Style: Huyện đang chọn tô xanh đậm, các huyện khác làm mờ
    def style_function(feature):
        ten_huyen = feature['properties'].get('ADM2_NAME', '')
        if ten_huyen == huyen:
            return {'fillColor': '#2E7D32', 'color': '#1F2A1F', 'weight': 3, 'fillOpacity': 0.6}
        else:
            return {'fillColor': '#CCCCCC', 'color': '#999999', 'weight': 1, 'fillOpacity': 0.2}


    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['ADM2_NAME'], aliases=['Huyện:'])
    ).add_to(m)

    st_folium(m, height=350, use_container_width=True)
else:
    st.warning("Không tìm thấy file ranh giới (ranh_gioi_huyen.geojson).")


# ==========================================
# PHẦN 2: CÁC THẺ TRẠNG THÁI (ĐÈN GIAO THÔNG)
# ==========================================
def the(tieu_de, noi_dung, phu, mau):
    return (f'<div style="background:{mau};padding:16px 18px;border-radius:14px;'
            f'color:white;min-height:120px">'
            f'<div style="font-size:15px;opacity:.9">{tieu_de}</div>'
            f'<div style="font-size:24px;font-weight:700;margin:4px 0">{noi_dung}</div>'
            f'<div style="font-size:14px;opacity:.9">{phu}</div></div>')


if hien["muc_kho_nong"] == 2:
    nong = ("Rất nóng, đất khô", "#C62828")
elif hien["muc_kho_nong"] == 1:
    nong = ("Nắng nóng", "#EF6C00")
else:
    nong = ("Bình thường", "#2E7D32")
ngay_nong = f"Trung bình {hien['nong35_tb11nam']:.0f} ngày/tháng có nắng từ 35°C (11 năm)"

mm = hien["mua_mm"]
if hien["nhanh3_ung_ngap"]:
    mua = ("Mưa rất lớn, dễ úng", "#1565C0")
elif hien["nhanh2_xoi_mon"]:
    mua = ("Mưa lớn, dễ xói mòn", "#6D4C41")
elif mm < 50:
    mua = ("Ít mưa", "#F57F17")
elif mm < 200:
    mua = ("Mưa vừa", "#2E7D32")
else:
    mua = ("Mưa nhiều", "#0277BD")

sm = hien["sm_rootzone"] * 100
q25, q75 = (d["sm_rootzone"].quantile([0.25, 0.75]) * 100).tolist()
if sm <= q25:
    dat = ("Đất khá khô", "#EF6C00")
elif sm >= q75:
    dat = ("Đất rất ẩm", "#0277BD")
else:
    dat = ("Đất đủ ẩm", "#2E7D32")

c1, c2, c3 = st.columns(3)
c1.markdown(the("☀️ Nắng nóng", nong[0], ngay_nong, nong[1]), unsafe_allow_html=True)
c2.markdown(the("🌧️ Lượng mưa", mua[0], f"{mm:.0f} mm trong tháng", mua[1]), unsafe_allow_html=True)
c3.markdown(the("🌱 Nước trong đất", dat[0], f"Độ ẩm vùng rễ khoảng {sm:.0f}%", dat[1]),
            unsafe_allow_html=True)

# ==========================================
# PHẦN 3: LỊCH RỦI RO VÀ BIỂU ĐỒ CHI TIẾT
# ==========================================
st.subheader("Lịch rủi ro 12 tháng")
hang = ["Nắng nóng, đất khô", "Mưa lớn, xói mòn", "Mưa rất lớn, úng ngập"]
z = [d["muc_kho_nong"].tolist(),
     (d["nhanh2_xoi_mon"].astype(int) * 2).tolist(),
     (d["nhanh3_ung_ngap"].astype(int) * 2).tolist()]

lich = go.Figure(go.Heatmap(
    z=z, x=d["thang_so"], y=hang, zmin=0, zmax=2,
    colorscale=[[0, "#A5D6A7"], [0.5, "#FFB74D"], [1, "#E53935"]],
    showscale=False, xgap=4, ygap=4, hovertemplate="Tháng %{x}<extra></extra>"))
lich.add_vrect(x0=thang - 0.5, x1=thang + 0.5, line_color="#1F2A1F",
               line_width=3, fillcolor="rgba(0,0,0,0)")
lich.update_layout(
    template="plotly_white", height=230, margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
               ticktext=[f"T{t}" for t in range(1, 13)], side="top"),
    yaxis=dict(autorange="reversed"))
st.plotly_chart(lich)
st.caption("🟢 an toàn · 🟠 cần chú ý · 🔴 rủi ro cao. Khung đen là tháng đang xem.")

st.subheader("Mưa, nắng nóng và nước trong đất")


def dinh_dang(fig, tieu_de):
    fig.update_layout(
        template="plotly_white", title=tieu_de, height=320, showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
                   ticktext=[f"T{t}" for t in range(1, 13)]))
    return fig


def mau_cot(dam, nhat):
    return [dam if t == thang else nhat for t in d["thang_so"]]


f1 = go.Figure(go.Bar(x=d["thang_so"], y=d["mua_mm"], marker_color=mau_cot("#1565C0", "#90CAF9")))
nguong, nhan = (180, "Mưa lớn (trên 180 mm)") if doi_nui else (400, "Mưa rất lớn (trên 400 mm)")
f1.add_hline(y=nguong, line_dash="dash", line_color="#C62828", annotation_text=nhan)
dinh_dang(f1, "Mưa mỗi tháng (mm)")

f2 = go.Figure()
f2.add_bar(x=d["thang_so"], y=d["nong35_tb11nam"], name="Trung bình 11 năm",
           marker_color=mau_cot("#EF6C00", "#FFCC80"))
f2.add_scatter(x=d["thang_so"], y=d["nong35_2025"], mode="markers", name="Năm 2025",
               marker=dict(symbol="diamond", size=10, color="#B71C1C"))
dinh_dang(f2, "Số ngày nắng từ 35°C mỗi tháng")
f2.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15))

f3 = go.Figure(go.Scatter(
    x=d["thang_so"], y=d["sm_rootzone"] * 100, mode="lines+markers", fill="tozeroy",
    line=dict(color="#6D4C41", width=3),
    marker=dict(size=[14 if t == thang else 7 for t in d["thang_so"]])))
f3.update_yaxes(range=[0, d["sm_rootzone"].max() * 130])
dinh_dang(f3, "Độ ẩm đất vùng rễ (%)")

k1, k2, k3 = st.columns(3)
k1.plotly_chart(f1)
k2.plotly_chart(f2)
k3.plotly_chart(f3)

# ==========================================
# PHẦN 4: SO SÁNH KỊCH BẢN LUÂN CANH
# ==========================================
st.subheader("🌾 So sánh các kịch bản luân canh")
st.caption("Dựa trên số liệu từ Báo cáo Thiết kế RotaNA (Mục 6). Điểm số thay đổi theo thanh trượt trọng số bên trái.")

kịch_bản = {
    "KB 0: Độc canh (Lúa - Trồng - Lúa)": {"nuoc": 35, "dat": 42, "kt": 28, "mau": "#9E9E9E"},
    "KB 1: Ưu tiên đất (Lúa - Đậu xanh - Lúa)": {"nuoc": 48, "dat": 78, "kt": 45, "mau": "#4CAF50"},
    "KB 2: Chịu hạn (Lúa - Vừng đen - Lúa)": {"nuoc": 30, "dat": 80, "kt": 52, "mau": "#2196F3"},
    "KB 3: Đa dạng kinh tế (Gia vị - Đậu đen - Ngô)": {"nuoc": 45, "dat": 68, "kt": 68, "mau": "#FF9800"}
}

ket_qua = []
for ten_kb, diem in kịch_bản.items():
    tong_diem = (diem["nuoc"] * w_nuoc) + (diem["dat"] * w_dat) + (diem["kt"] * w_kt)
    ket_qua.append({"Kịch bản": ten_kb, "Điểm tổng": round(tong_diem, 1), "Màu": diem["mau"]})

df_kq = pd.DataFrame(ket_qua).sort_values("Điểm tổng", ascending=True)  # Sắp xếp tăng dần để vẽ biểu đồ ngang

best = df_kq.iloc[-1]  # Lấy kịch bản điểm cao nhất
st.success(f"**🏆 Kịch bản tối ưu cho mục tiêu của bạn là:** {best['Kịch bản']} (Điểm: {best['Điểm tổng']}/100)")

fig_kb = go.Figure(go.Bar(
    x=df_kq["Điểm tổng"], y=df_kq["Kịch bản"], orientation='h',
    marker_color=df_kq["Màu"], text=df_kq["Điểm tổng"], textposition="outside"
))
fig_kb.update_layout(
    template="plotly_white", height=280,
    xaxis=dict(title="Điểm tổng (0-100)", range=[0, 100]),
    margin=dict(l=10, r=40, t=10, b=10)
)
st.plotly_chart(fig_kb, use_container_width=True)

# ==========================================
# PHẦN 5: GỢI Ý CANH TÁC (TẬP TRUNG VÀO LÚA)
# ==========================================
st.subheader(f"Gợi ý canh tác cho tháng {thang}")
loi = []

if hien["muc_kho_nong"] >= 1:
    loi.append(("warning",
                "**🔥 Nắng nóng, đất khô hạn.** Nếu đang canh tác lúa (Kịch bản 0), cần giữ mực nước ruộng 3-5cm để làm mát gốc cây, tránh hiện tượng lem lép hạt. Nếu thiếu nước tưới, cân nhắc chuyển sang Kịch bản 2 (Trồng Vừng đen chịu hạn) để tiết kiệm 45% nước."))

if hien["nhanh2_xoi_mon"]:
    loi.append(("warning",
                "**⛰️ Mưa lớn trên đất dốc.** Đất dễ bị rửa trôi. Khuyến cáo áp dụng Kịch bản 1 (Luân canh Lúa - Đậu xanh) để thảm lá đậu che phủ đất, giảm 85% lượng đất xói mòn so với việc để đất trống."))

if hien["nhanh3_ung_ngap"]:
    loi.append(("error",
                "**🌊 Nguy cơ úng ngập.** Đối với ruộng lúa, cần chủ động xẻ rãnh thoát nước sâu 20cm quanh bờ thửa trước khi mưa lớn. Tuyệt đối không gieo hạt vụ mới trong giai đoạn này."))

if not loi:
    loi.append(("success",
                "**✅ Tháng này ít rủi ro khí hậu.** Thuận lợi để làm đất và xuống giống lúa vụ mới theo lịch mùa vụ của địa phương."))

for loai, nd in loi:
    getattr(st, loai)(nd)
st.caption("Gợi ý chung mang tính tham khảo, cần cán bộ khuyến nông địa phương xác nhận.")

# ==========================================
# PHẦN 6: CÔNG THỨC KHOA HỌC & NGUỒN SỐ LIỆU
# ==========================================
with st.expander("🔬 Xem chi tiết các công thức khoa học đã tính toán"):
    st.markdown("""
    Hệ thống đã tự động tính toán các chỉ số sau từ dữ liệu vệ tinh NASA:

    **1. Chỉ số căng thẳng bốc thoát hơi nước (ESI - Evaporative Stress Index):**
    *Công thức:* `ESI = ET / PET`
    *Giải thích:* ET là lượng nước cây thực sự thoát ra (từ MODIS), PET là lượng nước tiềm năng có thể thoát (dựa trên thời tiết). ESI càng thấp, cây càng thiếu nước.
    """)

    esi_thang = hien['esi']
    st.info(
        f"👉 **Kết quả tháng {thang} tại {TEN[huyen]}:** ESI = {esi_thang:.2f} (Nếu < 0.5 là cây bị stress nước nghiêm trọng).")

    st.markdown("""
    **2. Cân bằng nước đơn giản (Water Balance):**
    *Công thức:* `Nước còn lại = Tổng mưa (GPM) - Tổng bốc thoát hơi (ET)`
    """)

    nuoc_con_lai = hien['nuoc_con_lai_mm']
    st.info(
        f"👉 **Kết quả tháng {thang}:** Mưa {hien['mua_mm']:.0f}mm - ET {hien['et_mm']:.0f}mm = **{nuoc_con_lai:.0f} mm** (Nếu âm nghĩa là cây phải hút nước ngầm hoặc cần tưới thêm).")

    st.markdown("""
    **3. Điểm đánh giá đa mục tiêu (Multi-Objective Scoring - Mục 4.2 trong Báo cáo):**
    *Công thức:* `Score = (W_water × S_water) + (W_soil × S_soil) + (W_profit × S_profit)`
    *Giải thích:* Hệ thống dùng công thức này để chấm điểm 4 kịch bản luân canh ở thanh trượt bên trái.
    """)

with st.expander("Số liệu này lấy từ đâu?"):
    st.markdown(
        "- **Mưa:** NASA GPM IMERG (cộng dồn theo tháng)\n"
        "- **Nhiệt bề mặt đất và độ ẩm vùng rễ:** MODIS và NASA SMAP (trung bình tháng)\n"
        "- **Số ngày nắng từ 35°C:** NASA POWER, 2015-2025. Yên Thành và Nghi Lộc nằm cùng một ô lưới "
        "POWER (~50 km) nên số liệu này giống nhau\n"
        "- **Ngưỡng cảnh báo:** là ngưỡng tương đối do nhóm đặt dựa trên dữ liệu từng huyện, "
        "không phải tiêu chuẩn chính thức")