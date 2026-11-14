import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_convex_hull import andrew, graham


def normalizar(h):
    """Rotaciona o fecho para começar no menor ponto (comparação independente do início)."""
    if not h:
        return h
    i = h.index(min(h))
    return h[i:] + h[:i]


class TestConvexHull(unittest.TestCase):
    def ambos(self, pontos, esperado):
        self.assertEqual(normalizar(andrew(pontos)), esperado)
        self.assertEqual(normalizar(graham(pontos)), esperado)

    def test_quadrado_com_interior(self):
        pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (1, 3), (3, 1)]
        self.ambos(pts, [(0, 0), (4, 0), (4, 4), (0, 4)])

    def test_colineares_na_aresta_removidos(self):
        pts = [(0, 0), (2, 0), (4, 0), (4, 4), (0, 4), (0, 2)]
        self.ambos(pts, [(0, 0), (4, 0), (4, 4), (0, 4)])

    def test_duplicatas(self):
        pts = [(0, 0), (0, 0), (3, 0), (3, 0), (0, 3)]
        self.ambos(pts, [(0, 0), (3, 0), (0, 3)])

    def test_todos_colineares(self):
        pts = [(0, 0), (1, 1), (2, 2), (3, 3)]
        self.assertEqual(andrew(pts), [(0, 0), (3, 3)])
        self.assertEqual(graham(pts), [(0, 0), (3, 3)])

    def test_pequenos(self):
        for f in (andrew, graham):
            self.assertEqual(f([]), [])
            self.assertEqual(f([(1, 1)]), [(1, 1)])
            self.assertEqual(f([(2, 2), (1, 1)]), [(1, 1), (2, 2)])
            self.assertEqual(f([(1, 1), (1, 1)]), [(1, 1)])

    def test_triangulo_anti_horario(self):
        h = andrew([(0, 0), (0, 5), (5, 0)])
        self.assertEqual(normalizar(h), [(0, 0), (5, 0), (0, 5)])

    def test_aleatorio_concorda(self):
        rng = random.Random(7)
        for _ in range(60):
            pts = [(rng.randint(0, 8), rng.randint(0, 8)) for _ in range(rng.randint(1, 25))]
            self.assertEqual(normalizar(andrew(pts)), normalizar(graham(pts)), pts)


if __name__ == "__main__":
    unittest.main()
