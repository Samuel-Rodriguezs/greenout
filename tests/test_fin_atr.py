import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_atr import atr, true_range

H = [10, 12, 13]
L = [8, 9, 11]
C = [9, 11, 12]


class TestATR(unittest.TestCase):
    def test_true_range(self):
        self.assertEqual(true_range(H, L, C), [2, 3, 2])

    def test_true_range_gap(self):
        # abertura com gap de alta: máxima-mínima=1, mas |h - fech_ant|=6
        self.assertEqual(true_range([10, 16], [9, 15], [10, 15.5]), [1, 6])

    def test_atr_wilder(self):
        r = atr(H, L, C, 2)
        self.assertIsNone(r[0])
        self.assertAlmostEqual(r[1], 2.5)
        self.assertAlmostEqual(r[2], 2.25)

    def test_serie_curta(self):
        self.assertEqual(atr([1], [1], [1], 3), [None])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            atr([1], [1, 2], [1])
        with self.assertRaises(ValueError):
            atr([1], [1], [1], 0)


if __name__ == "__main__":
    unittest.main()
