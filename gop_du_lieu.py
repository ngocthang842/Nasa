import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)

def doc(ten_file, ten_cot, cach):
    """Đọc file chuỗi thời gian từ GEE, gộp theo (huyện, tháng)."""
    df = pd.read_csv(RAW / f"{ten_file}.csv")[["huyen", "date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["thang"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df.groupby(["huyen", "thang"])["value"].agg(cach).rename(ten_cot)

# Thực vật: max trong tháng (ảnh đã lọc mây)
ndvi = doc("ndvi_qa_2025", "ndvi", "max")
evi = doc("evi_qa_2025", "evi", "max")
lai = doc("lai_qa_2025", "lai", "max")
# Khí hậu, đất: trung bình. Mưa, bốc thoát hơi: cộng dồn
lst = doc("lst_2025", "lst_c", "mean")
sm_re = doc("smap_rootzone_2025", "sm_rootzone", "mean")
sm_mat = doc("smap_surface_2025", "sm_surface", "mean")
mua = doc("mua_2025", "mua_mm", "sum")
et = doc("et_2025", "et_mm", "sum")
pet = doc("pet_2025", "pet_mm", "sum")

bang = pd.concat([ndvi, evi, lai, lst, mua, et, pet, sm_re, sm_mat], axis=1).reset_index()
bang["thang_so"] = bang["thang"].dt.month
bang["esi"] = bang["et_mm"] / bang["pet_mm"]              # thấp = cây thiếu nước
bang["nuoc_con_lai_mm"] = bang["mua_mm"] - bang["et_mm"]  # cân bằng nước đơn giản

# ---- Gộp dữ liệu NASA POWER: số ngày nóng (Tmax >= 35°C) ----
TEN_FILE = {"Yen Thanh": "Yen_Thanh", "Nghi Loc": "Nghi_Loc", "Con Cuong": "Con_Cuong"}
rows = []
for ten, f in TEN_FILE.items():
    p = pd.read_csv(RAW / f"power_{f}.csv", parse_dates=["date"]).set_index("date")
    nong = p["T2M_MAX"].ge(35)
    tb11 = nong.groupby([p.index.year, p.index.month]).sum().groupby(level=1).mean()
    p25 = p.loc["2025"]
    n25 = p25["T2M_MAX"].ge(35).groupby(p25.index.month).sum()
    tmax25 = p25["T2M_MAX"].groupby(p25.index.month).max()
    rh25 = p25["RH2M"].groupby(p25.index.month).mean()
    for t in range(1, 13):
        rows.append({
            "huyen": ten, "thang_so": t,
            "nong35_2025": int(n25.get(t, 0)),
            "nong35_tb11nam": round(float(tb11.get(t, 0)), 1),
            "tmax_2025": round(float(tmax25.get(t, float("nan"))), 1),
            "rh_2025": round(float(rh25.get(t, float("nan"))), 1),
        })
bang = bang.merge(pd.DataFrame(rows), on=["huyen", "thang_so"], how="left")

# ---- Bảng tĩnh theo huyện: địa hình, lớp phủ, đất ----
dem = pd.read_csv(RAW / "dem_slope_v2.csv").rename(columns={
    "ADM2_NAME": "huyen", "elevation": "do_cao_m", "slope": "do_doc_do"})
lc = pd.read_csv(RAW / "landcover.csv").rename(columns={"ADM2_NAME": "huyen"})
dat = pd.read_csv(RAW / "dat.csv").rename(columns={"ADM2_NAME": "huyen"})
for t in (dem, lc, dat):
    bang = bang.merge(t, on="huyen", how="left")

bang.to_csv(OUT / "bang_huyen_thang.csv", index=False)

# ---- Kiểm tra ----
print("Kích thước:", bang.shape, "(kỳ vọng 36 dòng)")
print("\nSố ô bị thiếu mỗi cột:")
print(bang.isna().sum()[lambda s: s > 0])
print("\nNDVI theo tháng (đã lọc mây):")
print(bang.pivot(index="thang_so", columns="huyen", values="ndvi").round(2))
print("\nHồ sơ từng huyện:")
cot = ["do_doc_do", "ty_le_doc_tren_5", "ty_le_doc_tren_15", "cay_go", "dat_nong_nghiep",
       "carbon_huu_co_g_kg", "ph", "cat_pct", "set_pct"]
print(bang.groupby("huyen")[cot].first().round(2).T)