import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_retornos import (
    retorno_acumulado,
    retorno_anualizado,
    retornos_log,
    retornos_simples,
)


class TestRetornos(unittest.TestCase):
    def test_simples(self):
        r = retornos_simples([100, 110, 99])
        self.assertAlmostEqual(r[0], 0.1)
        self.assertAlmostEqual(r[1], -0.1)

    def test_log_soma_igual_log_total(self):
        p = [100, 110, 99, 120]
        self.assertAlmostEqual(sum(retornos_log(p)), math.log(1.2))
        self.assertAlmostEqual(retornos_log(p)[0], math.log(1.1))

    def test_acumulado(self):
        self.assertAlmostEqual(retorno_acumulado(retornos_simples([100, 110, 99])), -0.01)
        self.assertEqual(retorno_acumulado([]), 0.0)

    def test_anualizado(self):
        self.assertAlmostEqual(retorno_anualizado(0.21, 126), 1.21**2 - 1)
        self.assertAlmostEqual(retorno_anualizado(0.1, 252), 0.1)

    def test_erros(self):
        with self.assertRaises(ValueError):
            retornos_simples([1, 0])
        with self.assertRaises(ValueError):
            retorno_anualizado(0.1, 0)
        with self.assertRaises(ValueError):
            retorno_anualizado(-1.0, 10)

    def test_serie_unitaria(self):
        self.assertEqual(retornos_simples([5]), [])


if __name__ == "__main__":
    unittest.main()
