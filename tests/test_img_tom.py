import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_tom import ajustar_brilho, ajustar_contraste, corrigir_gama, inverter, limiarizar


class TestImgTom(unittest.TestCase):
    def test_brilho_com_saturacao(self):
        img = [[0, 10, 250], [100, 128, 255]]
        self.assertEqual(ajustar_brilho(img, 10), [[10, 20, 255], [110, 138, 255]])
        self.assertEqual(ajustar_brilho(img, -20), [[0, 0, 230], [80, 108, 235]])

    def test_contraste(self):
        img = [[100, 128, 200]]
        self.assertEqual(ajustar_contraste(img, 2), [[72, 128, 255]])
        self.assertEqual(ajustar_contraste(img, 0.5), [[114, 128, 164]])

    def test_gama(self):
        img = [[0, 64, 255]]
        self.assertEqual(corrigir_gama(img, 2), [[0, 128, 255]])
        self.assertEqual(corrigir_gama(img, 1), img)
        self.assertEqual(corrigir_gama([[128]], 0.5), [[64]])
        with self.assertRaises(ValueError):
            corrigir_gama(img, 0)

    def test_inverter(self):
        self.assertEqual(inverter([[0, 55], [200, 255]]), [[255, 200], [55, 0]])

    def test_inverter_duas_vezes(self):
        img = [[3, 4, 5], [250, 0, 128]]
        self.assertEqual(inverter(inverter(img)), img)

    def test_limiar(self):
        img = [[10, 127, 128], [200, 0, 255]]
        self.assertEqual(limiarizar(img, 128), [[0, 0, 255], [255, 0, 255]])
        self.assertEqual(limiarizar(img, 128, alto=1, baixo=0), [[0, 0, 1], [1, 0, 1]])


if __name__ == "__main__":
    unittest.main()
