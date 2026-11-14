"""Bộ kiểm thử tự động toàn diện cho Hệ thống RotaNA (Vựa lúa Yên Thành).
Tuân thủ Bước 3: Test trong Chu trình Phát triển 4 bước của AgenticAI.
"""
import unittest
import pandas as pd
import numpy as np
import engine as E


class TestRotaNA(unittest.TestCase):
    """Kiểm thử tính toàn vẹn dữ liệu, thuật toán nông học và các view của RotaNA."""

    @classmethod
    def setUpClass(cls):
        """Khởi tạo dữ liệu dùng chung cho toàn bộ ca kiểm thử."""
        cls.dl = E.doc_thang()
        cls.nam_df = E.doc_nam()
        cls.tb_df = E.doc_tb()
        cls.diem = E.bang_diem(cls.dl) if len(cls.dl) else cls.dl
        cls.vung = "Yên Thành"
        cls.nam = 2026
        cls.thang = 4

    def test_01_du_lieu_chuoi_thoi_gian(self):
        """Kiểm tra dữ liệu chuỗi thời gian Yên Thành có đầy đủ các cột viễn thám."""
        self.assertFalse(self.dl.empty, "Dữ liệu chuỗi thời gian không được rỗng!")
        dl_yt = self.dl[self.dl.huyen == self.vung]
        self.assertFalse(dl_yt.empty, "Phải có dữ liệu riêng cho Huyện Yên Thành!")
        
        cot_yeu_cau = ["year", "month", "huyen", "tmax", "mua_mm", "nong35", "sm_rootzone", "ndvi"]
        for c in cot_yeu_cau:
            self.assertIn(c, dl_yt.columns, f"Thiếu cột dữ liệu cốt lõi: {c}")

    def test_02_thuat_toan_cham_diem_rui_ro(self):
        """Kiểm tra thuật toán chấm điểm rủi ro và khuyến nghị cây trồng."""
        self.assertFalse(self.diem.empty, "Bảng điểm rủi ro không được rỗng!")
        lua_yt = self.diem[(self.diem.huyen == self.vung) & (self.diem.cay == "Lúa") & (self.diem.month == self.thang)]
        self.assertFalse(lua_yt.empty, "Phải có kết quả chấm điểm cho Cây Lúa nước Yên Thành!")
        
        row = lua_yt.iloc[0]
        self.assertIsNotNone(row.get("rui_ro"), "Chỉ số rủi ro không được là None!")
        self.assertIn(row.get("muc"), ["Nên trồng", "Cân nhắc", "Hạn chế", "Ngoài vụ"], "Mức khuyến nghị phải thuộc danh mục chuẩn!")

    def test_03_thuat_toan_goi_y_luan_canh(self):
        """Kiểm tra thuật toán tự động gợi ý cơ cấu luân canh cây trồng tối ưu."""
        cac_dot = [
            {"ma": "xuan", "thang_bat_dau": 1, "thang_ket_thuc": 5, "ten": "Vụ Xuân"},
            {"ma": "hethu", "thang_bat_dau": 6, "thang_ket_thuc": 9, "ten": "Vụ Hè Thu"},
            {"ma": "dong", "thang_bat_dau": 10, "thang_ket_thuc": 12, "ten": "Vụ Đông"},
        ]
        goi_y = E.goi_y_to_hop_toi_uu(self.dl, self.vung, self.nam, cac_dot)
        self.assertIsInstance(goi_y, dict, "Kết quả gợi ý phải là một dictionary!")
        self.assertIn("xuan", goi_y, "Phải có gợi ý cho vụ Chiêm Xuân!")
        self.assertTrue(len(goi_y["xuan"]) > 0, "Vụ Xuân phải có ít nhất 1 cây trồng được gợi ý!")
        self.assertEqual(goi_y["xuan"][0]["cay"], "Lúa", "Vụ Xuân tại vựa lúa Yên Thành phải ưu tiên Cây Lúa!")

    def test_04_import_tat_ca_views(self):
        """Kiểm tra toàn bộ 7 module view trong hệ thống đều sẵn sàng hoạt động."""
        from views import tong_quan, ban_do, ve_tinh, luan_canh, so_sanh, ho_so_yen_thanh, du_lieu
        self.assertTrue(callable(tong_quan.hien), "tong_quan.hien phải là hàm gọi được!")
        self.assertTrue(callable(ban_do.hien_ban_do), "ban_do.hien_ban_do phải là hàm gọi được!")
        self.assertTrue(callable(ve_tinh.hien_ve_tinh), "ve_tinh.hien_ve_tinh phải là hàm gọi được!")
        self.assertTrue(callable(luan_canh.hien), "luan_canh.hien phải là hàm gọi được!")
        self.assertTrue(callable(so_sanh.hien), "so_sanh.hien phải là hàm gọi được!")
        self.assertTrue(callable(ho_so_yen_thanh.hien), "ho_so_yen_thanh.hien phải là hàm gọi được!")
        self.assertTrue(callable(du_lieu.hien), "du_lieu.hien phải là hàm gọi được!")


if __name__ == "__main__":
    unittest.main()
