import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_regressao import prever, r_quadrado, regressao_linear


class TestRegressao(unittest.TestCase):
    def test_reta_exata(self):
        a, b = regressao_linear([0, 1, 2, 3], [1, 3, 5, 7])
        self.assertAlmostEqual(a, 2.0)
        self.assertAlmostEqual(b, 1.0)

    def test_dados_ruidosos(self):
        a, b = regressao_linear([1, 2, 3, 4, 5], [2.2, 4.1, 6.2, 7.9, 10.1])
        self.assertAlmostEqual(a, 1.96, places=6)
        self.assertAlmostEqual(b, 0.22, places=6)

    def test_prever(self):
        self.assertAlmostEqual(prever((2.0, 1.0), 10), 21.0)

    def test_r2(self):
        self.assertAlmostEqual(r_quadrado([0, 1, 2], [1, 3, 5]), 1.0)
        self.assertLess(r_quadrado([1, 2, 3, 4], [1, 3, 2, 4]), 1.0)
        self.assertEqual(r_quadrado([1, 2, 3], [4, 4, 4]), 1.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            regressao_linear([1, 2], [1])
        with self.assertRaises(ValueError):
            regressao_linear([1], [1])
        with self.assertRaises(ValueError):
            regressao_linear([2, 2, 2], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
