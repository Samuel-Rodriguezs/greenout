import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_pca import PCA, potencia


class TestPCA(unittest.TestCase):
    def test_potencia_matriz_diagonal(self):
        lam, v = potencia([[3.0, 0.0], [0.0, 1.0]])
        self.assertAlmostEqual(lam, 3.0, places=6)
        self.assertAlmostEqual(abs(v[0]), 1.0, places=6)

    def test_potencia_simetrica(self):
        lam, v = potencia([[2.0, 1.0], [1.0, 2.0]])
        self.assertAlmostEqual(lam, 3.0, places=6)
        self.assertAlmostEqual(v[0], math.sqrt(0.5), places=5)

    def test_reta_diagonal(self):
        r = random.Random(1)
        X = []
        for _ in range(100):
            t = r.uniform(-5, 5)
            X.append([t + r.gauss(0, 0.05), t + r.gauss(0, 0.05)])
        p = PCA(1).ajustar(X)
        c = p.componentes[0]
        self.assertAlmostEqual(abs(c[0]), math.sqrt(0.5), places=2)
        self.assertGreater(p.razao_variancia()[0], 0.99)

    def test_componentes_ortogonais_e_unitarios(self):
        r = random.Random(2)
        X = [[r.gauss(0, 3), r.gauss(0, 1), r.gauss(0, 0.2)] for _ in range(200)]
        p = PCA(3).ajustar(X)
        a, b = p.componentes[0], p.componentes[1]
        self.assertAlmostEqual(sum(x * y for x, y in zip(a, b)), 0.0, places=4)
        self.assertAlmostEqual(sum(x * x for x in a), 1.0, places=6)
        self.assertGreater(p.variancias[0], p.variancias[1])
        self.assertAlmostEqual(sum(p.razao_variancia()), 1.0, places=3)

    def test_transformacao_centrada(self):
        X = [[1.0, 2.0], [3.0, 4.0], [5.0, 7.0], [7.0, 8.0]]
        Z = PCA(2).ajustar(X).transformar(X)
        for col in zip(*Z):
            self.assertAlmostEqual(sum(col), 0.0, places=8)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            PCA(1).ajustar([[1.0, 2.0]])
        with self.assertRaises(ValueError):
            PCA(3).ajustar([[1.0, 2.0], [2.0, 3.0]])


if __name__ == "__main__":
    unittest.main()
