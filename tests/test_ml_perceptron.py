import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_perceptron import Perceptron, acuracia


class TestPerceptron(unittest.TestCase):
    def test_and(self):
        X = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y = [0, 0, 0, 1]
        p = Perceptron(seed=1).treinar(X, y)
        self.assertEqual(p.prever(X), y)
        self.assertLess(p.epocas_usadas, 100)

    def test_or(self):
        X = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y = [0, 1, 1, 1]
        self.assertEqual(Perceptron(seed=2).treinar(X, y).prever(X), y)

    def test_xor_nao_converge(self):
        X = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y = [0, 1, 1, 0]
        p = Perceptron(epocas=50).treinar(X, y)
        self.assertEqual(p.epocas_usadas, 50)
        self.assertLess(acuracia(y, p.prever(X)), 1.0)

    def test_separavel_sintetico(self):
        import random
        r = random.Random(7)
        X = [[r.uniform(1, 3), r.uniform(1, 3)] for _ in range(30)]
        X += [[r.uniform(-3, -1), r.uniform(-3, -1)] for _ in range(30)]
        y = [1] * 30 + [0] * 30
        p = Perceptron(seed=3).treinar(X, y)
        self.assertEqual(acuracia(y, p.prever(X)), 1.0)

    def test_deterministico(self):
        X = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y = [0, 0, 0, 1]
        a = Perceptron(seed=5).treinar(X, y)
        b = Perceptron(seed=5).treinar(X, y)
        self.assertEqual((a.pesos, a.vies), (b.pesos, b.vies))

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            Perceptron().treinar([], [])
        with self.assertRaises(ValueError):
            Perceptron().treinar([[1]], [1, 0])


if __name__ == "__main__":
    unittest.main()
