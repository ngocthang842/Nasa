"""Trang cây theo vùng."""
import pandas as pd
import streamlit as st

import engine as E
from views.chung import tieu_de


def _dat_ngan(dl, h, nam, thang):
    q = dl[(dl.huyen == h) & (dl.year == nam) & (dl.month == thang)]
    if q.empty:
        return ""
    r = q.iloc[0]
    bit = []
    if "ph" in r and pd.notna(r.ph):
        bit.append(f"pH {r.ph:.1f}")
    if "cat_pct" in r and pd.notna(r.cat_pct):
        bit.append(f"cát {r.cat_pct:.0f}%")
    if "set_pct" in r and pd.notna(r.set_pct):
        bit.append(f"sét {r.set_pct:.0f}%")
    return " · ".join(bit)


def hien(ctx):
    dl, diem = ctx["dl"], ctx["diem"]
    nam, thang = ctx["nam"], ctx["thang"]
    tieu_de(ctx["vung"], thang, nam, "Cây theo vùng", len(ctx["years"]) < 2)
    st.caption("Mỗi vùng chỉ nói về cây người dân trồng nhiều. Đây là cách đọc nhanh, không phải bảng nguồn báo. Lịch vụ một số cây vẫn là ước lượng, cần cán bộ khuyến nông xác nhận.")
    cols = st.columns(len(ctx["huyens"]) or 1)
    for col, h in zip(cols, ctx["huyens"]):
        with col, st.container(border=True):
            st.markdown(f"**{h}** · {E.VUNG.get(h, '')}")
            cau = [c for hh, _, c in E.GIOI_THIEU if hh == h]
            if cau:
                st.write(" ".join(cau[:2]))
            dat = _dat_ngan(dl, h, nam, thang)
            if dat:
                st.markdown(f'<p class="cap">Đất</p><p style="color:#5B6E86;margin-top:-6px">{dat}</p>', unsafe_allow_html=True)
            for hh, cay, _ in E.GIOI_THIEU:
                if hh != h:
                    continue
                d = E.CAY[cay].get("dat") or {}
                muc, mau = "—", "#5B6B79"
                if len(diem):
                    q = diem[(diem.huyen == h) & (diem.year == nam) & (diem.month == thang) & (diem.cay == cay)]
                    if len(q):
                        muc, mau = q.iloc[0].muc, q.iloc[0].mau
                mo = d.get("mo_ta", "Chưa có mô tả đất.")
                st.markdown(
                    f'<div class="crop" style="--c:{mau}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center">'
                    f'<b>{cay}</b>'
                    f'<span style="font-size:12px;font-weight:650;color:{mau};border:1px solid {mau};border-radius:999px;padding:2px 8px">{muc}</span>'
                    f'</div><div class="r">{mo}</div></div>',
                    unsafe_allow_html=True,
                )