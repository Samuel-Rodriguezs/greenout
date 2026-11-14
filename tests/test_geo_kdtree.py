import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_kdtree import KDTree


class TestKDTree(unittest.TestCase):
    def test_vazia(self):
        t = KDTree([])
        self.assertEqual(len(t), 0)
        self.assertIsNone(t.mais_proximo((1, 1)))
        self.assertEqual(t.no_raio((0, 0), 5), [])

    def test_exemplo_2d(self):
        t = KDTree([(2, 3), (5, 4), (9, 6), (4, 7), (8, 1), (7, 2)])
        self.assertEqual(t.mais_proximo((9, 2)), (8, 1))
        self.assertEqual(t.mais_proximo((2, 3)), (2, 3))

    def test_k_vizinhos_ordenados(self):
        t = KDTree([(0, 0), (1, 0), (2, 0), (3, 0), (10, 0)])
        self.assertEqual(t.k_mais_proximos((0, 0), 3), [(0, 0), (1, 0), (2, 0)])
        self.assertEqual(len(t.k_mais_proximos((0, 0), 99)), 5)

    def test_raio(self):
        t = KDTree([(0, 0), (3, 4), (5, 0), (6, 6)])
        self.assertEqual(sorted(t.no_raio((0, 0), 5)), [(0, 0), (3, 4), (5, 0)])  # borda inclusa
        self.assertEqual(t.no_raio((100, 100), 1), [])

    def test_3d(self):
        t = KDTree([(0, 0, 0), (1, 1, 1), (5, 5, 5)])
        self.assertEqual(t.mais_proximo((4, 4, 4)), (5, 5, 5))

    def test_duplicatas(self):
        t = KDTree([(1, 1), (1, 1), (1, 1), (5, 5)])
        self.assertEqual(t.k_mais_proximos((1, 1), 3), [(1, 1)] * 3)

    def test_erros(self):
        with self.assertRaises(ValueError):
            KDTree([(1, 2), (1, 2, 3)])
        with self.assertRaises(ValueError):
            KDTree([(1, 2)]).k_mais_proximos((0, 0), 0)
        with self.assertRaises(ValueError):
            KDTree([(1, 2)]).mais_proximo((0, 0, 0))

    def test_aleatorio_contra_forca_bruta(self):
        rng = random.Random(8)
        for dim in (2, 3):
            pts = [tuple(rng.randint(0, 50) for _ in range(dim)) for _ in range(200)]
            t = KDTree(pts)
            for _ in range(25):
                alvo = tuple(rng.uniform(-5, 55) for _ in range(dim))
                esperado = sorted(math.dist(p, alvo) for p in pts)[:5]
                obtido = [math.dist(p, alvo) for p in t.k_mais_proximos(alvo, 5)]
                for a, b in zip(obtido, esperado):
                    self.assertAlmostEqual(a, b)
                r = rng.uniform(1, 15)
                self.assertEqual(
                    sorted(t.no_raio(alvo, r)), sorted(p for p in pts if math.dist(p, alvo) <= r)
                )


if __name__ == "__main__":
    unittest.main()
