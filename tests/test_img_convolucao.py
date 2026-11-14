import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_convolucao import convolver, correlacionar, indice_borda, limitar

IMG = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
SOMA = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]


class TestImgConvolucao(unittest.TestCase):
    def test_indice_borda(self):
        self.assertEqual([indice_borda(i, 3, "replicar") for i in (-2, -1, 3, 5)], [0, 0, 2, 2])
        self.assertEqual([indice_borda(i, 3, "espelhar") for i in (-2, -1, 3, 4)], [2, 1, 1, 0])
        self.assertEqual([indice_borda(i, 3, "circular") for i in (-1, 3, 4)], [2, 0, 1])
        self.assertIsNone(indice_borda(-1, 3, "zero"))
        self.assertEqual(indice_borda(-3, 1, "espelhar"), 0)
        with self.assertRaises(ValueError):
            indice_borda(-1, 3, "xyz")

    def test_identidade(self):
        ident = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
        self.assertEqual(convolver(IMG, ident), [[float(v) for v in l] for l in IMG])

    def test_convolucao_inverte_kernel(self):
        k = [[0, 0, 0], [0, 0, 1], [0, 0, 0]]
        self.assertEqual(convolver(IMG, k, "zero"), [[0, 1, 2], [0, 4, 5], [0, 7, 8]])
        self.assertEqual(convolver(IMG, k, "replicar"), [[1, 1, 2], [4, 4, 5], [7, 7, 8]])

    def test_correlacao_nao_inverte(self):
        k = [[0, 0, 0], [0, 0, 1], [0, 0, 0]]
        self.assertEqual(correlacionar(IMG, k, "zero"), [[2, 3, 0], [5, 6, 0], [8, 9, 0]])

    def test_soma_3x3_em_cada_borda(self):
        self.assertEqual(correlacionar(IMG, SOMA, "zero")[1][1], 45)
        self.assertEqual(correlacionar(IMG, SOMA, "zero")[0][0], 12)
        self.assertEqual(correlacionar(IMG, SOMA, "replicar")[0][0], 21)
        self.assertEqual(correlacionar(IMG, SOMA, "espelhar")[0][0], 33)
        self.assertEqual(correlacionar(IMG, SOMA, "circular")[0][0], 45)

    def test_divisor(self):
        self.assertEqual(correlacionar(IMG, SOMA, "zero", 9)[1][1], 5.0)

    def test_kernel_invalido(self):
        with self.assertRaises(ValueError):
            correlacionar(IMG, [[1, 1], [1, 1]])
        with self.assertRaises(ValueError):
            correlacionar(IMG, SOMA, divisor=0)

    def test_limitar(self):
        self.assertEqual(limitar([[-5.2, 0.4, 127.5, 300.0]]), [[0, 0, 128, 255]])


if __name__ == "__main__":
    unittest.main()
