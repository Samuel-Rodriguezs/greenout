import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_polinomio import avaliar, derivar, grau, multiplicar, normalizar, somar


class TestPolinomio(unittest.TestCase):
    def test_horner(self):
        self.assertEqual(avaliar([1, 2, 3], 2), 17)  # 1 + 2x + 3x^2
        self.assertAlmostEqual(avaliar([0.5, 0, 1], 1.5), 2.75)
        self.assertEqual(avaliar([], 3), 0)

    def test_soma(self):
        self.assertEqual(somar([1, 2], [3, 4, 5]), [4, 6, 5])
        self.assertEqual(somar([1, 2, 3], [0, 0, -3]), [1, 2])

    def test_produto(self):
        self.assertEqual(multiplicar([1, 1], [1, 1]), [1, 2, 1])
        self.assertEqual(multiplicar([1, -1], [1, 1]), [1, 0, -1])
        self.assertEqual(multiplicar([0], [1, 2]), [0])

    def test_grau_e_normalizar(self):
        self.assertEqual(grau([1, 2, 0, 0]), 1)
        self.assertEqual(normalizar([0, 0]), [0])
        self.assertEqual(grau([0]), 0)

    def test_derivada(self):
        self.assertEqual(derivar([5, 3, 2]), [3, 4])
        self.assertEqual(derivar([7]), [0])


if __name__ == "__main__":
    unittest.main()
