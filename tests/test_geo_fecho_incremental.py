import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_convex_hull import andrew
from geo_fecho_incremental import FechoIncremental


def norm(h):
    i = h.index(min(h))
    return h[i:] + h[:i]


class TestFechoIncremental(unittest.TestCase):
    def test_crescimento_basico(self):
        f = FechoIncremental()
        self.assertTrue(f.adicionar((0, 0)))
        self.assertTrue(f.adicionar((4, 0)))
        self.assertTrue(f.adicionar((0, 4)))
        self.assertEqual(norm(f.vertices), [(0, 0), (4, 0), (0, 4)])
        self.assertTrue(f.adicionar((4, 4)))
        self.assertEqual(len(f), 4)

    def test_ponto_interno_e_na_borda_nao_muda(self):
        f = FechoIncremental([(0, 0), (4, 0), (4, 4), (0, 4)])
        self.assertFalse(f.adicionar((2, 2)))
        self.assertFalse(f.adicionar((2, 0)))
        self.assertFalse(f.adicionar((4, 4)))
        self.assertEqual(len(f), 4)

    def test_ponto_colinear_estende_aresta(self):
        f = FechoIncremental([(0, 0), (4, 0), (4, 4), (0, 4)])
        self.assertTrue(f.adicionar((6, 0)))
        self.assertEqual(norm(f.vertices), [(0, 0), (6, 0), (4, 4), (0, 4)])

    def test_ponto_remove_varios_vertices(self):
        f = FechoIncremental([(0, 0), (4, 0), (5, 2), (4, 4), (0, 4)])
        self.assertTrue(f.adicionar((20, 2)))
        self.assertEqual(norm(f.vertices), [(0, 0), (4, 0), (20, 2), (4, 4), (0, 4)])

    def test_estado_colinear_inicial(self):
        f = FechoIncremental([(0, 0), (1, 1), (2, 2)])
        self.assertEqual(f.vertices, [(0, 0), (2, 2)])
        self.assertTrue(f.contem((1, 1)))
        self.assertFalse(f.contem((3, 3)))
        self.assertFalse(FechoIncremental().contem((0, 0)))

    def test_igual_ao_andrew_em_aleatorios(self):
        rng = random.Random(3)
        for _ in range(80):
            pts = [(rng.randint(-6, 6), rng.randint(-6, 6)) for _ in range(rng.randint(1, 30))]
            f = FechoIncremental()
            for p in pts:
                f.adicionar(p)
            esperado = andrew(pts)
            self.assertEqual(norm(f.vertices), norm(esperado), pts)


if __name__ == "__main__":
    unittest.main()
