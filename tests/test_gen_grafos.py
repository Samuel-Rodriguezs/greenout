import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_grafos as g


class TestGenGrafos(unittest.TestCase):
    def test_er_extremos(self):
        rng = random.Random(1)
        self.assertEqual(g.erdos_renyi(rng, 10, 0.0), [])
        self.assertEqual(len(g.erdos_renyi(rng, 10, 1.0)), 45)
        self.assertEqual(g.erdos_renyi(rng, 0, 0.5), [])

    def test_er_densidade_e_simplicidade(self):
        n, p = 200, 0.1
        e = g.erdos_renyi(random.Random(2), n, p)
        esperado = p * n * (n - 1) / 2
        self.assertAlmostEqual(len(e), esperado, delta=0.1 * esperado)
        self.assertEqual(len(set(e)), len(e))
        self.assertTrue(all(0 <= u < v < n for u, v in e))

    def test_er_determinismo(self):
        self.assertEqual(g.erdos_renyi(random.Random(3), 50, 0.2), g.erdos_renyi(random.Random(3), 50, 0.2))

    def test_er_invalido(self):
        with self.assertRaises(ValueError):
            g.erdos_renyi(random.Random(0), 5, 1.5)
        with self.assertRaises(ValueError):
            g.erdos_renyi(random.Random(0), -1, 0.5)

    def test_ba_contagem_e_conexo(self):
        n, m = 300, 3
        e = g.barabasi_albert(random.Random(4), n, m)
        self.assertEqual(len(e), m * (m + 1) // 2 + (n - m - 1) * m)
        self.assertEqual(len(set(e)), len(e))  # sem arestas repetidas
        self.assertTrue(all(u != v for u, v in e))
        self.assertEqual(g.componentes_conexas(n, e), 1)
        self.assertTrue(min(g.graus(n, e)) >= m)

    def test_ba_cauda_pesada(self):
        n, m = 2000, 2
        gr = g.graus(n, g.barabasi_albert(random.Random(5), n, m))
        media = sum(gr) / n
        self.assertGreater(max(gr), 8 * media)  # hubs, ao contrário de um ER de mesma média

    def test_ba_determinismo_e_invalido(self):
        self.assertEqual(g.barabasi_albert(random.Random(6), 40, 2), g.barabasi_albert(random.Random(6), 40, 2))
        with self.assertRaises(ValueError):
            g.barabasi_albert(random.Random(0), 3, 3)
        with self.assertRaises(ValueError):
            g.barabasi_albert(random.Random(0), 5, 0)

    def test_componentes(self):
        self.assertEqual(g.componentes_conexas(5, [(0, 1), (2, 3)]), 3)
        self.assertEqual(g.componentes_conexas(0, []), 0)


if __name__ == "__main__":
    unittest.main()
