import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_beta_alfa import alfa_jensen, beta, covariancia

B = [0.01, -0.02, 0.03, 0.0]


class TestBetaAlfa(unittest.TestCase):
    def test_covariancia(self):
        # desvios de B: 0.005, -0.025, 0.025, -0.005 ; soma dos quadrados 0.0013 ; /3
        self.assertAlmostEqual(covariancia(B, B), 0.0013 / 3)

    def test_beta_dobro(self):
        self.assertAlmostEqual(beta([2 * x for x in B], B), 2.0)

    def test_beta_negativo(self):
        self.assertAlmostEqual(beta([-x for x in B], B), -1.0)

    def test_alfa_constante(self):
        a = [2 * x + 0.001 for x in B]
        self.assertAlmostEqual(alfa_jensen(a, B), 0.001)

    def test_alfa_com_taxa_livre(self):
        # ativo = benchmark: beta 1, alfa 0 para qualquer rf
        self.assertAlmostEqual(alfa_jensen(B, B, 0.002), 0.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            beta([1, 2], [1])
        with self.assertRaises(ValueError):
            beta([1, 2, 3], [5, 5, 5])
        with self.assertRaises(ValueError):
            covariancia([1], [1])


if __name__ == "__main__":
    unittest.main()
