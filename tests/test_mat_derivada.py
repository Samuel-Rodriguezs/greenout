import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from mat_derivada import (diferenca_central, diferenca_progressiva,
                          diferenca_regressiva, segunda_derivada)


class TestDerivada(unittest.TestCase):
    def test_central_polinomio(self):
        self.assertAlmostEqual(diferenca_central(lambda x: x ** 3, 2.0), 12.0, places=5)

    def test_progressiva_e_regressiva(self):
        self.assertAlmostEqual(diferenca_progressiva(math.exp, 0.0), 1.0, places=4)
        self.assertAlmostEqual(diferenca_regressiva(math.exp, 0.0), 1.0, places=4)

    def test_seno(self):
        self.assertAlmostEqual(diferenca_central(math.sin, 0.0), 1.0, places=8)

    def test_constante(self):
        self.assertAlmostEqual(diferenca_central(lambda x: 7.0, 3.0), 0.0, places=10)

    def test_segunda_derivada(self):
        self.assertAlmostEqual(segunda_derivada(lambda x: x ** 3, 2.0), 12.0, places=3)
        self.assertAlmostEqual(segunda_derivada(lambda x: x * x, 5.0), 2.0, places=3)


if __name__ == "__main__":
    unittest.main()
