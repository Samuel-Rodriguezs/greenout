import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_matriz import (determinante, identidade, inversa, multiplicar,
                        resolver_sistema, transposta)


class TestMatriz(unittest.TestCase):
    def test_transposta(self):
        self.assertEqual(transposta([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])

    def test_multiplicar(self):
        self.assertEqual(multiplicar([[1, 2], [3, 4]], [[5, 6], [7, 8]]), [[19, 22], [43, 50]])
        with self.assertRaises(ValueError):
            multiplicar([[1, 2]], [[1, 2]])

    def test_determinante(self):
        self.assertAlmostEqual(determinante([[1, 2], [3, 4]]), -2.0)
        # 2*(3-2) - 0*(1-2) + 1*(1-3) = 0
        self.assertAlmostEqual(determinante([[2, 0, 1], [1, 3, 2], [1, 1, 1]]), 0.0)
        self.assertAlmostEqual(determinante([[2, 1, 0], [1, 3, 1], [0, 1, 4]]), 18.0)
        self.assertAlmostEqual(determinante([[0, 1], [1, 0]]), -1.0)
        self.assertEqual(determinante([[1, 2], [2, 4]]), 0.0)
        self.assertAlmostEqual(determinante([[5]]), 5.0)

    def test_inversa(self):
        m = [[4, 7], [2, 6]]
        prod = multiplicar(m, inversa(m))
        for i, l in enumerate(identidade(2)):
            for j, v in enumerate(l):
                self.assertAlmostEqual(prod[i][j], v)

    def test_singular(self):
        with self.assertRaises(ValueError):
            inversa([[1, 2], [2, 4]])

    def test_nao_quadrada(self):
        with self.assertRaises(ValueError):
            determinante([[1, 2, 3], [4, 5, 6]])

    def test_sistema(self):
        x = resolver_sistema([[2, 1], [1, 3]], [5, 10])
        self.assertAlmostEqual(x[0], 1.0)
        self.assertAlmostEqual(x[1], 3.0)


if __name__ == "__main__":
    unittest.main()
