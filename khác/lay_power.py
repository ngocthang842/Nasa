import requests
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent   # thư mục chứa "khác" và "data"
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"

# Tọa độ xấp xỉ trung tâm huyện (POWER có độ phân giải ~50 km nên sai lệch vài km không đáng kể)
HUYEN = {
    "Yen Thanh": (19.03, 105.45),
    "Nghi Loc": (18.78, 105.65),
    "Con Cuong": (19.05, 104.88),
}
THAM_SO = "T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN"

for ten, (lat, lon) in HUYEN.items():
    print(f"Đang lấy {ten} ...")
    r = requests.get(
        "https://power.larc.nasa.gov/api/temporal/daily/point",
        params={
            "parameters": THAM_SO,
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": "20150101",
            "end": "20261110",
            "format": "JSON",
        },
        timeout=180,
    )
    if r.status_code != 200:
        print("  LỖI:", r.status_code, r.text[:300])
        continue

    p = r.json()["properties"]["parameter"]
    df = pd.DataFrame(p)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    df = df.replace(-999, float("nan"))
    df.to_csv(RAW / f"power_{ten.replace(' ', '_')}.csv")

    nam = df.loc["2025"]
    so_ngay_nong = (nam["T2M_MAX"] > 39).groupby(nam.index.month).sum()
    print(f"  Xong: {df.shape[0]} dòng, {df.shape[1]} cột")
    print("  Số ngày Tmax > 39°C trong năm 2025, theo tháng:")
    print("  ", so_ngay_nong[so_ngay_nong > 0].to_dict() or "không có ngày nào")