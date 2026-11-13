import earthaccess
import xarray as xr
import pandas as pd
import numpy as np
import os
import time
import re

earthaccess.login(strategy="netrc")

huyen_coords = {
    "Yen Thanh": (19.03, 105.45),
    "Nghi Loc": (18.78, 105.65),
    "Con Cuong": (19.05, 104.88),
}

# ====== CẤU HÌNH ======
START = "2025-07-31"      # lùi 1 ngày vì giờ UTC chậm hơn giờ Việt Nam 7 tiếng
END = "2025-09-30"
NGAY_DAU, NGAY_CUOI = "2025-08-01", "2025-09-30"   # khoảng ngày (giờ VN) muốn giữ lại
UTC_OFFSET = 7            # 7 = tính ngày theo giờ Việt Nam, 0 = giữ giờ UTC

RAW_CSV = "data/processed/GPM_30p_tho.csv"
OUT_CSV = "data/processed/GPM_Mua_CucDoan_2025.csv"
temp_dir = "./data/temp_raw/GPM_3IMERGHH/"
os.makedirs(temp_dir, exist_ok=True)
os.makedirs("data/processed", exist_ok=True)


def thoi_gian_tu_ten(ten_file):
    """Tên file dạng ...3IMERG.20250801-S003000-E005959... -> '2025-08-01 00:30' (UTC)."""
    m = re.search(r'(\d{4})(\d{2})(\d{2})-S(\d{2})(\d{2})', ten_file)
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)} {m.group(4)}:{m.group(5)}"


# Nếu lần trước chạy dở thì đọc lại phần đã xong, khỏi tải lại
if os.path.exists(RAW_CSV):
    raw_cu = pd.read_csv(RAW_CSV)
    all_data = raw_cu.to_dict("records")
    da_xong = set(raw_cu["datetime"])
    print(f"Tiếp tục từ lần trước: đã có {len(da_xong)} khung 30 phút.")
else:
    all_data, da_xong = [], set()

print("--- Đang tìm kiếm dữ liệu GPM 30 phút ---")
results = earthaccess.search_data(
    short_name="GPM_3IMERGHH",
    version="07",
    temporal=(START, END),
    bounding_box=(104.0, 18.5, 106.0, 19.5)
)
print(f"Tìm thấy {len(results)} file (mỗi ngày 48 file).")

for i, result in enumerate(results):
    file_path = None
    ds = None
    try:
        ten_file = os.path.basename(result.data_links()[0])
        thoi_gian = thoi_gian_tu_ten(ten_file)
        if thoi_gian is None:
            raise ValueError(f"Không đọc được ngày giờ từ tên file: {ten_file}")
        if thoi_gian in da_xong:
            continue

        file_path = earthaccess.download([result], temp_dir)[0]
        ds = xr.open_dataset(file_path, group='Grid')

        for ten, (lat, lon) in huyen_coords.items():
            val = ds['precipitation'].sel(lat=lat, lon=lon, method='nearest').item()
            if np.isnan(val) or val < 0:      # bỏ giá trị lỗi
                val = np.nan
            all_data.append({"huyen": ten, "datetime": thoi_gian, "mua_mmh": val})

        ds.close()
        ds = None
        time.sleep(0.1)
        os.remove(file_path)
        da_xong.add(thoi_gian)

        if (i + 1) % 100 == 0:
            print(f"Đã xử lý {i + 1}/{len(results)} file...")
            pd.DataFrame(all_data).to_csv(RAW_CSV, index=False)   # lưu tạm

    except Exception as e:
        print(f"Lỗi ở file thứ {i + 1}: {e}")
        if ds is not None:
            try:
                ds.close()
            except:
                pass
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

# ====== TỔNG HỢP ======
if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv(RAW_CSV, index=False)

    df["datetime"] = pd.to_datetime(df["datetime"]) + pd.Timedelta(hours=UTC_OFFSET)
    df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= NGAY_DAU) & (df["date"] <= NGAY_CUOI)]

    # Biến 'precipitation' là tốc độ mưa (mm/giờ), mỗi khung dài 30 phút -> nhân 0.5 ra mm
    df["mua_mm"] = df["mua_mmh"] * 0.5

    df_ngay = df.groupby(["huyen", "date"], as_index=False).agg(
        mua_ngay_mm=("mua_mm", "sum"),            # tổng mưa trong ngày (mm)
        mua_max_30p_mm=("mua_mm", "max"),         # mưa lớn nhất trong 1 khung 30 phút (mm)
        cuong_do_max_mmh=("mua_mmh", "max"),      # cường độ lớn nhất (mm/giờ)
        so_khung_hop_le=("mua_mm", "count"),      # đủ ngày là 48 khung
    )
    df_ngay.to_csv(OUT_CSV, index=False)

    thieu = df_ngay[df_ngay["so_khung_hop_le"] < 48]
    if len(thieu):
        print(f"⚠️ Có {len(thieu)} dòng huyện-ngày thiếu khung 30 phút (xem cột so_khung_hop_le).")
    print(f"✅ HOÀN THÀNH! Đã lưu: {OUT_CSV}")
    print(df_ngay.sort_values("cuong_do_max_mmh", ascending=False).head(10))