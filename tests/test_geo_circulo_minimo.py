import itertools
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_circulo_minimo import circulo_minimo


def forca_bruta(pts):
    """Menor raio entre os círculos de 2 e 3 pontos que contêm todos."""
    melhor = None
    cands = []
    for a, b in itertools.combinations(pts, 2):
        cands.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, math.dist(a, b) / 2))
    for a, b, c in itertools.combinations(pts, 3):
        d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
        if d == 0:
            continue
        ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
        uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
        cands.append((ux, uy, math.hypot(ux - a[0], uy - a[1])))
    for cx, cy, r in cands:
        if all(math.hypot(p[0] - cx, p[1] - cy) <= r + 1e-9 for p in pts):
            if melhor is None or r < melhor:
                melhor = r
    return melhor


class TestCirculoMinimo(unittest.TestCase):
    def test_um_ponto(self):
        self.assertEqual(circulo_minimo([(3, 4)]), (3, 4, 0))

    def test_dois_pontos(self):
        cx, cy, r = circulo_minimo([(0, 0), (6, 8)])
        self.assertAlmostEqual(cx, 3)
        self.assertAlmostEqual(cy, 4)
        self.assertAlmostEqual(r, 5)

    def test_triangulo_retangulo_usa_hipotenusa(self):
        cx, cy, r = circulo_minimo([(0, 0), (4, 0), (0, 3)])
        self.assertAlmostEqual(r, 2.5)
        self.assertAlmostEqual(cx, 2)
        self.assertAlmostEqual(cy, 1.5)

    def test_equilatero(self):
        h = math.sqrt(3)
        cx, cy, r = circulo_minimo([(0, 0), (2, 0), (1, h)])
        self.assertAlmostEqual(r, 2 / h)
        self.assertAlmostEqual(cx, 1)

    def test_colineares_e_duplicatas(self):
        cx, cy, r = circulo_minimo([(0, 0), (1, 1), (2, 2), (4, 4), (4, 4)])
        self.assertAlmostEqual(r, math.sqrt(8))
        self.assertAlmostEqual(cx, 2)

    def test_pontos_internos_ignorados(self):
        pts = [(-5, 0), (5, 0), (0, 5), (0, -5), (1, 1), (-2, 3)]
        self.assertAlmostEqual(circulo_minimo(pts)[2], 5)

    def test_vazio(self):
        with self.assertRaises(ValueError):
            circulo_minimo([])

    def test_aleatorio_contra_forca_bruta(self):
        rng = random.Random(21)
        for _ in range(60):
            pts = [(rng.randint(-10, 10), rng.randint(-10, 10)) for _ in range(rng.randint(2, 9))]
            if len(set(pts)) < 2:
                continue
            cx, cy, r = circulo_minimo(pts, semente=rng.randint(0, 99))
            self.assertAlmostEqual(r, forca_bruta(pts), places=6, msg=str(pts))
            self.assertTrue(all(math.hypot(p[0] - cx, p[1] - cy) <= r + 1e-7 for p in pts))


if __name__ == "__main__":
    unittest.main()
