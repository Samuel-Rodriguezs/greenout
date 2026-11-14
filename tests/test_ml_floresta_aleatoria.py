import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_floresta_aleatoria import FlorestaAleatoria


def dados(seed, n=40):
    r = random.Random(seed)
    X = [[r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1)] for _ in range(n)]
    y = [1 if x[0] + x[1] > 0 else 0 for x in X]
    return X, y


class TestFloresta(unittest.TestCase):
    def test_generaliza(self):
        Xt, yt = dados(1, 120)
        Xv, yv = dados(2, 60)
        f = FlorestaAleatoria(n_arvores=15, n_atributos=2, seed=4).treinar(Xt, yt)
        acc = sum(p == r for p, r in zip(f.prever(Xv), yv)) / len(yv)
        self.assertGreaterEqual(acc, 0.8)

    def test_deterministico_por_seed(self):
        X, y = dados(3)
        a = FlorestaAleatoria(seed=9).treinar(X, y).prever(X)
        b = FlorestaAleatoria(seed=9).treinar(X, y).prever(X)
        self.assertEqual(a, b)

    def test_numero_de_arvores(self):
        X, y = dados(3)
        self.assertEqual(len(FlorestaAleatoria(n_arvores=7).treinar(X, y).arvores), 7)

    def test_uma_classe(self):
        f = FlorestaAleatoria(n_arvores=3).treinar([[1, 2], [3, 4]], ["z", "z"])
        self.assertEqual(f.prever([[0, 0]]), ["z"])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            FlorestaAleatoria(n_arvores=0)
        with self.assertRaises(ValueError):
            FlorestaAleatoria().treinar([], [])


if __name__ == "__main__":
    unittest.main()
