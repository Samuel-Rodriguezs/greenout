import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_mediana import filtro_mediana, filtro_mediana_rgb


class TestImgMediana(unittest.TestCase):
    def test_remove_sal(self):
        img = [[10, 10, 10], [10, 255, 10], [10, 10, 10]]
        self.assertEqual(filtro_mediana(img), [[10] * 3] * 3)

    def test_remove_pimenta(self):
        img = [[200] * 5, [200, 200, 0, 200, 200], [200] * 5]
        self.assertEqual(filtro_mediana(img), [[200] * 5] * 3)

    def test_preserva_degrau(self):
        img = [[0, 0, 100, 100]] * 4
        self.assertEqual(filtro_mediana(img), img)

    def test_valores_conhecidos(self):
        img = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        out = filtro_mediana(img, 1, "zero")
        # centro: mediana de 1..9 = 5; canto (0,0): {0,0,0,0,0,1,2,4,5} -> 0
        self.assertEqual(out[1][1], 5)
        self.assertEqual(out[0][0], 0)
        # canto (0,0) com replicação: {1,1,2,1,1,2,4,4,5} ordenado -> 1,1,1,1,2,2,4,4,5 -> 2
        self.assertEqual(filtro_mediana(img)[0][0], 2)

    def test_raio_2(self):
        img = [[9] * 5 for _ in range(5)]
        img[2][2] = 0
        img[0][0] = 255
        self.assertEqual(filtro_mediana(img, 2), [[9] * 5] * 5)

    def test_rgb_por_canal(self):
        base = (10, 20, 30)
        img = [[base] * 3, [base, (255, 0, 99), base], [base] * 3]
        self.assertEqual(filtro_mediana_rgb(img), [[base] * 3] * 3)

    def test_raio_invalido(self):
        with self.assertRaises(ValueError):
            filtro_mediana([[1]], 0)


if __name__ == "__main__":
    unittest.main()
