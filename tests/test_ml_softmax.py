import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_softmax import (RegressaoSoftmax, entropia_cruzada,
                        entropia_cruzada_distribuicao, log_softmax, softmax)


class TestSoftmax(unittest.TestCase):
    def test_soma_um_e_ordem(self):
        p = softmax([1.0, 2.0, 3.0])
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertTrue(p[0] < p[1] < p[2])

    def test_estavel_numericamente(self):
        self.assertEqual(softmax([1000.0, 1000.0]), [0.5, 0.5])
        self.assertAlmostEqual(softmax([-1000.0, 0.0])[1], 1.0)

    def test_invariante_a_translacao(self):
        a, b = softmax([1.0, 2.0]), softmax([11.0, 12.0])
        self.assertAlmostEqual(a[0], b[0])

    def test_log_softmax(self):
        z = [0.5, 1.5, -1.0]
        for l, p in zip(log_softmax(z), softmax(z)):
            self.assertAlmostEqual(l, math.log(p))

    def test_entropia_cruzada(self):
        self.assertAlmostEqual(entropia_cruzada(0, [0.5, 0.5]), math.log(2))
        self.assertAlmostEqual(entropia_cruzada(1, [0.0, 1.0]), 0.0)
        self.assertGreater(entropia_cruzada(0, [0.0, 1.0]), 30)
        with self.assertRaises(ValueError):
            entropia_cruzada(2, [0.5, 0.5])

    def test_distribuicao(self):
        self.assertAlmostEqual(entropia_cruzada_distribuicao([1, 0], [0.25, 0.75]), math.log(4))
        with self.assertRaises(ValueError):
            entropia_cruzada_distribuicao([1], [0.5, 0.5])

    def test_classificador_tres_classes(self):
        r = random.Random(4)
        X, y = [], []
        for k, (cx, cy) in enumerate([(0, 0), (4, 0), (0, 4)]):
            for _ in range(20):
                X.append([r.gauss(cx, 0.5), r.gauss(cy, 0.5)])
                y.append(k)
        m = RegressaoSoftmax(3, taxa=0.5, iteracoes=150).treinar(X, y)
        self.assertLess(m.perdas[-1], m.perdas[0])
        acc = sum(a == b for a, b in zip(m.prever(X), y)) / len(y)
        self.assertGreaterEqual(acc, 0.95)

    def test_vazio(self):
        with self.assertRaises(ValueError):
            softmax([])


if __name__ == "__main__":
    unittest.main()
