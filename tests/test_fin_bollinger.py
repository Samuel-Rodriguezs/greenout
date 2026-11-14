import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from fin_bollinger import bollinger, percentual_b


class TestBollinger(unittest.TestCase):
    def test_a_mao(self):
        b = bollinger([1, 2, 3], 3, 2)
        dp = math.sqrt(2 / 3)
        self.assertEqual(b.media[:2], [None, None])
        self.assertAlmostEqual(b.media[2], 2.0)
        self.assertAlmostEqual(b.superior[2], 2 + 2 * dp)
        self.assertAlmostEqual(b.inferior[2], 2 - 2 * dp)

    def test_serie_constante_colapsa(self):
        b = bollinger([7, 7, 7, 7], 2)
        self.assertEqual(b.superior[3], 7.0)
        self.assertEqual(b.inferior[3], 7.0)

    def test_percentual_b(self):
        self.assertAlmostEqual(percentual_b(12, 14, 10), 0.5)
        self.assertAlmostEqual(percentual_b(10, 14, 10), 0.0)
        self.assertAlmostEqual(percentual_b(15, 14, 10), 1.25)
        self.assertEqual(percentual_b(5, 5, 5), 0.5)

    def test_n_invalido(self):
        with self.assertRaises(ValueError):
            bollinger([1], 0)


if __name__ == "__main__":
    unittest.main()
