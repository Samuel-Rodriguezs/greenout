import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_dbscan import RUIDO, dbscan


def anel(raio, n, cx=0.0, cy=0.0):
    return [[cx + raio * math.cos(2 * math.pi * i / n), cy + raio * math.sin(2 * math.pi * i / n)]
            for i in range(n)]


class TestDBSCAN(unittest.TestCase):
    def test_dois_grupos_e_ruido(self):
        X = [[0, 0], [0.2, 0], [0, 0.2], [0.2, 0.2], [10, 10], [10.2, 10], [10, 10.2], [10.2, 10.2], [5, 5]]
        r = dbscan(X, eps=0.5, min_pts=3)
        self.assertEqual(r[:4], [0] * 4)
        self.assertEqual(r[4:8], [1] * 4)
        self.assertEqual(r[8], RUIDO)

    def test_aneis_concentricos(self):
        X = anel(1, 40) + anel(5, 100)
        r = dbscan(X, eps=0.8, min_pts=3)
        self.assertEqual(len(set(r[:40])), 1)
        self.assertEqual(len(set(r[40:])), 1)
        self.assertNotEqual(r[0], r[40])
        self.assertNotIn(RUIDO, r)

    def test_tudo_ruido(self):
        self.assertEqual(dbscan([[0], [10], [20]], eps=1, min_pts=2), [RUIDO] * 3)

    def test_borda_incluida(self):
        # ponto de borda alcançável vira parte do cluster
        r = dbscan([[0], [0.5], [1.0], [1.9]], eps=1.0, min_pts=3)
        self.assertEqual(r, [0, 0, 0, 0])

    def test_vazio(self):
        self.assertEqual(dbscan([], 1.0, 2), [])

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            dbscan([[0]], 0, 1)
        with self.assertRaises(ValueError):
            dbscan([[0]], 1, 0)


if __name__ == "__main__":
    unittest.main()
