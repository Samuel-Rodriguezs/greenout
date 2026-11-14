import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_kmeans_pp import inicializar_pp, kmeans


def blobs():
    r = random.Random(5)
    X = []
    for cx, cy in [(0, 0), (10, 10), (0, 10)]:
        X += [[r.gauss(cx, 0.5), r.gauss(cy, 0.5)] for _ in range(20)]
    return X


class TestKMeansPP(unittest.TestCase):
    def test_tres_grupos(self):
        centros, rot, inercia = kmeans(blobs(), 3, seed=1)
        for i in range(3):
            self.assertEqual(len(set(rot[i * 20:(i + 1) * 20])), 1)
        self.assertEqual(len(set(rot)), 3)
        self.assertLess(inercia, 60)

    def test_deterministico(self):
        self.assertEqual(kmeans(blobs(), 3, seed=2), kmeans(blobs(), 3, seed=2))

    def test_k1_centro_e_media(self):
        centros, rot, _ = kmeans([[0.0], [2.0], [4.0]], 1)
        self.assertEqual(centros, [[2.0]])
        self.assertEqual(rot, [0, 0, 0])

    def test_k_igual_n_inercia_zero(self):
        _, _, inercia = kmeans([[0.0], [5.0], [9.0]], 3, seed=3)
        self.assertAlmostEqual(inercia, 0.0)

    def test_pp_escolhe_centros_distantes(self):
        X = [[0.0], [0.1], [100.0], [100.1]]
        for s in range(10):
            c = inicializar_pp(X, 2, random.Random(s))
            self.assertGreater(abs(c[0][0] - c[1][0]), 50)

    def test_pontos_identicos(self):
        centros, _, inercia = kmeans([[1.0, 1.0]] * 4, 2, seed=0)
        self.assertEqual(inercia, 0.0)

    def test_k_invalido(self):
        with self.assertRaises(ValueError):
            kmeans([[1.0]], 2)
        with self.assertRaises(ValueError):
            kmeans([[1.0]], 0)


if __name__ == "__main__":
    unittest.main()
