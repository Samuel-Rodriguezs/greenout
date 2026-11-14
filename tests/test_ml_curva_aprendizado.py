import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_curva_aprendizado import curva_aprendizado, diagnostico
from ml_knn import KNN


def dados(seed, n):
    r = random.Random(seed)
    X = [[r.uniform(0, 10)] for _ in range(n)]
    y = [1 if x[0] > 5 else 0 for x in X]
    return X, y


def ajustar(X, y):
    return KNN(k=1).treinar(X, y)


def prever(m, X):
    return m.prever(X)


def erro(y, p):
    return sum(a != b for a, b in zip(y, p)) / len(y)


class TestCurva(unittest.TestCase):
    def setUp(self):
        self.Xt, self.yt = dados(1, 150)
        self.Xv, self.yv = dados(2, 100)

    def test_erro_validacao_cai_com_mais_dados(self):
        c = curva_aprendizado(ajustar, prever, erro, self.Xt, self.yt, self.Xv, self.yv, [3, 150], seed=1)
        self.assertLess(c[-1][2], c[0][2])
        self.assertLess(c[-1][2], 0.1)

    def test_erro_treino_k1_zero(self):
        c = curva_aprendizado(ajustar, prever, erro, self.Xt, self.yt, self.Xv, self.yv, [10, 50], seed=1)
        self.assertTrue(all(t == 0.0 for _, t, _ in c))

    def test_formato_e_determinismo(self):
        a = curva_aprendizado(ajustar, prever, erro, self.Xt, self.yt, self.Xv, self.yv, [5, 20, 80], seed=3)
        b = curva_aprendizado(ajustar, prever, erro, self.Xt, self.yt, self.Xv, self.yv, [5, 20, 80], seed=3)
        self.assertEqual(a, b)
        self.assertEqual([n for n, _, _ in a], [5, 20, 80])

    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            curva_aprendizado(ajustar, prever, erro, self.Xt, self.yt, self.Xv, self.yv, [0])
        with self.assertRaises(ValueError):
            curva_aprendizado(ajustar, prever, erro, self.Xt, self.yt, self.Xv, self.yv, [999])

    def test_diagnostico(self):
        self.assertEqual(diagnostico([(10, 0.4, 0.45)]), "subajuste")
        self.assertEqual(diagnostico([(10, 0.0, 0.2)], limiar_erro=0.5), "sobreajuste")
        self.assertEqual(diagnostico([(10, 0.02, 0.05)]), "bom")


if __name__ == "__main__":
    unittest.main()
