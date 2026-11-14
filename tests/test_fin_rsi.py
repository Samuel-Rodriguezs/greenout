import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_rsi import rsi


class TestRSI(unittest.TestCase):
    def test_wilder_a_mao(self):
        r = rsi([10, 11, 12, 11, 12, 13], 3)
        self.assertEqual(r[:3], [None] * 3)
        self.assertAlmostEqual(r[3], 100 - 100 / 3)
        self.assertAlmostEqual(r[4], 100 - 100 / 4.5)
        self.assertAlmostEqual(r[5], 100 - 100 / 6.75)

    def test_so_altas(self):
        self.assertEqual(rsi([1, 2, 3, 4], 2)[2:], [100.0, 100.0])

    def test_so_baixas(self):
        self.assertAlmostEqual(rsi([4, 3, 2, 1], 2)[3], 0.0)

    def test_serie_plana(self):
        self.assertEqual(rsi([5, 5, 5, 5], 2)[2], 50.0)

    def test_serie_curta(self):
        self.assertEqual(rsi([1, 2, 3], 3), [None] * 3)

    def test_periodo_invalido(self):
        with self.assertRaises(ValueError):
            rsi([1, 2], 0)


if __name__ == "__main__":
    unittest.main()
