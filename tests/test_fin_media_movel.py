import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_media_movel import ema, sma


class TestMediaMovel(unittest.TestCase):
    def test_sma(self):
        r = sma([1, 2, 3, 4, 5], 3)
        self.assertEqual(r[:2], [None, None])
        self.assertEqual(r[2:], [2.0, 3.0, 4.0])

    def test_sma_janela_1(self):
        self.assertEqual(sma([4, 5], 1), [4.0, 5.0])

    def test_ema_semente_sma(self):
        r = ema([1, 2, 3, 4, 5], 3)
        self.assertEqual(r[:2], [None, None])
        self.assertAlmostEqual(r[2], 2.0)
        self.assertAlmostEqual(r[3], 3.0)
        self.assertAlmostEqual(r[4], 4.0)

    def test_ema_serie_curta(self):
        self.assertEqual(ema([1, 2], 5), [None, None])

    def test_janela_invalida(self):
        with self.assertRaises(ValueError):
            sma([1], 0)
        with self.assertRaises(ValueError):
            ema([1], -1)


if __name__ == "__main__":
    unittest.main()
