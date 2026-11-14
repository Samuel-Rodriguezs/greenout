import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_recorte import adicionar_borda, colar, preencher_retangulo, recortar

IMG = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]


class TestImgRecorte(unittest.TestCase):
    def test_recortar(self):
        self.assertEqual(recortar(IMG, 1, 1, 2, 2), [[6, 7], [10, 11]])
        self.assertEqual(recortar(IMG, 0, 0, 4, 3), IMG)

    def test_recortar_copia(self):
        r = recortar(IMG, 0, 0, 2, 1)
        r[0][0] = 99
        self.assertEqual(IMG[0][0], 1)

    def test_recortar_invalido(self):
        for args in [(3, 0, 2, 1), (0, 2, 1, 2), (-1, 0, 1, 1), (0, 0, 0, 1)]:
            with self.assertRaises(ValueError):
                recortar(IMG, *args)

    def test_preencher_retangulo(self):
        out = preencher_retangulo(IMG, 1, 0, 2, 2, 0)
        self.assertEqual(out, [[1, 0, 0, 4], [5, 0, 0, 8], [9, 10, 11, 12]])
        self.assertEqual(IMG[0], [1, 2, 3, 4])

    def test_preencher_com_corte(self):
        out = preencher_retangulo(IMG, 3, 2, 5, 5, 7)
        self.assertEqual(out[2], [9, 10, 11, 7])
        self.assertEqual(out[1], [5, 6, 7, 8])
        self.assertEqual(preencher_retangulo(IMG, -2, -1, 3, 2, 0)[0], [0, 2, 3, 4])

    def test_adicionar_borda(self):
        out = adicionar_borda([[1, 2], [3, 4]], 1, 0, 2, 1, 9)
        self.assertEqual(out, [[9] * 5, [9, 9, 1, 2, 9], [9, 9, 3, 4, 9]])

    def test_borda_negativa(self):
        with self.assertRaises(ValueError):
            adicionar_borda(IMG, -1, 0, 0, 0)

    def test_colar(self):
        out = colar([[0] * 3 for _ in range(3)], [[1, 2], [3, 4]], 2, 1)
        self.assertEqual(out, [[0, 0, 0], [0, 0, 1], [0, 0, 3]])
        out = colar([[0] * 3 for _ in range(3)], [[1, 2], [3, 4]], -1, -1)
        self.assertEqual(out[0], [4, 0, 0])


if __name__ == "__main__":
    unittest.main()
