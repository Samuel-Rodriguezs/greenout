import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_redimensiona import bilinear, vizinho_mais_proximo


class TestImgRedimensiona(unittest.TestCase):
    def test_vizinho_ampliar(self):
        out = vizinho_mais_proximo([[1, 2], [3, 4]], 4, 4)
        self.assertEqual(out, [[1, 1, 2, 2], [1, 1, 2, 2], [3, 3, 4, 4], [3, 3, 4, 4]])

    def test_vizinho_reduzir(self):
        img = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
        self.assertEqual(vizinho_mais_proximo(img, 2, 2), [[1, 3], [9, 11]])

    def test_vizinho_proporcao_nao_inteira(self):
        out = vizinho_mais_proximo([[1, 2], [3, 4]], 3, 1)
        self.assertEqual(out, [[1, 1, 2]])

    def test_vizinho_rgb(self):
        img = [[(1, 2, 3), (4, 5, 6)]]
        self.assertEqual(vizinho_mais_proximo(img, 4, 1),
                         [[(1, 2, 3), (1, 2, 3), (4, 5, 6), (4, 5, 6)]])

    def test_bilinear_2x2_para_3x3(self):
        out = bilinear([[0, 100], [100, 200]], 3, 3)
        self.assertEqual(out, [[0, 50, 100], [50, 100, 150], [100, 150, 200]])

    def test_bilinear_mesmo_tamanho(self):
        img = [[10, 20, 30], [40, 50, 60]]
        self.assertEqual(bilinear(img, 3, 2), img)

    def test_bilinear_dobro_horizontal(self):
        # destino x=0..3 -> origem -0.25, 0.25, 0.75, 1.25 (com limites 0 e 1)
        out = bilinear([[0, 100]], 4, 1)
        self.assertEqual(out, [[0, 25, 75, 100]])

    def test_bilinear_rgb(self):
        img = [[(0, 0, 0), (100, 200, 50)]]
        self.assertEqual(bilinear(img, 4, 1),
                         [[(0, 0, 0), (25, 50, 12), (75, 150, 38), (100, 200, 50)]])

    def test_bilinear_reduzir_media(self):
        out = bilinear([[0, 100, 200, 100]], 2, 1)
        self.assertEqual(out, [[50, 150]])

    def test_dimensoes_invalidas(self):
        with self.assertRaises(ValueError):
            bilinear([[1]], 0, 1)
        with self.assertRaises(ValueError):
            vizinho_mais_proximo([[1]], 1, -1)


if __name__ == "__main__":
    unittest.main()
