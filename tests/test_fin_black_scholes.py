import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_black_scholes import gregas, preco_call, preco_put, volatilidade_implicita


class TestBlackScholes(unittest.TestCase):
    def test_valores_de_referencia(self):
        self.assertAlmostEqual(preco_call(100, 100, 0.05, 0.2, 1), 10.4506, places=3)
        self.assertAlmostEqual(preco_put(100, 100, 0.05, 0.2, 1), 5.5735, places=3)

    def test_paridade_put_call(self):
        c = preco_call(120, 100, 0.03, 0.25, 0.5)
        p = preco_put(120, 100, 0.03, 0.25, 0.5)
        self.assertAlmostEqual(c - p, 120 - 100 * math.exp(-0.03 * 0.5))

    def test_paridade_com_dividendos(self):
        c = preco_call(100, 95, 0.04, 0.3, 2, q=0.02)
        p = preco_put(100, 95, 0.04, 0.3, 2, q=0.02)
        self.assertAlmostEqual(c - p, 100 * math.exp(-0.04) - 95 * math.exp(-0.08))

    def test_vencimento_e_sigma_zero(self):
        self.assertEqual(preco_call(110, 100, 0.05, 0.2, 0), 10)
        self.assertEqual(preco_put(90, 100, 0.05, 0.2, 0), 10)
        self.assertEqual(preco_call(90, 100, 0.05, 0.2, 0), 0)
        self.assertAlmostEqual(preco_call(100, 100, 0.05, 0.0, 1), 100 - 100 * math.exp(-0.05))

    def test_gregas(self):
        g = gregas(100, 100, 0.05, 0.2, 1)
        self.assertAlmostEqual(g["delta"], 0.6368, places=3)
        self.assertAlmostEqual(g["gamma"], 0.018762, places=5)
        self.assertAlmostEqual(g["vega"], 37.524, places=2)
        gp = gregas(100, 100, 0.05, 0.2, 1, "put")
        self.assertAlmostEqual(gp["delta"], g["delta"] - 1)

    def test_vol_implicita(self):
        p = preco_call(100, 105, 0.02, 0.35, 0.75)
        self.assertAlmostEqual(volatilidade_implicita(p, 100, 105, 0.02, 0.75), 0.35, places=6)
        q = preco_put(100, 105, 0.02, 0.18, 0.75)
        self.assertAlmostEqual(volatilidade_implicita(q, 100, 105, 0.02, 0.75, "put"), 0.18, places=6)

    def test_erros(self):
        with self.assertRaises(ValueError):
            preco_call(0, 100, 0.05, 0.2, 1)
        with self.assertRaises(ValueError):
            preco_put(100, 100, 0.05, -0.2, 1)
        with self.assertRaises(ValueError):
            gregas(100, 100, 0.05, 0.2, 0)
        with self.assertRaises(ValueError):
            gregas(100, 100, 0.05, 0.2, 1, "x")
        with self.assertRaises(ValueError):
            volatilidade_implicita(0.0, 100, 100, 0.05, 1)


if __name__ == "__main__":
    unittest.main()
