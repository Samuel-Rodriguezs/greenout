import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_monte_carlo import preco_opcao_mc, simular_caminhos


class TestMonteCarlo(unittest.TestCase):
    def test_forma(self):
        c = simular_caminhos(100, 0.05, 0.2, 1, 12, 7, seed=1)
        self.assertEqual(len(c), 7)
        self.assertTrue(all(len(x) == 13 and x[0] == 100 for x in c))
        self.assertTrue(all(p > 0 for x in c for p in x))

    def test_reprodutivel_por_seed(self):
        a = simular_caminhos(100, 0.05, 0.2, 1, 5, 3, seed=42)
        b = simular_caminhos(100, 0.05, 0.2, 1, 5, 3, seed=42)
        c = simular_caminhos(100, 0.05, 0.2, 1, 5, 3, seed=43)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_sem_volatilidade_e_deterministico(self):
        c = simular_caminhos(100, 0.05, 0.0, 2, 4, 2, seed=0)
        for caminho in c:
            self.assertAlmostEqual(caminho[-1], 100 * math.exp(0.10))

    def test_media_terminal(self):
        c = simular_caminhos(100, 0.05, 0.2, 1, 1, 20000, seed=7)
        media = sum(x[-1] for x in c) / len(c)
        self.assertAlmostEqual(media, 100 * math.exp(0.05), delta=1.0)

    def test_opcao_proxima_de_black_scholes(self):
        preco, erro = preco_opcao_mc(100, 100, 0.05, 0.2, 1, 20000, seed=3)
        self.assertAlmostEqual(preco, 10.4506, delta=max(4 * erro, 0.01))
        self.assertLess(erro, 0.2)
        put, _ = preco_opcao_mc(100, 100, 0.05, 0.2, 1, 20000, "put", seed=3)
        self.assertAlmostEqual(put, 5.5735, delta=0.3)

    def test_opcao_deterministica(self):
        preco, erro = preco_opcao_mc(100, 90, 0.0, 0.0, 1, 10)
        self.assertAlmostEqual(preco, 10.0)
        self.assertAlmostEqual(erro, 0.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            simular_caminhos(0, 0.05, 0.2, 1, 1, 1)
        with self.assertRaises(ValueError):
            simular_caminhos(100, 0.05, 0.2, 1, 0, 1)
        with self.assertRaises(ValueError):
            preco_opcao_mc(100, 100, 0.05, 0.2, 1, 10, "x")


if __name__ == "__main__":
    unittest.main()
