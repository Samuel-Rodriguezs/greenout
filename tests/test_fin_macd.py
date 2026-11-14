import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_macd import ema_continua, macd


class TestMACD(unittest.TestCase):
    def test_ema_continua(self):
        r = ema_continua([1, 2, 3, 4], 3)
        for a, b in zip(r, [1, 1.5, 2.25, 3.125]):
            self.assertAlmostEqual(a, b)

    def test_macd_a_mao(self):
        r = macd([1, 2, 3, 4], rapida=2, lenta=3, sinal=2)
        esperado = [0, 1 / 6, 0.3055555556, 0.3935185185]
        for a, b in zip(r.macd, esperado):
            self.assertAlmostEqual(a, b)
        self.assertAlmostEqual(r.sinal[1], 1 / 9)
        self.assertAlmostEqual(r.sinal[2], 0.2407407407)
        self.assertAlmostEqual(r.histograma[2], 0.3055555556 - 0.2407407407)

    def test_serie_constante(self):
        r = macd([5.0] * 10, 2, 3, 2)
        self.assertTrue(all(abs(x) < 1e-12 for x in r.histograma))

    def test_periodos_invalidos(self):
        with self.assertRaises(ValueError):
            macd([1, 2], rapida=5, lenta=3)


if __name__ == "__main__":
    unittest.main()
