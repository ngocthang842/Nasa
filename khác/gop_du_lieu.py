import sys
import pandas as pd
from pathlib import Path

NAM = int(sys.argv[1]) if len(sys.argv) > 1 else 2025

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)


def _doc_tho(ten_file):
    file_path = RAW / f"{ten_file}.csv"

    # Kiểm tra nếu file không tồn tại hoặc quá nhỏ (file rỗng)
    if not file_path.exists() or file_path.stat().st_size < 10:
        print(f"⚠️ Bỏ qua file rỗng hoặc không tồn tại: {file_path.name}")
        return None

    try:
        df = pd.read_csv(file_path)
        # Kiểm tra xem có đủ 3 cột cần thiết không
        if df.empty or not all(c in df.columns for c in ["huyen", "date", "value"]):
            return None

        df = df[["huyen", "date", "value"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        df["thang"] = df["date"].dt.to_period("M").dt.to_timestamp()
        return df
    except Exception as e:
        print(f"⚠️ Lỗi đọc file {file_path.name}: {e}")
        return None


def doc(ten_file, ten_cot, cach):
    """Đọc và gộp theo tháng. Trả về Series rỗng với MultiIndex chuẩn nếu file lỗi."""
    df = _doc_tho(ten_file)
    if df is None:
        # Tạo MultiIndex rỗng để Pandas không bị lỗi khi ghép cột
        idx = pd.MultiIndex.from_arrays([[], []], names=["huyen", "thang"])
        return pd.Series(name=ten_cot, index=idx, dtype='float64')
    return df.groupby(["huyen", "thang"])["value"].agg(cach).rename(ten_cot)


def dem(ten_file, ten_cot):
    """Đếm số ngày có dữ liệu."""
    df = _doc_tho(ten_file)
    if df is None:
        idx = pd.MultiIndex.from_arrays([[], []], names=["huyen", "thang"])
        return pd.Series(name=ten_cot, index=idx, dtype='float64')
    return df.groupby(["huyen", "thang"])["value"].count().rename(ten_cot)


# --- Đọc dữ liệu chuỗi thời gian ---
ndvi = doc(f"ndvi_qa_{NAM}", "ndvi", "max")
evi = doc(f"evi_qa_{NAM}", "evi", "max")
lai = doc(f"lai_qa_{NAM}", "lai", "max")
lst = doc(f"lst_{NAM}", "lst_c", "mean")
sm_re = doc(f"smap_rootzone_{NAM}", "sm_rootzone", "mean")
sm_mat = doc(f"smap_surface_{NAM}", "sm_surface", "mean")
mua = doc(f"mua_{NAM}", "mua_mm", "sum")
et = doc(f"et_{NAM}", "et_mm", "sum")
pet = doc(f"pet_{NAM}", "pet_mm", "sum")
n_mua = dem(f"mua_{NAM}", "n_mua")
n_et = dem(f"et_{NAM}", "n_et")

# --- Ghép dữ liệu ---
bang = pd.concat([ndvi, evi, lai, lst, mua, et, pet, sm_re, sm_mat, n_mua, n_et], axis=1).reset_index()

# Lọc theo năm
bang = bang[bang["thang"].dt.year == NAM].copy()
bang["thang_so"] = bang["thang"].dt.month

# Nếu không có dữ liệu cho năm này, dừng luôn
if bang.empty:
    print(f"\n❌ Không có dữ liệu chuỗi thời gian nào hợp lệ cho năm {NAM}.")
    sys.exit(0)

# Tính các chỉ số (có thể ra NaN nếu thiếu ET/PET)
bang["esi"] = bang["et_mm"] / bang["pet_mm"]
bang["nuoc_con_lai_mm"] = bang["mua_mm"] - bang["et_mm"]

# --- Gộp dữ liệu NASA POWER ---
TEN_FILE = {"Yen Thanh": "Yen_Thanh", "Nghi Loc": "Nghi_Loc", "Con Cuong": "Con_Cuong"}
rows = []
for ten, f in TEN_FILE.items():
    file_power = RAW / f"power_{f}.csv"
    if not file_power.exists(): continue

    p = pd.read_csv(file_power, parse_dates=["date"]).set_index("date")
    nong = p["T2M_MAX"].ge(35)
    tb11 = nong.groupby([p.index.year, p.index.month]).sum().groupby(level=1).mean()
    pn = p.loc[str(NAM)]
    n_nam = pn["T2M_MAX"].ge(35).groupby(pn.index.month).sum()
    tmax_nam = pn["T2M_MAX"].groupby(pn.index.month).max()
    rh_nam = pn["RH2M"].groupby(pn.index.month).mean()
    for t in range(1, 13):
        rows.append({
            "huyen": ten, "thang_so": t,
            f"nong35_{NAM}": int(n_nam.get(t, 0)),
            "nong35_tb11nam": round(float(tb11.get(t, 0)), 1),
            f"tmax_{NAM}": round(float(tmax_nam.get(t, float("nan"))), 1),
            f"rh_{NAM}": round(float(rh_nam.get(t, float("nan"))), 1),
        })
if rows:
    bang = bang.merge(pd.DataFrame(rows), on=["huyen", "thang_so"], how="left")

# --- Gộp dữ liệu Địa hình, Lớp phủ, Đất ---
dem_df = pd.read_csv(RAW / "dem_slope_v2.csv").rename(
    columns={"ADM2_NAME": "huyen", "elevation": "do_cao_m", "slope": "do_doc_do"})
lc = pd.read_csv(RAW / "landcover.csv").rename(columns={"ADM2_NAME": "huyen"})
dat = pd.read_csv(RAW / "dat.csv").rename(columns={"ADM2_NAME": "huyen"})
for t in (dem_df, lc, dat):
    bang = bang.merge(t, on="huyen", how="left")

# --- Loại tháng dở dang ---
# Nếu là năm 2026 (thiếu file ET), n_et sẽ là NaN, ta vẫn giữ lại dữ liệu mưa
du = (bang["n_mua"] >= 25) & ((bang["n_et"] >= 3) | bang["n_et"].isna())

if (~du).any():
    print("\nBỏ các tháng thiếu dữ liệu mưa/ET:")
    print(bang.loc[~du, ["huyen", "thang_so", "n_mua", "n_et"]])

bang = bang[du].drop(columns=["n_mua", "n_et"], errors='ignore')

# --- Lưu file ---
bang.to_csv(OUT / f"bang_huyen_thang_{NAM}.csv", index=False)

# --- Kiểm tra ---
print(f"\n✅ Đã xử lý xong năm {NAM}. Kích thước:", bang.shape)
if not bang.empty:
    print("\nSố ô bị thiếu mỗi cột:")
    print(bang.isna().sum()[lambda s: s > 0])
    print("\nMưa theo tháng (mm):")
    print(bang.pivot(index="thang_so", columns="huyen", values="mua_mm").round(0))