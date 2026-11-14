import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_naive_bayes_gaussiano import NaiveBayesGaussiano


def dados(seed, n=50):
    r = random.Random(seed)
    X = [[r.gauss(0, 1), r.gauss(0, 1)] for _ in range(n)]
    X += [[r.gauss(4, 1), r.gauss(4, 1)] for _ in range(n)]
    return X, ["a"] * n + ["b"] * n


class TestNBG(unittest.TestCase):
    def test_acuracia(self):
        X, y = dados(1)
        Xv, yv = dados(2, 30)
        m = NaiveBayesGaussiano().treinar(X, y)
        acc = sum(p == r for p, r in zip(m.prever(Xv), yv)) / len(yv)
        self.assertGreaterEqual(acc, 0.95)

    def test_parametros_estimados(self):
        X, y = dados(3, 200)
        m = NaiveBayesGaussiano().treinar(X, y)
        self.assertAlmostEqual(m.medias["b"][0], 4, delta=0.3)
        self.assertAlmostEqual(m.variancias["a"][1], 1, delta=0.3)
        self.assertEqual(m.priori["a"], 0.5)

    def test_proba_soma_um(self):
        X, y = dados(1)
        m = NaiveBayesGaussiano().treinar(X, y)
        p = m.proba([2.0, 2.0])
        self.assertAlmostEqual(sum(p.values()), 1.0)
        self.assertAlmostEqual(p["a"], 0.5, delta=0.1)
        self.assertGreater(m.proba([4.0, 4.0])["b"], 0.99)

    def test_priori_desbalanceada(self):
        m = NaiveBayesGaussiano().treinar([[0.0], [0.1], [-0.1], [0.05], [0.0], [10.0]],
                                          ["x", "x", "x", "x", "x", "y"])
        self.assertAlmostEqual(m.priori["x"], 5 / 6)

    def test_variancia_zero_suavizada(self):
        m = NaiveBayesGaussiano().treinar([[1.0], [1.0], [5.0], [5.0]], [0, 0, 1, 1])
        self.assertEqual(m.prever([[1.0], [5.0]]), [0, 1])

    def test_invalido(self):
        with self.assertRaises(ValueError):
            NaiveBayesGaussiano().treinar([], [])


if __name__ == "__main__":
    unittest.main()
