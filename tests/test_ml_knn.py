import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_knn import KNN, distancia_euclidiana, distancia_manhattan


class TestKNN(unittest.TestCase):
    def setUp(self):
        r = random.Random(11)
        self.X = [[r.gauss(0, 0.5), r.gauss(0, 0.5)] for _ in range(30)]
        self.X += [[r.gauss(5, 0.5), r.gauss(5, 0.5)] for _ in range(30)]
        self.y = ["a"] * 30 + ["b"] * 30

    def test_classifica(self):
        m = KNN(k=5).treinar(self.X, self.y)
        self.assertEqual(m.classificar([0.1, -0.2]), "a")
        self.assertEqual(m.classificar([4.8, 5.3]), "b")

    def test_acuracia_treino_k1(self):
        m = KNN(k=1).treinar(self.X, self.y)
        self.assertEqual(m.prever(self.X), self.y)

    def test_regressao(self):
        m = KNN(k=2).treinar([[0], [1], [10]], [0.0, 2.0, 100.0])
        self.assertAlmostEqual(m.regredir([0.4]), 1.0)

    def test_distancias(self):
        self.assertEqual(distancia_euclidiana([0, 0], [3, 4]), 5.0)
        self.assertEqual(distancia_manhattan([0, 0], [3, 4]), 7)

    def test_desempate_pelo_mais_proximo(self):
        m = KNN(k=2).treinar([[0], [3]], ["x", "y"])
        self.assertEqual(m.classificar([1]), "x")

    def test_k_maior_que_dados(self):
        m = KNN(k=10).treinar([[0], [1]], [1.0, 3.0])
        self.assertEqual(m.regredir([0]), 2.0)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            KNN(k=0)
        with self.assertRaises(ValueError):
            KNN().treinar([], [])


if __name__ == "__main__":
    unittest.main()
