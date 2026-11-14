import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_janelas as j


class TestJanelas(unittest.TestCase):
    def test_hann(self):
        w = j.hann(5)
        self.assertAlmostEqual(w[0], 0.0)
        self.assertAlmostEqual(w[1], 0.5)
        self.assertAlmostEqual(w[2], 1.0)
        self.assertAlmostEqual(w[4], 0.0)

    def test_hamming(self):
        w = j.hamming(5)
        self.assertAlmostEqual(w[0], 0.08)
        self.assertAlmostEqual(w[2], 1.0)

    def test_blackman(self):
        w = j.blackman(5)
        self.assertAlmostEqual(w[0], 0.0, places=9)
        self.assertAlmostEqual(w[1], 0.34, places=9)
        self.assertAlmostEqual(w[2], 1.0)

    def test_simetria(self):
        for f in (j.hann, j.hamming, j.blackman):
            w = f(16)
            for a, b in zip(w, reversed(w)):
                self.assertAlmostEqual(a, b)

    def test_bordas(self):
        self.assertEqual(j.hann(0), [])
        self.assertEqual(j.hamming(1), [1.0])
        with self.assertRaises(ValueError):
            j.hann(-1)

    def test_aplicar(self):
        self.assertEqual(j.aplicar([2, 2, 2], [0, 1, 0.5]), [0, 2, 1])
        with self.assertRaises(ValueError):
            j.aplicar([1], [1, 2])

    def test_ganho(self):
        self.assertEqual(j.ganho_coerente(j.retangular(4)), 1.0)
        self.assertEqual(j.ganho_coerente([]), 0.0)


if __name__ == "__main__":
    unittest.main()
