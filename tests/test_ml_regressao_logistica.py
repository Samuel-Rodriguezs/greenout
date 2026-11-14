import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_regressao_logistica import RegressaoLogistica, sigmoide


def dados(seed=3, n=40):
    r = random.Random(seed)
    X = [[r.gauss(2, 0.7), r.gauss(2, 0.7)] for _ in range(n)]
    X += [[r.gauss(-2, 0.7), r.gauss(-2, 0.7)] for _ in range(n)]
    return X, [1] * n + [0] * n


class TestRegressaoLogistica(unittest.TestCase):
    def test_sigmoide(self):
        self.assertAlmostEqual(sigmoide(0), 0.5)
        self.assertGreater(sigmoide(50), 0.999)
        self.assertLess(sigmoide(-50), 0.001)
        self.assertEqual(sigmoide(-1000), 0.0)

    def test_aprende(self):
        X, y = dados()
        m = RegressaoLogistica(iteracoes=300).treinar(X, y)
        acc = sum(a == b for a, b in zip(m.prever(X), y)) / len(y)
        self.assertGreaterEqual(acc, 0.97)

    def test_perda_decresce(self):
        X, y = dados()
        m = RegressaoLogistica(iteracoes=100, taxa=0.1).treinar(X, y)
        self.assertLess(m.historico_perda[-1], m.historico_perda[0])
        self.assertLess(m.historico_perda[-1], 0.2)

    def test_l2_encolhe_pesos(self):
        X, y = dados()
        a = RegressaoLogistica(iteracoes=200).treinar(X, y)
        b = RegressaoLogistica(iteracoes=200, l2=1.0).treinar(X, y)
        self.assertLess(abs(b.pesos[0]), abs(a.pesos[0]))

    def test_proba_em_01(self):
        X, y = dados()
        m = RegressaoLogistica(iteracoes=50).treinar(X, y)
        self.assertTrue(all(0 <= p <= 1 for p in m.proba(X)))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            RegressaoLogistica().treinar([], [])


if __name__ == "__main__":
    unittest.main()
