import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_svm_linear import SVMLinear


def dados(seed=1, n=40):
    r = random.Random(seed)
    X = [[r.gauss(2.5, 0.6), r.gauss(2.5, 0.6)] for _ in range(n)]
    X += [[r.gauss(-2.5, 0.6), r.gauss(-2.5, 0.6)] for _ in range(n)]
    return X, [1] * n + [-1] * n


class TestSVM(unittest.TestCase):
    def test_separa(self):
        X, y = dados()
        m = SVMLinear(epocas=20, seed=2).treinar(X, y)
        acc = sum(a == b for a, b in zip(m.prever(X), y)) / len(y)
        self.assertGreaterEqual(acc, 0.97)

    def test_generaliza(self):
        X, y = dados(1)
        Xv, yv = dados(99, 20)
        m = SVMLinear(epocas=20, seed=2).treinar(X, y)
        acc = sum(a == b for a, b in zip(m.prever(Xv), yv)) / len(yv)
        self.assertGreaterEqual(acc, 0.95)

    def test_peso_aponta_para_classe_positiva(self):
        X, y = dados()
        m = SVMLinear(seed=3, epocas=10).treinar(X, y)
        self.assertGreater(m.pesos[0], 0)
        self.assertGreater(m.pesos[1], 0)

    def test_deterministico(self):
        X, y = dados()
        self.assertEqual(SVMLinear(seed=4, epocas=5).treinar(X, y).pesos,
                         SVMLinear(seed=4, epocas=5).treinar(X, y).pesos)

    def test_margens_positivas_maioria(self):
        X, y = dados()
        m = SVMLinear(epocas=20, seed=2).treinar(X, y)
        self.assertGreater(sum(g > 0 for g in m.margens(X, y)), 75)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            SVMLinear().treinar([[1.0]], [0])
        with self.assertRaises(ValueError):
            SVMLinear().treinar([], [])


if __name__ == "__main__":
    unittest.main()
