import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_cor import cinza_para_rgb, hsv_para_rgb, pixel_para_cinza, rgb_para_cinza, rgb_para_hsv


class TestImgCor(unittest.TestCase):
    def test_cinza_primarias(self):
        img = [[(255, 0, 0), (0, 255, 0)], [(0, 0, 255), (255, 255, 255)]]
        self.assertEqual(rgb_para_cinza(img), [[76, 150], [29, 255]])

    def test_cinza_neutro_preservado(self):
        self.assertEqual(pixel_para_cinza((100, 100, 100)), 100)

    def test_cinza_para_rgb(self):
        self.assertEqual(cinza_para_rgb([[5, 9]]), [[(5, 5, 5), (9, 9, 9)]])

    def test_hsv_primarias(self):
        self.assertEqual(rgb_para_hsv((255, 0, 0)), (0.0, 1.0, 1.0))
        self.assertEqual(rgb_para_hsv((0, 255, 0)), (120.0, 1.0, 1.0))
        self.assertEqual(rgb_para_hsv((0, 0, 255)), (240.0, 1.0, 1.0))
        self.assertEqual(rgb_para_hsv((255, 255, 0))[0], 60.0)

    def test_hsv_sem_saturacao(self):
        h, s, v = rgb_para_hsv((51, 51, 51))
        self.assertEqual((h, s), (0.0, 0.0))
        self.assertAlmostEqual(v, 0.2)
        self.assertEqual(rgb_para_hsv((0, 0, 0)), (0.0, 0.0, 0.0))

    def test_hsv_para_rgb(self):
        self.assertEqual(hsv_para_rgb((0, 1, 1)), (255, 0, 0))
        self.assertEqual(hsv_para_rgb((180, 1, 1)), (0, 255, 255))
        self.assertEqual(hsv_para_rgb((300, 1, 0.5)), (128, 0, 128))
        self.assertEqual(hsv_para_rgb((360, 1, 1)), (255, 0, 0))

    def test_ida_e_volta(self):
        for p in [(12, 200, 99), (255, 128, 0), (0, 0, 0), (77, 77, 77), (1, 2, 250)]:
            self.assertEqual(hsv_para_rgb(rgb_para_hsv(p)), p)


if __name__ == "__main__":
    unittest.main()
