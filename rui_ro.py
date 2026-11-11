import pandas as pd

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)

NGUONG_DOC = 0.30   # tỷ lệ diện tích dốc >15° để coi là huyện đồi núi (tạm, chỉnh theo bảng in ra)
NGUONG_NONG = 3     # số ngày >=35°C trung bình mỗi tháng (11 năm) để coi là tháng gió Lào

bang = pd.read_csv("data/processed/bang_huyen_thang.csv", parse_dates=["thang"])

def z(s):
    return (s - s.mean()) / s.std()

g = bang.groupby("huyen")

# Nhánh 1: khô nóng, hai nguồn độc lập
bang["chi_so_han_nong"] = g["lst_c"].transform(z) - g["sm_rootzone"].transform(z)
bang["nong_ve_tinh"] = bang["chi_so_han_nong"] > 1.0
bang["nong_power"] = bang["nong35_tb11nam"] >= NGUONG_NONG
bang["muc_kho_nong"] = bang["nong_ve_tinh"].astype(int) + bang["nong_power"].astype(int)  # 0, 1, 2
bang["nhanh1_kho_han"] = bang["muc_kho_nong"] >= 1

# Nhánh 2 và 3: mưa lớn, tách theo địa hình
la_doi_nui = bang["ty_le_doc_tren_15"] >= NGUONG_DOC
bang["nhanh2_xoi_mon"] = la_doi_nui & (bang["mua_mm"] > 180)
bang["nhanh3_ung_ngap"] = (~la_doi_nui) & (bang["mua_mm"] > 400)

bang.to_csv("data/processed/rui_ro_huyen_thang.csv", index=False)

# ---- In kết quả ----
print("Tỷ lệ diện tích dốc >15° mỗi huyện (để kiểm tra ngưỡng NGUONG_DOC):")
print(bang.groupby("huyen")["ty_le_doc_tren_15"].first().round(2))
print()
for huyen, d in bang.groupby("huyen"):
    print(huyen)
    print("  khô nóng (vệ tinh) :", d.loc[d["nong_ve_tinh"], "thang_so"].tolist())
    print("  nóng (POWER)       :", d.loc[d["nong_power"], "thang_so"].tolist())
    print("  hai nguồn cùng báo :", d.loc[d["muc_kho_nong"] == 2, "thang_so"].tolist())
    print("  xói mòn            :", d.loc[d["nhanh2_xoi_mon"], "thang_so"].tolist())
    print("  úng ngập           :", d.loc[d["nhanh3_ung_ngap"], "thang_so"].tolist())