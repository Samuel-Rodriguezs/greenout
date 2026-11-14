import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_regularizacao import lasso, penalidade_l1, penalidade_l2, ridge


def dados(n=60, seed=1):
    r = random.Random(seed)
    X = [[r.gauss(0, 1) for _ in range(4)] for _ in range(n)]
    y = [3 * x[0] - 2 * x[1] + 1.0 + r.gauss(0, 0.05) for x in X]
    return X, y


class TestRegularizacao(unittest.TestCase):
    def test_ridge_alfa_zero_recupera_coeficientes(self):
        X, y = dados()
        w, b = ridge(X, y, 0.0)
        self.assertAlmostEqual(w[0], 3, delta=0.05)
        self.assertAlmostEqual(w[1], -2, delta=0.05)
        self.assertAlmostEqual(w[2], 0, delta=0.05)
        self.assertAlmostEqual(b, 1.0, delta=0.05)

    def test_ridge_encolhe(self):
        X, y = dados()
        w0, _ = ridge(X, y, 0.0)
        w1, _ = ridge(X, y, 100.0)
        self.assertLess(sum(v * v for v in w1), sum(v * v for v in w0))
        self.assertNotEqual(w1[0], 0.0)

    def test_lasso_zera_irrelevantes(self):
        X, y = dados()
        w, b = lasso(X, y, 0.1)
        self.assertEqual(w[2], 0.0)
        self.assertEqual(w[3], 0.0)
        self.assertAlmostEqual(w[0], 3, delta=0.3)
        self.assertAlmostEqual(b, 1.0, delta=0.1)

    def test_lasso_alfa_grande_zera_tudo(self):
        X, y = dados()
        w, b = lasso(X, y, 100.0)
        self.assertEqual(w, [0.0] * 4)
        self.assertAlmostEqual(b, sum(y) / len(y))

    def test_penalidades(self):
        self.assertEqual(penalidade_l1([1, -2, 3], 0.5), 3.0)
        self.assertEqual(penalidade_l2([1, -2, 3], 0.5), 7.0)

    def test_ridge_resolve_colinearidade(self):
        X = [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0], [4.0, 8.0]]
        y = [1.0, 2.0, 3.0, 4.0]
        with self.assertRaises(ValueError):
            ridge(X, y, 0.0)
        w, _ = ridge(X, y, 0.1)
        self.assertAlmostEqual(w[0] + 2 * w[1], 1.0, delta=0.05)

    def test_alfa_negativo(self):
        with self.assertRaises(ValueError):
            ridge([[1.0], [2.0]], [1.0, 2.0], -1)
        with self.assertRaises(ValueError):
            lasso([[1.0], [2.0]], [1.0, 2.0], -1)


if __name__ == "__main__":
    unittest.main()
