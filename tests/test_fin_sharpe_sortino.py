import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_sharpe_sortino import sharpe, sortino

R = [0.02, -0.01, 0.03, 0.0]


class TestSharpeSortino(unittest.TestCase):
    def test_sharpe_periodico(self):
        self.assertAlmostEqual(sharpe(R, 0.0, 1), 0.01 / math.sqrt(0.001 / 3))

    def test_sharpe_anualizado(self):
        self.assertAlmostEqual(sharpe(R), sharpe(R, 0.0, 1) * math.sqrt(252))

    def test_sharpe_taxa_livre(self):
        # excessos: 0.01, -0.02, 0.02, -0.01 -> média 0 -> sharpe 0
        self.assertAlmostEqual(sharpe(R, 0.01, 1), 0.0)

    def test_sortino(self):
        self.assertAlmostEqual(sortino(R, 0.0, 1), 2.0)
        self.assertAlmostEqual(sortino(R), 2.0 * math.sqrt(252))

    def test_sortino_alvo(self):
        # alvo 0.01: abaixo = 0.0 (-0.01 -> -0.02), -0.01 (0.0) etc.
        # desvios: 0.01, -0.02, 0.02, -0.01 -> quadrados negativos 4e-4 + 1e-4
        esperado = (0.01 - 0.01) / math.sqrt(5e-4 / 4)
        self.assertAlmostEqual(sortino(R, 0.01, 1), esperado)

    def test_bordas(self):
        with self.assertRaises(ValueError):
            sharpe([0.01])
        with self.assertRaises(ValueError):
            sharpe([0.01, 0.01])
        with self.assertRaises(ValueError):
            sortino([0.01, 0.02])
        with self.assertRaises(ValueError):
            sortino([])


if __name__ == "__main__":
    unittest.main()
