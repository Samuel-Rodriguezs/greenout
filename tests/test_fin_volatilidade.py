import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_volatilidade import desvio_amostral, volatilidade, volatilidade_movel

R = [0.01, -0.01, 0.01, -0.01]


class TestVolatilidade(unittest.TestCase):
    def test_desvio(self):
        self.assertAlmostEqual(desvio_amostral(R), 0.01 * math.sqrt(4 / 3))

    def test_anualizada(self):
        self.assertAlmostEqual(volatilidade(R), 0.01 * math.sqrt(4 / 3) * math.sqrt(252))
        self.assertAlmostEqual(volatilidade(R, 1), 0.01 * math.sqrt(4 / 3))

    def test_constante_zero(self):
        self.assertEqual(volatilidade([0.02] * 5), 0.0)

    def test_movel(self):
        m = volatilidade_movel([0.01, -0.01, 0.03], 2, 1)
        self.assertIsNone(m[0])
        self.assertAlmostEqual(m[1], 0.01 * math.sqrt(2))
        self.assertAlmostEqual(m[2], 0.04 / math.sqrt(2))

    def test_poucos_dados(self):
        with self.assertRaises(ValueError):
            desvio_amostral([0.1])
        with self.assertRaises(ValueError):
            volatilidade_movel([0.1, 0.2], 1)


if __name__ == "__main__":
    unittest.main()
