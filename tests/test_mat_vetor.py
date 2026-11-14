import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from mat_vetor import (angulo, escalar_por, norma, produto_escalar,
                       produto_vetorial, soma)


class TestVetor(unittest.TestCase):
    def test_escalar(self):
        self.assertEqual(produto_escalar([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(produto_escalar([], []), 0)

    def test_vetorial(self):
        self.assertEqual(produto_vetorial([1, 0, 0], [0, 1, 0]), [0, 0, 1])
        self.assertEqual(produto_vetorial([0, 1, 0], [1, 0, 0]), [0, 0, -1])
        self.assertEqual(produto_vetorial([2, 3, 4], [2, 3, 4]), [0, 0, 0])
        v = produto_vetorial([1, 2, 3], [4, 5, 6])
        self.assertEqual(v, [-3, 6, -3])
        self.assertEqual(produto_escalar(v, [1, 2, 3]), 0)

    def test_norma_soma(self):
        self.assertAlmostEqual(norma([3, 4]), 5.0)
        self.assertEqual(soma([1, 2], [3, 4]), [4, 6])
        self.assertEqual(escalar_por(2, [1, -1]), [2, -2])

    def test_angulo(self):
        self.assertAlmostEqual(angulo([1, 0], [0, 1]), math.pi / 2)
        self.assertAlmostEqual(angulo([1, 0], [-1, 0]), math.pi)
        self.assertAlmostEqual(angulo([2, 0], [5, 0]), 0.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            produto_escalar([1], [1, 2])
        with self.assertRaises(ValueError):
            produto_vetorial([1, 2], [3, 4])
        with self.assertRaises(ValueError):
            angulo([0, 0], [1, 1])


if __name__ == "__main__":
    unittest.main()
