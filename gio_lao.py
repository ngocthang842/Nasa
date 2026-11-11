import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

pd.set_option("display.width", 200)

HUYEN = ["Yen_Thanh", "Nghi_Loc", "Con_Cuong"]
NGUONG = [35, 37, 39]

def dem_chuoi_dai_nhat(bool_series):
    """Số ngày liên tiếp dài nhất mà điều kiện đúng."""
    dai, hien_tai = 0, 0
    for v in bool_series:
        hien_tai = hien_tai + 1 if v else 0
        dai = max(dai, hien_tai)
    return dai

dong_nam, dong_thang = [], []

for h in HUYEN:
    df = pd.read_csv(RAW / f"power_{h}.csv", parse_dates=["date"]).set_index("date")
    ten = h.replace("_", " ")

    # 1) Số ngày nóng mỗi năm theo từng ngưỡng
    for n in NGUONG:
        dem = (df["T2M_MAX"] >= n).groupby(df.index.year).sum()
        for nam, so in dem.items():
            dong_nam.append({"huyen": ten, "nam": nam, "nguong": n, "so_ngay": int(so)})

    # 2) Trung bình nhiều năm theo tháng: số ngày >= 35°C và Tmax trung bình
    nong35 = (df["T2M_MAX"] >= 35).groupby([df.index.year, df.index.month]).sum()
    tb_thang = nong35.groupby(level=1).mean()
    tmax_thang = df["T2M_MAX"].groupby(df.index.month).mean()
    rh_thang = df["RH2M"].groupby(df.index.month).mean()
    for t in range(1, 13):
        dong_thang.append({"huyen": ten, "thang_so": t,
                           "tmax_tb": round(tmax_thang[t], 1),
                           "rh_tb": round(rh_thang[t], 1),
                           "ngay_nong35_tb": round(tb_thang.get(t, 0), 1)})

    print(f"\n{ten}: Tmax lớn nhất 11 năm = {df['T2M_MAX'].max():.1f}°C, "
          f"chuỗi ngày liên tiếp >= 35°C dài nhất = {dem_chuoi_dai_nhat(df['T2M_MAX'] >= 35)} ngày")

theo_nam = pd.DataFrame(dong_nam)
theo_thang = pd.DataFrame(dong_thang)

print("\nSố ngày nóng mỗi năm (ngưỡng 35°C):")
print(theo_nam[theo_nam.nguong == 35].pivot(index="nam", columns="huyen", values="so_ngay"))
print("\nSố ngày nóng mỗi năm (ngưỡng 37°C):")
print(theo_nam[theo_nam.nguong == 37].pivot(index="nam", columns="huyen", values="so_ngay"))
print("\nTrung bình nhiều năm theo tháng:")
print(theo_thang.pivot(index="thang_so", columns="huyen",
                       values=["tmax_tb", "ngay_nong35_tb"]))

theo_nam.to_csv(OUT / "gio_lao_theo_nam.csv", index=False)
theo_thang.to_csv(OUT / "gio_lao_theo_thang.csv", index=False)