import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_opcao_binomial import preco_binomial


class TestBinomial(unittest.TestCase):
    def test_um_passo_a_mao(self):
        u = math.exp(0.2)
        d = 1 / u
        p = (1 - d) / (u - d)
        esperado = p * (100 * u - 100)  # r = 0, só o ramo de alta paga
        self.assertAlmostEqual(preco_binomial(100, 100, 0.0, 0.2, 1, 1), esperado)

    def test_converge_para_black_scholes(self):
        self.assertAlmostEqual(preco_binomial(100, 100, 0.05, 0.2, 1, 1000), 10.4506, delta=0.02)
        self.assertAlmostEqual(
            preco_binomial(100, 100, 0.05, 0.2, 1, 1000, "put"), 5.5735, delta=0.02
        )

    def test_paridade_na_arvore(self):
        c = preco_binomial(100, 90, 0.04, 0.3, 1, 200)
        p = preco_binomial(100, 90, 0.04, 0.3, 1, 200, "put")
        self.assertAlmostEqual(c - p, 100 - 90 * math.exp(-0.04), places=9)

    def test_put_americana_vale_mais(self):
        eu = preco_binomial(100, 110, 0.05, 0.25, 1, 200, "put")
        am = preco_binomial(100, 110, 0.05, 0.25, 1, 200, "put", americana=True)
        self.assertGreater(am, eu)
        self.assertGreaterEqual(am, 10.0)  # valor intrínseco

    def test_call_americana_sem_dividendos_igual_europeia(self):
        eu = preco_binomial(100, 100, 0.05, 0.2, 1, 100)
        am = preco_binomial(100, 100, 0.05, 0.2, 1, 100, americana=True)
        self.assertAlmostEqual(eu, am, places=9)

    def test_erros(self):
        with self.assertRaises(ValueError):
            preco_binomial(100, 100, 0.05, 0.2, 1, 0)
        with self.assertRaises(ValueError):
            preco_binomial(100, 100, 0.05, 0.2, 1, 10, "x")
        with self.assertRaises(ValueError):
            preco_binomial(100, 100, 2.0, 0.01, 1, 1)  # p fora de [0, 1]


if __name__ == "__main__":
    unittest.main()
