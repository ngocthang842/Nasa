"""RotaNA - lõi xử lý: nạp dữ liệu, chuẩn hóa, chấm điểm rủi ro theo cây và tháng."""
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
PROC = ROOT / "data" / "processed"
GEO_HUYEN = ROOT / "data" / "raw" / "ranh_gioi_huyen.geojson"
GEO_VN = ROOT / "data" / "raw" / "viet_nam.geojson"

NGUONG_NONG = 35
MUA_LON = 50
MUC = [(30, "Nên trồng", "#22C55E"), (55, "Cân nhắc", "#F59E0B"), (101, "Hạn chế", "#EF4444")]
MAU_NGOAI_VU = "#5B6B79"
TEN_HIEN_THI = {
    "yenthanh": "Yên Thành", "nghiloc": "Nghi Lộc", "concuong": "Con Cuông",
    "dienchau": "Diễn Châu", "doluong": "Đô Lương",
}

CAY = {
    "Lúa": dict(icon="🌾", tuoi=0.5, dat=None, lich={
        1: ("Gieo mạ, cấy vụ xuân", .1, .5, .2), 2: ("Đẻ nhánh", .1, .5, .2),
        3: ("Làm đòng", .3, .6, .2), 4: ("Trổ bông vụ xuân", 1, .8, .3),
        5: ("Chín, thu hoạch xuân", .5, .3, .6), 6: ("Làm đất, cấy hè thu", .6, .9, .4),
        7: ("Đẻ nhánh hè thu", .6, .7, .5), 8: ("Trổ bông, ngậm sữa hè thu", 1, .5, 1),
        9: ("Chín hè thu", .3, .2, .9), 10: ("Thu hoạch hè thu", .1, .1, 1)}),
    "Lạc": dict(icon="🥜", tuoi=0.9, lich={
        1: ("Gieo lạc xuân", .1, .3, .8), 2: ("Gieo, mọc mầm", .1, .4, .8), 3: ("Ra hoa", .3, .7, .7),
        4: ("Đâm tia, làm quả", .4, .9, .8), 5: ("Chín, thu hoạch", .3, .3, 1),
        9: ("Gieo lạc đông", .1, .3, .9), 10: ("Phát triển lạc đông", .1, .4, .8), 11: ("Thu hoạch lạc đông", .1, .2, .6)},
        dat=dict(pH=(5.0, 7.0), cat=(40, 90), set_max=30,
                 nguon="https://vaas.vn/sites/default/files/library/attachments/Ky-thuat-trong-lac.pdf",
                 mo_ta="Đất cát pha, thịt nhẹ, thoát nước tốt; pH hợp nhất 5,5 đến 6,0")),
    "Ngô": dict(icon="🌽", tuoi=0.9, lich={
        1: ("Gieo ngô xuân", .1, .5, .4), 2: ("Gieo, mọc mầm", .1, .6, .5), 3: ("Phát triển thân lá", .3, .7, .5),
        4: ("Trổ cờ, phun râu", 1, .8, .4), 5: ("Chín, thu hoạch", .4, .3, .7), 9: ("Gieo ngô đông", .1, .4, 1),
        10: ("Mọc mầm, phát triển", .1, .4, 1), 11: ("Phát triển ngô đông", .1, .5, .6), 12: ("Phát triển ngô đông", .1, .5, .4)},
        dat=dict(pH=(5.5, 7.5), cat=(0, 80), set_max=45,
                 nguon="https://wikifarmer.com/library/vi/article/chuan-bi-dat-yeu-cau-ve-dat-trong-va-yeu-cau-ve-gieo-hat-ngo",
                 mo_ta="Đất tơi xốp, thoát nước tốt; pH trên 5,5")),
    "Ngô nếp": dict(icon="🌽", tuoi=0.9, lich={
        1: ("Gieo ngô nếp xuân", .1, .5, .5), 2: ("Phát triển", .1, .6, .5), 3: ("Trổ cờ, phun râu", .8, .8, .5),
        4: ("Thu bắp xuân", .5, .3, .6), 9: ("Gieo ngô nếp đông", .1, .4, 1), 10: ("Phát triển", .1, .4, .9),
        11: ("Trổ cờ, phun râu", .1, .4, .7), 12: ("Thu bắp đông", .1, .2, .4)},
        dat=dict(pH=(5.5, 7.5), cat=(0, 80), set_max=45,
                 nguon="https://wikifarmer.com/library/vi/article/chuan-bi-dat-yeu-cau-ve-dat-trong-va-yeu-cau-ve-gieo-hat-ngo",
                 mo_ta="Như ngô: đất tơi xốp, thoát nước tốt, pH trên 5,5")),
    "Chè": dict(icon="🍵", tuoi=1.0, lich={
        1: ("Rét, cây nghỉ", 0, .2, 0), 2: ("Ra búp xuân", .1, .3, .2), 3: ("Búp xuân", .2, .4, .3),
        4: ("Hái chè", .4, .5, .3), 5: ("Hái chè", .6, .7, .3), 6: ("Hái chè, nắng nóng", .8, .9, .4),
        7: ("Hái chè, nắng nóng", .9, 1, .4), 8: ("Hái chè, mưa lớn", .8, .8, .7), 9: ("Mưa lớn, xói mòn", .3, .3, .9),
        10: ("Mưa lớn, xói mòn", .2, .2, .9), 11: ("Hái cuối vụ", .1, .3, .4), 12: ("Cây nghỉ", 0, .2, .1)},
        dat=dict(pH=(4.5, 5.5),
                 nguon="https://tapchicongthuong.vn/phan-bon-van-dien--lua-chon-cua-nguoi-trong-che-phu-tho-62056.htm",
                 mo_ta="pH 4,5 đến 5,5; tầng đất sâu; mưa năm trên 1.200 mm")),
    "Cam": dict(icon="🍊", tuoi=1.0, lich={
        1: ("Phân hóa mầm hoa", 0, .3, .2), 2: ("Phân hóa mầm hoa", 0, .3, .2), 3: ("Ra hoa", .3, .5, .5),
        4: ("Đậu quả", .7, .8, .5), 5: ("Quả non", .8, .9, .5), 6: ("Quả lớn", .8, .8, .7), 7: ("Quả lớn", .8, .7, .8),
        8: ("Quả lớn, mùa bão", .6, .5, .9), 9: ("Quả lớn", .4, .4, .9), 10: ("Chín, thu hoạch", .2, .3, .8),
        11: ("Thu hoạch", .1, .2, .5), 12: ("Nghỉ", 0, .1, .2)},
        dat=dict(pH=(5.0, 6.5), set_max=40,
                 nguon="",
                 mo_ta="Cam ưa đất tơi, thoát nước, pH khoảng 5 đến 6,5. Úng gốc và nắng lúc đậu quả đều hại")),
    "Sắn": dict(icon="🌿", tuoi=1.0, lich={
        1: ("Thu hoạch", 0, .1, .2), 4: ("Trồng sắn", .3, .7, .5), 5: ("Trồng, mọc mầm", .4, .8, .6),
        6: ("Phát triển thân lá", .6, .7, .6), 7: ("Phát triển thân lá", .6, .5, .6), 8: ("Phát triển", .4, .3, .8),
        9: ("Phát triển", .2, .2, .8), 10: ("Phát triển", .1, .2, .7), 11: ("Tích lũy củ", 0, .1, .5), 12: ("Thu hoạch", 0, .1, .3)},
        dat=dict(pH=(4.5, 7.5),
                 nguon="",
                 mo_ta="Đất thoát nước tốt, pH 4,5 đến 7,5; trồng tháng 4 đến 6, thu cuối năm")),
}

CAY_VUNG = {
    "Yên Thành": ["Lúa", "Lạc", "Ngô"],
    "Nghi Lộc": ["Lúa", "Ngô nếp", "Lạc"],
    "Con Cuông": ["Chè", "Cam", "Ngô", "Sắn"],
}

# (vùng, cây, một câu nôm na)
GIOI_THIEU = [
    ("Yên Thành", "Lúa", "Cây chính của huyện, thâm canh lúa từ lâu."),
    ("Yên Thành", "Lạc", "Lạc xuân trồng nhiều, nhưng sợ mưa lạnh và ngập."),
    ("Yên Thành", "Ngô", "Chủ yếu ở xã vùng cao, không phải cây số một."),
    ("Nghi Lộc", "Ngô nếp", "Đặc sản của huyện, trồng vụ đông và vụ xuân, hay xen lạc."),
    ("Nghi Lộc", "Lạc", "Hợp đất cát ven biển, là cây chủ lực cùng ngô nếp."),
    ("Nghi Lộc", "Lúa", "Vẫn trồng, nhưng không phải cây người ta nhớ tới Nghi Lộc."),
    ("Con Cuông", "Chè", "Cây kinh tế số một trên đồi, gắn với xóa đói giảm nghèo."),
    ("Con Cuông", "Cam", "Cam (trước ghi là cây có múi) là cây ăn quả chủ lực cùng chè."),
    ("Con Cuông", "Ngô", "Cây trồng thêm trên nương, cần Phòng nông nghiệp xác nhận thêm."),
    ("Con Cuông", "Sắn", "Trồng trên đất dốc, cùng nhóm với ngô."),
]

KICH_BAN = {
    "KB 0: Độc canh (Lúa - Trồng - Lúa)": {"nuoc": 35, "dat": 42, "kt": 28, "mau": "#9E9E9E"},
    "KB 2: Chịu hạn (Lúa - Vừng đen - Lúa)": {"nuoc": 30, "dat": 80, "kt": 52, "mau": "#2196F3"},
}
VUNG = {"Yên Thành": "đồng bằng chuyên lúa", "Nghi Lộc": "ven biển, đất pha cát", "Con Cuông": "đồi núi"}


def khoa(s):
    s = unicodedata.normalize("NFD", str(s).lower().replace("đ", "d"))
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def ten_huyen(s):
    return TEN_HIEN_THI.get(khoa(s), str(s).strip())


def _c(x):
    return float(np.clip(x, 0, 1))


def muc_tu_diem(r):
    for gioi_han, ten, mau in MUC:
        if r < gioi_han:
            return ten, mau
    return MUC[-1][1], MUC[-1][2]


def doc_thang():
    # Luôn ưu tiên đọc tất cả các file bang_huyen_thang_*.csv (có nhiều năm)
    fs = sorted(PROC.glob("bang_huyen_thang*.csv"))

    # Nếu không có file bang_huyen_thang, mới tìm đến file rui_ro (dự phòng)
    if not fs:
        fs = sorted(PROC.glob("rui_ro_huyen_thang*.csv"))

    out = []
    for f in fs:
        d = pd.read_csv(f)
        d["thang"] = pd.to_datetime(d["thang"])
        d["year"], d["month"] = d.thang.dt.year, d.thang.dt.month

        # Chuyển các cột nong35_2024, nong35_2025... thành một cột chung là nong35
        for b in ("nong35", "tmax", "rh"):
            d[b] = np.nan
            for c in d.columns:
                m = re.fullmatch(rf"{b}_(\d{{4}})", c)
                if m:
                    k = d.year == int(m[1])
                    d.loc[k, b] = d.loc[k, c]
        out.append(d)

    if not out:
        return pd.DataFrame()

    d = pd.concat(out).drop_duplicates(["huyen", "thang"], keep="last")
    d["huyen"] = d.huyen.map(ten_huyen)
    return d.sort_values(["huyen", "thang"]).reset_index(drop=True)


def doc_nam():
    f = PROC / "gio_lao_theo_nam.csv"
    d = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["huyen", "nam", "nguong", "so_ngay"])
    d["huyen"] = d.huyen.map(ten_huyen)
    return d


def doc_tb():
    f = PROC / "gio_lao_theo_thang.csv"
    d = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["huyen", "thang_so", "ngay_nong35_tb"])
    d["huyen"] = d.huyen.map(ten_huyen)
    return d


def diem_dat(r, cay):
    d = CAY[cay].get("dat")
    if not d:
        return None, "Chưa có tiêu chí đất có nguồn cho cây này"
    s, ghi = 1.0, []
    ph = getattr(r, "ph", np.nan)
    cat = getattr(r, "cat_pct", np.nan)
    set_ = getattr(r, "set_pct", np.nan)
    if "pH" in d and pd.notna(ph):
        lo, hi = d["pH"]
        k = max(lo - ph, ph - hi, 0)
        if k > 0:
            s -= min(.5, .35 * k)
            ghi.append(f"pH {ph:.1f} ngoài mức cây ưa {lo} đến {hi}")
    if "cat" in d and pd.notna(cat) and not d["cat"][0] <= cat <= d["cat"][1]:
        s -= .25
        ghi.append(f"cát {cat:.0f}% ngoài mức cây ưa {d['cat'][0]} đến {d['cat'][1]}%")
    if "set_max" in d and pd.notna(set_) and set_ > d["set_max"]:
        s -= .25
        ghi.append(f"sét {set_:.0f}% cao hơn mức {d['set_max']}%")
    s = max(s, .2)
    muc = ("Hợp" if not ghi else "Gần hợp") if s >= .85 else "Tạm được" if s >= .6 else "Kém"
    return s, f"Đất vùng này: {muc}" + (" (" + "; ".join(ghi) + ")" if ghi else "") + ". " + d.get("mo_ta", "")


def cham(r, cay):
    cfg = CAY[cay]
    stg = cfg["lich"].get(int(r.month))
    s, dat_txt = diem_dat(r, cay)
    if stg is None:
        return dict(giai_doan="Ngoài vụ thường lệ", rui_ro=np.nan, muc="Ngoài vụ", mau=MAU_NGOAI_VU,
                    ly_do="Tháng này không nằm trong lịch vụ của cây.", dat_txt=dat_txt)
    gd, wn, wh, wu = stg
    nong = r.nong35 if pd.notna(r.nong35) else 0
    nuoc = r.nuoc_con_lai_mm if pd.notna(getattr(r, "nuoc_con_lai_mm", np.nan)) else 0
    mua = r.mua_mm if pd.notna(getattr(r, "mua_mm", np.nan)) else 0
    f = getattr(r, "nhanh3_ung_ngap", False)
    flag = bool(f) if pd.notna(f) else False
    kho = _c((50 - nuoc) / 150)
    ung = max(_c((mua - 350) / 300), .7 * flag)
    pn, ph, pu = wn * _c(nong / 8), wh * cfg["tuoi"] * kho, wu * ung
    rr = 100 * (1 - (1 - pn) * (1 - ph) * (1 - pu))
    if s is not None:
        rr = min(100, rr + (1 - s) * 30)
    muc, mau = muc_tu_diem(rr)
    top = max((pn, f"{int(nong)} ngày nắng từ {NGUONG_NONG}°C đúng giai đoạn {gd.lower()}"),
              (ph, f"thiếu nước, cán cân nước {nuoc:.0f} mm (mưa {mua:.0f} mm)"),
              (pu, f"mưa {mua:.0f} mm trong tháng, nguy cơ úng ngập"))
    ly_do = "Chưa thấy yếu tố thời tiết bất lợi cho giai đoạn này." if top[0] < .15 else "Rủi ro chính: " + top[1] + "."
    return dict(giai_doan=gd, rui_ro=rr, muc=muc, mau=mau, ly_do=ly_do, dat_txt=dat_txt)


def bang_diem(df):
    rows = []
    for r in df.itertuples(index=False):
        for c in CAY_VUNG.get(r.huyen, []):
            rows.append(dict(huyen=r.huyen, year=r.year, month=r.month, cay=c, **cham(r, c)))
    return pd.DataFrame(rows)
