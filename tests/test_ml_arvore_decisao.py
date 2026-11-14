import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_arvore_decisao import ArvoreDecisao, entropia, gini


class TestArvore(unittest.TestCase):
    def test_impurezas(self):
        self.assertEqual(gini(["a", "a"]), 0.0)
        self.assertAlmostEqual(gini(["a", "b"]), 0.5)
        self.assertAlmostEqual(entropia(["a", "b"]), 1.0)
        self.assertEqual(entropia([]), 0.0)

    def test_degrau_simples(self):
        X = [[1], [2], [3], [10], [11], [12]]
        y = [0, 0, 0, 1, 1, 1]
        a = ArvoreDecisao().treinar(X, y)
        self.assertEqual(a.prever(X), y)
        self.assertEqual(a.profundidade(), 1)
        self.assertEqual(a.raiz.limiar, 6.5)

    def test_faixa_central_precisa_profundidade_2(self):
        X = [[v] for v in range(9)]
        y = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        a = ArvoreDecisao(criterio="entropia").treinar(X, y)
        self.assertEqual(a.prever(X), y)
        self.assertEqual(a.profundidade(), 2)

    def test_poda_por_profundidade(self):
        X = [[v] for v in range(9)]
        y = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        a = ArvoreDecisao(profundidade_max=1).treinar(X, y)
        self.assertLessEqual(a.profundidade(), 1)
        self.assertLess(sum(p == r for p, r in zip(a.prever(X), y)), 9)

    def test_profundidade_zero_e_maioria(self):
        a = ArvoreDecisao(profundidade_max=0).treinar([[1], [2], [3]], ["x", "x", "y"])
        self.assertEqual(a.prever([[0], [9]]), ["x", "x"])

    def test_rotulo_unico(self):
        a = ArvoreDecisao().treinar([[1], [2]], ["k", "k"])
        self.assertTrue(a.raiz.folha)

    def test_sem_treino_e_invalido(self):
        with self.assertRaises(RuntimeError):
            ArvoreDecisao().prever_um([1])
        with self.assertRaises(ValueError):
            ArvoreDecisao(criterio="x")
        with self.assertRaises(ValueError):
            ArvoreDecisao().treinar([], [])


if __name__ == "__main__":
    unittest.main()
