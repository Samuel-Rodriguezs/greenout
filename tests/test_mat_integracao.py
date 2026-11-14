import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from mat_integracao import simpson, trapezio


class TestIntegracao(unittest.TestCase):
    def test_trapezio_linear_exato(self):
        self.assertAlmostEqual(trapezio(lambda x: 2 * x + 1, 0, 3, 10), 12.0, places=10)

    def test_trapezio_seno(self):
        self.assertAlmostEqual(trapezio(math.sin, 0, math.pi, 10000), 2.0, places=6)

    def test_simpson_cubica_exata(self):
        self.assertAlmostEqual(simpson(lambda x: x ** 3, 0, 2, 2), 4.0, places=10)

    def test_simpson_exponencial(self):
        self.assertAlmostEqual(simpson(math.exp, 0, 1, 100), math.e - 1, places=8)

    def test_intervalo_invertido(self):
        self.assertAlmostEqual(simpson(lambda x: x, 1, 0, 4), -0.5, places=10)

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            simpson(math.sin, 0, 1, 3)
        with self.assertRaises(ValueError):
            trapezio(math.sin, 0, 1, 0)


if __name__ == "__main__":
    unittest.main()
