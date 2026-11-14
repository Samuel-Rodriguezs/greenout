import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_outliers as o

DADOS = [1, 2, 3, 4, 5, 100]


class TestOutliers(unittest.TestCase):
    def test_limites_iqr(self):
        # Q1=2.25, Q3=4.75, IQR=2.5 -> [-1.5, 8.5]
        inf, sup = o.limites_iqr(DADOS)
        self.assertAlmostEqual(inf, -1.5)
        self.assertAlmostEqual(sup, 8.5)

    def test_outliers_iqr(self):
        self.assertEqual(o.outliers_iqr(DADOS), [5])
        self.assertEqual(o.outliers_iqr([1, 2, 3, 4, 5]), [])

    def test_zscore(self):
        z = o.zscores(DADOS)
        self.assertAlmostEqual(z[5], 80.8333333 / 36.1733, places=3)
        self.assertAlmostEqual(sum(z), 0.0)
        self.assertEqual(o.outliers_zscore(DADOS, limite=2), [5])
        self.assertEqual(o.outliers_zscore(DADOS), [])

    def test_constante(self):
        self.assertEqual(o.zscores([3, 3, 3]), [0.0, 0.0, 0.0])

    def test_remover(self):
        self.assertEqual(o.remover_outliers(DADOS), [1, 2, 3, 4, 5])
        self.assertEqual(o.remover_outliers(DADOS, "zscore", limite=2), [1, 2, 3, 4, 5])
        with self.assertRaises(ValueError):
            o.remover_outliers(DADOS, "x")

    def test_vazio(self):
        with self.assertRaises(ValueError):
            o.outliers_iqr([])


if __name__ == "__main__":
    unittest.main()
