import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_flood import preencher_regiao

IMG = [
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 1, 1],
]


class TestImgFlood(unittest.TestCase):
    def test_conectividade_4(self):
        out = preencher_regiao(IMG, 0, 0, 7)
        self.assertEqual(out, [[7, 7, 1, 0], [7, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1]])

    def test_conectividade_8_atravessa_diagonal(self):
        out = preencher_regiao(IMG, 0, 0, 7, conectividade=8)
        self.assertEqual(out, [[7, 7, 1, 7], [7, 1, 7, 7], [1, 7, 7, 1], [7, 7, 1, 1]])

    def test_semente_em_outra_regiao(self):
        out = preencher_regiao(IMG, 3, 0, 5)
        self.assertEqual(out, [[0, 0, 1, 5], [0, 1, 5, 5], [1, 5, 5, 1], [5, 5, 1, 1]])

    def test_original_intacto(self):
        preencher_regiao(IMG, 0, 0, 9)
        self.assertEqual(IMG[0], [0, 0, 1, 0])

    def test_mesma_cor_nao_trava(self):
        self.assertEqual(preencher_regiao([[3, 3], [3, 3]], 0, 0, 3), [[3, 3], [3, 3]])

    def test_tolerancia(self):
        img = [[10, 12, 50], [11, 13, 51]]
        self.assertEqual(preencher_regiao(img, 0, 0, 0, tolerancia=3), [[0, 0, 50], [0, 0, 51]])

    def test_rgb(self):
        a, b = (255, 0, 0), (0, 0, 255)
        img = [[a, a, b], [b, a, b]]
        self.assertEqual(preencher_regiao(img, 0, 0, (0, 255, 0)),
                         [[(0, 255, 0), (0, 255, 0), b], [b, (0, 255, 0), b]])

    def test_erros(self):
        with self.assertRaises(ValueError):
            preencher_regiao(IMG, 4, 0, 1)
        with self.assertRaises(ValueError):
            preencher_regiao(IMG, 0, 0, 1, conectividade=5)


if __name__ == "__main__":
    unittest.main()
