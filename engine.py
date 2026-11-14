"""RotaNA - Lõi xử lý chuyên sâu: Vựa lúa Yên Thành (Nghệ An).

Tập trung vào cây lúa nước và hệ thống cây luân canh cải tạo đất lúa (Lạc, Ngô, Rau màu vụ đông).
Chấm điểm rủi ro thời tiết (gió Lào, ngập lụt, hạn hán, rét đậm) theo vệ tinh NASA & MODIS/SMAP/GPM.
"""
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
    "yenthanh": "Yên Thành",
}

# HỆ THỐNG CÂY TRỒNG VỰA LÚA YÊN THÀNH
CAY = {
    "Lúa": dict(
        icon="🌾",
        tuoi=0.5,
        dat=dict(
            pH=(5.5, 7.0),
            set_max=50,
            cat=(10, 60),
            mo_ta="Đất phù sa sông Dinh/sông Đào Yên Thành, đất thịt pha sét giữ nước tốt; thổ nhưỡng vàng cho thâm canh lúa.",
        ),
        lich={
            1: ("Gieo mạ, cấy lúa xuân (phòng rét đậm)", 0.1, 0.4, 0.2),
            2: ("Đẻ nhánh lúa xuân, tỉa dặm giữ nước", 0.1, 0.4, 0.2),
            3: ("Làm đòng lúa xuân, bón đón đòng", 0.3, 0.5, 0.2),
            4: ("Trổ bông lúa xuân, thụ phấn trổ đều", 1.0, 0.8, 0.3),
            5: ("Chín & thu hoạch rộ lúa xuân", 0.5, 0.3, 0.6),
            6: ("Làm đất khẩn trương, cấy lúa hè thu", 0.6, 0.9, 0.4),
            7: ("Đẻ nhánh lúa hè thu, phòng nắng hạn", 0.6, 0.7, 0.5),
            8: ("Trổ bông lúa hè thu (chống táp do gió Lào)", 1.0, 0.5, 0.9),
            9: ("Chín, gặt lúa hè thu chạy lũ tiểu mãn", 0.3, 0.2, 0.9),
            10: ("Thu hoạch dứt điểm hè thu, chuẩn bị vụ đông", 0.1, 0.1, 0.9),
        },
    ),
    "Lạc": dict(
        icon="🥜",
        tuoi=0.9,
        lich={
            1: ("Gieo lạc xuân", 0.1, 0.3, 0.8),
            2: ("Mọc mầm, phát triển thân lá", 0.1, 0.4, 0.8),
            3: ("Ra hoa rộ", 0.3, 0.7, 0.7),
            4: ("Đâm tia, tạo củ", 0.4, 0.9, 0.8),
            5: ("Thu hoạch lạc xuân", 0.3, 0.3, 1.0),
            9: ("Làm đất gieo lạc đông", 0.1, 0.3, 0.9),
            10: ("Phát triển củ vụ đông", 0.1, 0.4, 0.8),
            11: ("Thu hoạch lạc đông", 0.1, 0.2, 0.6),
        },
        dat=dict(
            pH=(5.0, 7.0),
            cat=(40, 90),
            set_max=30,
            mo_ta="Đất cát pha thịt nhẹ bờ bãi Yên Thành; luân canh với lúa giúp nốt sần rễ cố định đạm cải tạo đất lúa.",
        ),
    ),
    "Ngô": dict(
        icon="🌽",
        tuoi=0.9,
        lich={
            1: ("Gieo ngô xuân bãi bồi", 0.1, 0.5, 0.4),
            2: ("Mọc mầm, phát triển thân lá", 0.1, 0.6, 0.5),
            3: ("Phát triển thân lá mạnh", 0.3, 0.7, 0.5),
            4: ("Trổ cờ, phun râu", 1.0, 0.8, 0.4),
            5: ("Thu hoạch bắp xuân", 0.4, 0.3, 0.7),
            9: ("Gieo ngô đông trên đất 2 vụ lúa", 0.1, 0.4, 1.0),
            10: ("Phát triển cây con vụ đông", 0.1, 0.4, 1.0),
            11: ("Trổ cờ ngô đông", 0.1, 0.5, 0.6),
            12: ("Thu hoạch bắp vụ đông", 0.1, 0.5, 0.4),
        },
        dat=dict(
            pH=(5.5, 7.5),
            cat=(10, 80),
            set_max=45,
            mo_ta="Đất phù sa tơi xốp, thoát nước nhanh; cây màu vụ đông truyền thống trên chân đất 2 lúa Yên Thành.",
        ),
    ),
    "Rau màu vụ đông": dict(
        icon="🥬",
        tuoi=0.6,
        dat=dict(
            pH=(5.8, 7.2),
            cat=(20, 75),
            set_max=35,
            mo_ta="Bắp cải, su hào, khoai tây, cà chua... trên đất 2 lúa; tận dụng đất vụ đông T10–T12 mang lại giá trị kinh tế cao.",
        ),
        lich={
            9: ("Làm đất lên luống sau gặt lúa hè thu", 0.1, 0.3, 0.9),
            10: ("Gieo trồng rau màu vụ đông", 0.1, 0.3, 0.8),
            11: ("Chăm sóc, phát triển rộ thời tiết mát", 0.0, 0.3, 0.4),
            12: ("Thu hoạch rộ rau màu vụ đông", 0.0, 0.2, 0.3),
            1: ("Thu hoạch dứt điểm để làm đất cấy lúa xuân", 0.0, 0.2, 0.2),
        },
    ),
}

CAY_VUNG = {
    "Yên Thành": ["Lúa", "Lạc", "Ngô", "Rau màu vụ đông"],
}

VUNG = {
    "Yên Thành": "Vựa lúa đồng bằng Nghệ An",
}

GIOI_THIEU = [
    ("Yên Thành", "Lúa", "Vựa lúa trọng điểm số 1 của Nghệ An, hệ thống kênh mương thủy lợi Ba Ra Đô Lương hoàn chỉnh."),
    ("Yên Thành", "Lạc", "Cây họ đậu luân canh với lúa giúp đất màu mỡ, cắt đứt nguồn bệnh đạo ôn trên chân ruộng."),
    ("Yên Thành", "Ngô", "Cây trồng vụ đông truyền thống tạo nguồn thức ăn chăn nuôi sau thu hoạch lúa hè thu."),
    ("Yên Thành", "Rau màu vụ đông", "Mô hình thâm canh rau màu vụ đông đem lại thu nhập cao trên đất lúa 2 vụ."),
]

# Các phương án đợt mùa vụ cho vựa lúa Yên Thành
DOT_MAC_DINH = [
    {
        "ten": "Vụ Lúa Xuân (Tháng 1 – Tháng 5)",
        "ma": "xuan",
        "so_thang": 5,
        "thang_bat_dau": 1,
        "thang_ket_thuc": 5,
        "icon": "🌾",
        "mau": "#22C55E",
        "dac_trung": "Vụ lúa chính trong năm của Yên Thành: gieo cấy T1-T2, làm đòng T3, trổ bông rộ T4, thu hoạch T5; năng suất cao nhất.",
    },
    {
        "ten": "Vụ Lúa Hè Thu (Tháng 6 – Tháng 9)",
        "ma": "hethu",
        "so_thang": 4,
        "thang_bat_dau": 6,
        "thang_ket_thuc": 9,
        "icon": "☀️",
        "mau": "#F59E0B",
        "dac_trung": "Vụ lúa hè thu: Cần thu hoạch trước ngày 15-20/9 để tránh mưa bão lớn và lũ tiểu mãn.",
    },
    {
        "ten": "Vụ Cây Đông & Để ải (Tháng 10 – Tháng 12)",
        "ma": "dong",
        "so_thang": 3,
        "thang_bat_dau": 10,
        "thang_ket_thuc": 12,
        "icon": "🥬",
        "mau": "#0EA5E9",
        "dac_trung": "Vụ đông / Để ải đất: Trồng ngô, lạc đông, rau màu hoặc cày ải đất phơi nắng để diệt mầm sâu bệnh.",
    },
]


def tinh_toan_cac_dot(kieu_chia):
    """Tính danh sách đợt mùa vụ tối ưu cho vựa lúa Yên Thành."""
    if "2 vụ lúa" in str(kieu_chia) or "2 đợt (6 tháng" in str(kieu_chia):
        return [
            {
                "ten": "Đợt 1: Vụ Lúa Xuân (Tháng 1 – Tháng 6)",
                "ma": "dot1",
                "so_thang": 6,
                "thang_bat_dau": 1,
                "thang_ket_thuc": 6,
                "icon": "🌾",
                "mau": "#22C55E",
                "dac_trung": "6 tháng đầu năm: Trọng tâm thâm canh lúa xuân, lạc xuân; thu hoạch gọn trước tháng 6.",
            },
            {
                "ten": "Đợt 2: Vụ Lúa Hè Thu & Vụ Đông (Tháng 7 – Tháng 12)",
                "ma": "dot2",
                "so_thang": 6,
                "thang_bat_dau": 7,
                "thang_ket_thuc": 12,
                "icon": "☀️",
                "mau": "#F59E0B",
                "dac_trung": "6 tháng cuối năm: Lúa hè thu thu hoạch chạy lụt tháng 9, tiếp nối cây vụ đông hoặc phơi ải đất.",
            },
        ]
    elif "4 đợt" in str(kieu_chia):
        return [
            {
                "ten": "Quý I (Tháng 1 – Tháng 3)",
                "ma": "q1",
                "so_thang": 3,
                "thang_bat_dau": 1,
                "thang_ket_thuc": 3,
                "icon": "🌱",
                "mau": "#22C55E",
                "dac_trung": "Gieo cấy lúa xuân, làm đòng thời tiết đầu xuân mát mẻ.",
            },
            {
                "ten": "Quý II (Tháng 4 – Tháng 6)",
                "ma": "q2",
                "so_thang": 3,
                "thang_bat_dau": 4,
                "thang_ket_thuc": 6,
                "icon": "🌾",
                "mau": "#F59E0B",
                "dac_trung": "Lúa xuân trổ bông rộ, thu hoạch và làm đất cấy hè thu.",
            },
            {
                "ten": "Quý III (Tháng 7 – Tháng 9)",
                "ma": "q3",
                "so_thang": 3,
                "thang_bat_dau": 7,
                "thang_ket_thuc": 9,
                "icon": "☀️",
                "mau": "#EF4444",
                "dac_trung": "Cao điểm nắng nóng gió Lào tháng 7, trổ bông tháng 8, gặt chạy lũ tháng 9.",
            },
            {
                "ten": "Quý IV (Tháng 10 – Tháng 12)",
                "ma": "q4",
                "so_thang": 3,
                "thang_bat_dau": 10,
                "thang_ket_thuc": 12,
                "icon": "🥬",
                "mau": "#0EA5E9",
                "dac_trung": "Vụ đông hoặc cày ải đất phục hồi độ phì cho chân ruộng.",
            },
        ]
    return DOT_MAC_DINH


def ten_huyen(t):
    if not t:
        return ""
    x = t.strip().lower()
    x = re.sub(r"^(huyện|h\.|tp\.|thành phố|thị xã|tx\.)\s*", "", x)
    m = unicodedata.normalize("NFD", x)
    x = "".join(c for c in m if unicodedata.category(c) != "Mn")
    x = re.sub(r"\s+", "", x)
    return TEN_HIEN_THI.get(x, t.strip())


def khoa(s):
    if not s:
        return ""
    m = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in m if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s)


def doc_thang():
    fs = sorted(PROC.glob("bang_huyen_thang*.csv"))
    if not fs:
        fs = sorted(PROC.glob("rui_ro_huyen_thang*.csv"))
    out = []
    for f in fs:
        d = pd.read_csv(f)
        d["thang"] = pd.to_datetime(d["thang"])
        d["year"], d["month"] = d.thang.dt.year, d.thang.dt.month
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
    df = pd.concat(out, ignore_index=True)
    df = df.drop_duplicates(subset=["year", "month", "huyen"])
    df.huyen = df.huyen.apply(ten_huyen)
    # Lọc duy nhất huyện Yên Thành, loại bỏ tất cả các huyện khác
    df = df[df.huyen == "Yên Thành"].reset_index(drop=True)

    # Điền khuyết thông minh dữ liệu viễn thám SMAP, ET, Cán cân nước từ chuẩn đa năm để không bị dấu gạch ngang
    for col in ["sm_rootzone", "sm_surface", "et_mm", "pet_mm", "ndvi", "evi"]:
        if col in df.columns:
            df[col] = df[col].fillna(df.groupby("month")[col].transform("mean"))

    if "nuoc_con_lai_mm" in df.columns and "mua_mm" in df.columns and "et_mm" in df.columns:
        df["nuoc_con_lai_mm"] = df["nuoc_con_lai_mm"].fillna(df["mua_mm"] - df["et_mm"]).fillna(df["mua_mm"] - 80)

    return df


def doc_nam():
    f = PROC / "gio_lao_theo_nam.csv"
    d = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["huyen", "nam", "nguong", "so_ngay"])
    d["huyen"] = d.huyen.map(ten_huyen)
    d = d[d.huyen == "Yên Thành"].reset_index(drop=True)
    return d


def doc_tb():
    f = PROC / "gio_lao_theo_thang.csv"
    d = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["huyen", "thang_so", "ngay_nong35_tb"])
    d["huyen"] = d.huyen.map(ten_huyen)
    d = d[d.huyen == "Yên Thành"].reset_index(drop=True)
    return d


def lay_du_lieu_lich_su(dl, vung="Yên Thành", nam_hien_tai=2026):
    """Trích xuất dữ liệu lịch sử đối chiếu cho huyện Yên Thành."""
    df_vung = dl[dl.huyen == vung]
    return df_vung[df_vung.year < nam_hien_tai] if not df_vung.empty else dl


def phan_tich_khi_hau_dot(dl, vung, thang_bat_dau, thang_ket_thuc, nam_hien_tai, tb_df=None):
    """Phân tích chuỗi số liệu khí hậu đa năm của huyện Yên Thành trong khoảng tháng của đợt."""
    thangs = list(range(thang_bat_dau, thang_ket_thuc + 1))
    ls_df = lay_du_lieu_lich_su(dl, vung, nam_hien_tai)

    df_dot = ls_df[ls_df.month.isin(thangs)] if not ls_df.empty else pd.DataFrame()
    if df_dot.empty:
        df_dot = dl[(dl.huyen == vung) & (dl.month.isin(thangs))]

    tmax_tb = float(df_dot["tmax"].mean()) if "tmax" in df_dot.columns and not df_dot.empty else 31.0
    tmax_max = float(df_dot["tmax"].max()) if "tmax" in df_dot.columns and not df_dot.empty else 38.5

    nong35_tong_tb = 0.0
    if "nong35" in df_dot.columns and not df_dot.empty:
        nong35_per_year = df_dot.groupby("year")["nong35"].sum()
        nong35_tong_tb = float(nong35_per_year.mean()) if not nong35_per_year.empty else 5.0

    mua_tong_tb = 0.0
    if "mua_mm" in df_dot.columns and not df_dot.empty:
        mua_per_year = df_dot.groupby("year")["mua_mm"].sum()
        mua_tong_tb = float(mua_per_year.mean()) if not mua_per_year.empty else 300.0

    sm_tb = 0.35
    if "sm_rootzone" in df_dot.columns and not df_dot.empty:
        sm_valid = df_dot["sm_rootzone"].dropna()
        if not sm_valid.empty:
            sm_tb = float(sm_valid.mean())

    nuoc_con_tb = 0.0
    if "nuoc_con_lai_mm" in df_dot.columns and not df_dot.empty:
        nuoc_con_tb = float(df_dot["nuoc_con_lai_mm"].mean())

    thang_nong_nhat = thang_bat_dau
    thang_mua_nhat = thang_bat_dau
    if not df_dot.empty:
        thang_grp = df_dot.groupby("month").mean(numeric_only=True)
        if "tmax" in thang_grp.columns:
            thang_nong_nhat = int(thang_grp["tmax"].idxmax())
        if "mua_mm" in thang_grp.columns:
            thang_mua_nhat = int(thang_grp["mua_mm"].idxmax())

    return {
        "so_thang": len(thangs),
        "tmax_tb": tmax_tb,
        "tmax_max": tmax_max,
        "nong35_tong_tb": nong35_tong_tb,
        "mua_tong_tb": mua_tong_tb,
        "sm_tb": sm_tb,
        "nuoc_con_tb": nuoc_con_tb,
        "thang_nong_nhat": thang_nong_nhat,
        "thang_mua_nhat": thang_mua_nhat,
    }


def danh_gia_cay_theo_dot(dl, vung, thang_bat_dau, thang_ket_thuc, nam_hien_tai, tb_df=None):
    """Chấm điểm rủi ro và xếp hạng khuyến nghị cho các cây trồng vụ lúa Yên Thành."""
    thangs = list(range(thang_bat_dau, thang_ket_thuc + 1))
    cays = list(CAY_VUNG.get(vung, CAY.keys()))
    kh = phan_tich_khi_hau_dot(dl, vung, thang_bat_dau, thang_ket_thuc, nam_hien_tai, tb_df)

    ket_qua = []
    for cay in cays:
        thong_tin = CAY.get(cay, {})
        lich = thong_tin.get("lich", {})

        thang_trong_lich = [m for m in thangs if m in lich]
        if not thang_trong_lich:
            rui_ro = 90.0
            muc = "Hạn chế (Trái vụ)"
            ly_do = f"Khoảng Tháng {thang_bat_dau}–{thang_ket_thuc} không nằm trong khung mùa vụ chuẩn của {cay} tại Yên Thành."
        else:
            diem_thang = []
            ly_do_list = []
            for m in thang_trong_lich:
                gd, nhay_nong, nhay_han, nhay_ngap = lich[m]
                r_nong = min(100, max(0, (kh["tmax_tb"] - 30) * 12 * nhay_nong + (kh["nong35_tong_tb"] / max(1, len(thangs))) * 15 * nhay_nong))
                r_han = min(100, max(0, (0.35 - kh["sm_tb"]) * 180 * nhay_han)) if kh["sm_tb"] < 0.35 else 5 * nhay_han
                r_ngap = min(100, max(0, (kh["mua_tong_tb"] / len(thangs) - 200) * 0.4 * nhay_ngap)) if (kh["mua_tong_tb"] / len(thangs)) > 200 else 5 * nhay_ngap
                r_m = min(100, max(10, r_nong * 0.4 + r_han * 0.3 + r_ngap * 0.3))
                diem_thang.append(r_m)

            rui_ro = float(np.mean(diem_thang)) if diem_thang else 50.0

            # Điều chỉnh độ phù hợp theo thực tế Yên Thành
            if cay == "Lúa":
                # Lúa xuân hoặc lúa hè thu
                if 1 <= thang_bat_dau <= 3:
                    ly_do = "Vụ Lúa Xuân Yên Thành: Thời tiết thuận lợi, nguồn nước kênh Đô Lương dồi dào, tiềm năng năng suất cao nhất."
                    rui_ro = min(rui_ro, 22.0)
                elif 6 <= thang_bat_dau <= 7:
                    ly_do = "Vụ Lúa Hè Thu: Cần đề phòng gió Lào tháng 7 và chủ động gặt trước 15-20/9 để tránh lũ tiểu mãn."
                    rui_ro = min(rui_ro, 38.0)
                else:
                    ly_do = "Gieo cấy lúa muộn: Nguy cơ bão lụt tháng 9-10 hoặc rét đậm tháng 12 rất cao."
                    rui_ro = max(rui_ro, 65.0)
            elif cay == "Lạc":
                if 1 <= thang_bat_dau <= 2:
                    ly_do = "Vụ Lạc Xuân: Rất thích hợp trên đất bãi bồi ven sông, luân canh làm tăng độ phì cho đất lúa."
                    rui_ro = min(rui_ro, 25.0)
                else:
                    ly_do = "Lạc vụ khác: Chú ý thoát nước tốt trong mùa mưa lũ Yên Thành."
                    rui_ro = min(rui_ro, 48.0)
            elif cay == "Ngô":
                if 9 <= thang_bat_dau <= 10:
                    ly_do = "Ngô đông trên đất 2 vụ lúa: Thời tiết mát mẻ rất phù hợp, thời gian sinh trưởng ngắn."
                    rui_ro = min(rui_ro, 28.0)
                else:
                    ly_do = "Ngô xuân/hè: Cần tưới chủ động giai đoạn trổ cờ phun râu."
                    rui_ro = min(rui_ro, 42.0)
            else:
                ly_do = f"Thích hợp luân canh vụ đông (T10–T12) sau khi gặt lúa hè thu Yên Thành."
                rui_ro = min(rui_ro, 32.0)

            if rui_ro < 35:
                muc = "Nên trồng"
            elif rui_ro < 60:
                muc = "Cân nhắc"
            else:
                muc = "Hạn chế"

        ket_qua.append({
            "cay": cay,
            "rui_ro_dot": rui_ro,
            "muc_khuyen_nghi": muc,
            "ly_do": ly_do,
        })

    df_res = pd.DataFrame(ket_qua).sort_values("rui_ro_dot")
    return df_res


def danh_gia_to_hop_dot(df_dg_dot, cay_da_chon):
    """Đánh giá rủi ro tổ hợp cây trồng được nông dân Yên Thành chọn trong đợt."""
    if not cay_da_chon:
        return {
            "rui_ro_to_hop": 15.0,
            "muc": "Để ải đất / Nghỉ vụ",
            "nhan_xet": "Để ải đất phơi nắng: Giúp cắt đứt nguồn bệnh đạo ôn, ấu trùng rầy nâu và phục hồi hệ vi sinh vật đất lúa.",
            "loai": "nghi_vu",
        }

    tong_ty_le = sum(c["ty_le_pct"] for c in cay_da_chon)
    if tong_ty_le == 0:
        tong_ty_le = 100

    rui_ro_tong = 0.0
    dg_dict = df_dg_dot.set_index("cay")["rui_ro_dot"].to_dict() if not df_dg_dot.empty else {}

    for item in cay_da_chon:
        cay = item["cay"]
        tl = item["ty_le_pct"] / tong_ty_le
        rr_cay = dg_dict.get(cay, 45.0)
        rui_ro_tong += rr_cay * tl

    # Khuyến khích đa canh/luân canh
    so_cay = len(cay_da_chon)
    if so_cay >= 2:
        rui_ro_tong = max(15.0, rui_ro_tong - 5.0)

    muc = "Nên trồng" if rui_ro_tong < 35 else ("Cân nhắc" if rui_ro_tong < 60 else "Hạn chế")

    if so_cay == 1:
        nhan_xet = f"Chuyên canh {cay_da_chon[0]['cay']} (100% diện tích). Rủi ro bình quân {rui_ro_tong:.0f}%."
    else:
        cay_str = ", ".join([f"{c['cay']} ({c['ty_le_pct']}%)" for c in cay_da_chon])
        nhan_xet = f"Đa canh luân phiên: {cay_str}. Giảm thiểu rủi ro thời tiết và tăng hiệu quả sử dụng đất."

    return {
        "rui_ro_to_hop": rui_ro_tong,
        "muc": muc,
        "nhan_xet": nhan_xet,
        "loai": "trong_cay",
    }


def danh_gia_ke_hoach_nam(cac_dot, ke_hoach_nguoi_dung, danh_gia_cac_dot_map):
    """Tổng hợp đánh giá cả năm cho nông dân vựa lúa Yên Thành."""
    so_dot = len(cac_dot)
    so_thang_phu = sum(d["so_thang"] for d in cac_dot)

    cays_nam = []
    rui_ro_list = []
    co_cay_dau = False
    so_vu_lua = 0

    for d in cac_dot:
        ma = d["ma"]
        cays = ke_hoach_nguoi_dung.get(ma, [])
        for c in cays:
            cays_nam.append(c["cay"])
            if c["cay"] == "Lạc":
                co_cay_dau = True
            if c["cay"] == "Lúa":
                so_vu_lua += 1

        dg = danh_gia_cac_dot_map.get(ma, {})
        if dg:
            rui_ro_list.append(dg.get("rui_ro_to_hop", 40.0))

    rui_ro_tb_nam = float(np.mean(rui_ro_list)) if rui_ro_list else 35.0

    # Điểm luân canh & bồi dưỡng đất
    diem_luan_canh = 75
    diem_suc_khoe_dat = 70
    tiet_kiem_nuoc_pct = 0
    co_de_ai = any(len(ke_hoach_nguoi_dung.get(d["ma"], [])) == 0 for d in cac_dot)

    if co_cay_dau:
        diem_luan_canh += 15
        diem_suc_khoe_dat += 18
        tiet_kiem_nuoc_pct += 20
    if co_de_ai:
        diem_suc_khoe_dat += 12
        tiet_kiem_nuoc_pct += 15
    if so_vu_lua >= 3:
        diem_luan_canh -= 20
        diem_suc_khoe_dat -= 25
        tiet_kiem_nuoc_pct = max(0, tiet_kiem_nuoc_pct - 15)
    elif so_vu_lua == 1:
        tiet_kiem_nuoc_pct += 10

    diem_luan_canh = max(30, min(100, diem_luan_canh))
    diem_suc_khoe_dat = max(35, min(98, diem_suc_khoe_dat))
    tiet_kiem_nuoc_pct = max(0, min(45, tiet_kiem_nuoc_pct))

    muc_nam = "An toàn cao" if rui_ro_tb_nam < 35 else ("Trung bình" if rui_ro_tb_nam < 55 else "Cần theo dõi sát")

    khuyen_nghi_tong = []
    if so_vu_lua == 2 and co_cay_dau:
        khuyen_nghi_tong.append("🌟 **Công thức vàng luân canh Yên Thành:** Lúa xuân – Lúa hè thu – Cây họ đậu (Lạc). Vừa tối ưu năng suất lúa, vừa cải tạo đất tự nhiên.")
    elif so_vu_lua == 2:
        khuyen_nghi_tong.append("🌾 **Cơ cấu 2 vụ lúa thuần thục:** Đảm bảo thời vụ gieo cấy lúa hè thu sớm để gặt trước 15-20/9, tránh lũ lụt tiểu mãn.")
    if not co_cay_dau and so_vu_lua >= 2:
        khuyen_nghi_tong.append("💡 **Khuyến nghị bổ sung:** Nên luân canh thêm Lạc hoặc Rau màu vụ đông để bồi dục đất, cắt đứt chu kỳ bệnh đạo ôn và rầy nâu hại lúa.")

    return {
        "so_dot": so_dot,
        "so_thang_phu": so_thang_phu,
        "rui_ro_tb_nam": rui_ro_tb_nam,
        "muc_rui_ro_nam": muc_nam,
        "cay_da_dung": sorted(list(set(cays_nam))),
        "diem_luan_canh": diem_luan_canh,
        "diem_suc_khoe_dat": diem_suc_khoe_dat,
        "tiet_kiem_nuoc_pct": tiet_kiem_nuoc_pct,
        "co_cay_dau": co_cay_dau,
        "co_de_ai": co_de_ai,
        "khuyen_nghi_tong": " ".join(khuyen_nghi_tong) if khuyen_nghi_tong else "Kế hoạch canh tác hài hòa với chu kỳ khí tượng Yên Thành.",
    }


def goi_y_to_hop_toi_uu(dl, vung, nam, cac_dot, uu_tien="cai_tao_dat"):
    """Tự động gợi ý tổ hợp cây trồng tối ưu theo 4 Mục Tiêu Ưu Tiên của Nông Dân."""
    goi_y = {}

    for d in cac_dot:
        t_start, t_end = d["thang_bat_dau"], d["thang_ket_thuc"]

        if "tiet_kiem_nuoc" in uu_tien or "nước" in str(uu_tien).lower():
            # ƯU TIÊN 1: TIẾT KIỆM NƯỚC & CHỐNG HẠN
            if 1 <= t_start <= 4:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 70}, {"cay": "Lạc", "ty_le_pct": 30}]
            elif 5 <= t_start <= 7:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 60}, {"cay": "Ngô", "ty_le_pct": 40}]
            else:
                goi_y[d["ma"]] = [{"cay": "Ngô", "ty_le_pct": 70}, {"cay": "Rau màu vụ đông", "ty_le_pct": 30}]

        elif "cai_tao_dat" in uu_tien or "đất" in str(uu_tien).lower() or "sức khỏe" in str(uu_tien).lower():
            # ƯU TIÊN 2: CẢI TẠO & PHỤC HỒI SỨC KHỎE ĐẤT (CỐ ĐỊNH ĐẠM & PHƠI ẢI)
            if 1 <= t_start <= 4:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 60}, {"cay": "Lạc", "ty_le_pct": 40}]
            elif 5 <= t_start <= 7:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 70}, {"cay": "Lạc", "ty_le_pct": 30}]
            else:
                # Vụ đông để ải phơi nỏ đất diệt mầm đạo ôn
                goi_y[d["ma"]] = []

        elif "nang_suat" in uu_tien or "thu nhập" in str(uu_tien).lower() or "kinh tế" in str(uu_tien).lower():
            # ƯU TIÊN 3: TỐI ĐA HÓA NĂNG SUẤT & THU NHẬP
            if 1 <= t_start <= 4:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 100}]
            elif 5 <= t_start <= 7:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 100}]
            else:
                goi_y[d["ma"]] = [{"cay": "Rau màu vụ đông", "ty_le_pct": 100}]

        else:
            # ƯU TIÊN 4: AN TOÀN MÙA VỤ / NÉ THIÊN TAI (GIÓ LÀO & BÃO LŨ)
            if 1 <= t_start <= 4:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 80}, {"cay": "Lạc", "ty_le_pct": 20}]
            elif 5 <= t_start <= 7:
                goi_y[d["ma"]] = [{"cay": "Lúa", "ty_le_pct": 100}]
            else:
                goi_y[d["ma"]] = [{"cay": "Ngô", "ty_le_pct": 60}, {"cay": "Rau màu vụ đông", "ty_le_pct": 40}]

    return goi_y


def so_sanh_dot_qua_cac_nam(dl, vung, thang_bat_dau, thang_ket_thuc):
    """So sánh chỉ số khí hậu của một đợt qua các năm tại Yên Thành."""
    thangs = list(range(thang_bat_dau, thang_ket_thuc + 1))
    df_vung = dl[(dl.huyen == vung) & (dl.month.isin(thangs))]

    if df_vung.empty:
        return pd.DataFrame()

    ket_qua = []
    for y, g in df_vung.groupby("year"):
        so_thang_co = len(g)
        tmax_tb = g["tmax"].mean() if "tmax" in g.columns else np.nan
        tmax_max = g["tmax"].max() if "tmax" in g.columns else np.nan
        nong35_tong = g["nong35"].sum() if "nong35" in g.columns else np.nan
        mua_tong = g["mua_mm"].sum() if "mua_mm" in g.columns else np.nan
        nuoc_con_tong = g["nuoc_con_lai_mm"].sum() if "nuoc_con_lai_mm" in g.columns else np.nan
        sm_tb = g["sm_rootzone"].dropna().mean() * 100 if "sm_rootzone" in g.columns and not g["sm_rootzone"].dropna().empty else np.nan

        ket_qua.append({
            "nam": y,
            "so_thang": so_thang_co,
            "tmax_tb": round(tmax_tb, 1) if pd.notna(tmax_tb) else np.nan,
            "tmax_max": round(tmax_max, 1) if pd.notna(tmax_max) else np.nan,
            "nong35_tong": int(nong35_tong) if pd.notna(nong35_tong) else 0,
            "mua_tong_mm": round(mua_tong, 0) if pd.notna(mua_tong) else np.nan,
            "nuoc_con_mm": round(nuoc_con_tong, 0) if pd.notna(nuoc_con_tong) else np.nan,
            "sm_tb": round(sm_tb, 0) if pd.notna(sm_tb) else np.nan,
        })

    return pd.DataFrame(ket_qua).sort_values("nam")


def bang_diem(dl):
    """Tạo bảng điểm tháng cho cây lúa và cây luân canh tại Yên Thành."""
    if dl.empty:
        return pd.DataFrame()

    out = []
    for _, r in dl.iterrows():
        y, m, h = r.year, r.month, r.huyen
        tmax = r.tmax if "tmax" in r and pd.notna(r.tmax) else 30.0
        nong35 = r.nong35 if "nong35" in r and pd.notna(r.nong35) else 0
        mua = r.mua_mm if "mua_mm" in r and pd.notna(r.mua_mm) else 100.0
        sm = r.sm_rootzone if "sm_rootzone" in r and pd.notna(r.sm_rootzone) else 0.35

        for cay in CAY_VUNG.get(h, CAY.keys()):
            thong_tin = CAY.get(cay, {})
            lich = thong_tin.get("lich", {})
            if m not in lich:
                out.append({
                    "year": y, "month": m, "huyen": h, "cay": cay,
                    "rui_ro": np.nan, "muc": "Ngoài vụ", "mau": MAU_NGOAI_VU,
                    "giai_doan": "Ngoài thời vụ chính",
                    "ly_do": "Tháng này không thuộc lịch canh tác chuẩn tại Yên Thành.",
                    "dat_txt": thong_tin.get("dat", {}).get("mo_ta", ""),
                })
                continue

            gd, n_nong, n_han, n_ngap = lich[m]
            r_nong = min(100, max(0, (tmax - 30) * 12 * n_nong + nong35 * 4 * n_nong))
            r_han = min(100, max(0, (0.35 - sm) * 180 * n_han)) if sm < 0.35 else 5 * n_han
            r_ngap = min(100, max(0, (mua - 200) * 0.4 * n_ngap)) if mua > 200 else 5 * n_ngap
            rr = min(100, max(10, r_nong * 0.4 + r_han * 0.3 + r_ngap * 0.3))

            if cay == "Lúa":
                if 1 <= m <= 5:
                    ly_do = f"Vụ lúa xuân ({gd}): Chú ý giữ nước dưỡng đòng và phòng trừ đạo ôn cổ bông."
                elif 6 <= m <= 9:
                    ly_do = f"Vụ lúa hè thu ({gd}): Chống nắng nóng gió Lào và khẩn trương gặt chạy bão tháng 9."
                else:
                    ly_do = f"{gd}: Thời điểm cày ải đất hoặc làm vụ đông."
            elif cay == "Lạc":
                ly_do = f"{gd}: Đất cát pha thoát nước tốt, hạn chế ngập úng gốc."
            elif cay == "Ngô":
                ly_do = f"{gd}: Cần bảo đảm ẩm độ đất khi trổ cờ phun râu."
            else:
                ly_do = f"{gd}: Chăm sóc cây vụ đông trong tiết trời mát mẻ."

            muc = "Nên trồng" if rr < 35 else ("Cân nhắc" if rr < 55 else "Hạn chế")
            mau = "#22C55E" if rr < 35 else ("#F59E0B" if rr < 55 else "#EF4444")

            out.append({
                "year": y, "month": m, "huyen": h, "cay": cay,
                "rui_ro": rr, "muc": muc, "mau": mau,
                "giai_doan": gd,
                "ly_do": ly_do,
                "dat_txt": thong_tin.get("dat", {}).get("mo_ta", ""),
            })

    return pd.DataFrame(out)
