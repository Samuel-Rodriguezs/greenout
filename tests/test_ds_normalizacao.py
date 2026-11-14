import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_normalizacao as n


class TestNormalizacao(unittest.TestCase):
    def test_min_max(self):
        self.assertEqual(n.min_max([1, 2, 3]), [0.0, 0.5, 1.0])
        self.assertEqual(n.min_max([10, 20, 30], -1, 1), [-1.0, 0.0, 1.0])
        self.assertEqual(n.min_max([5, 5]), [0.0, 0.0])

    def test_inversa_min_max(self):
        orig = [3.0, 8.0, 5.5]
        lo, hi = n.parametros_minmax(orig)
        volta = n.desfazer_min_max(n.min_max(orig), lo, hi)
        for a, b in zip(orig, volta):
            self.assertAlmostEqual(a, b)

    def test_z_score(self):
        z = n.z_score([1, 2, 3])
        self.assertAlmostEqual(z[0], -1.2247449, places=6)
        self.assertAlmostEqual(z[1], 0.0)
        self.assertAlmostEqual(z[2], 1.2247449, places=6)
        self.assertEqual(n.z_score([4, 4]), [0.0, 0.0])

    def test_inversa_z(self):
        orig = [2.0, 4.0, 9.0]
        m, dp = n.parametros_zscore(orig)
        for a, b in zip(orig, n.desfazer_z_score(n.z_score(orig), m, dp)):
            self.assertAlmostEqual(a, b)

    def test_robusta(self):
        # mediana 3, Q1 2, Q3 4, IQR 2
        self.assertEqual(n.escala_robusta([1, 2, 3, 4, 5]), [-1.0, -0.5, 0.0, 0.5, 1.0])

    def test_vazio(self):
        with self.assertRaises(ValueError):
            n.min_max([])
        with self.assertRaises(ValueError):
            n.z_score([])


if __name__ == "__main__":
    unittest.main()
