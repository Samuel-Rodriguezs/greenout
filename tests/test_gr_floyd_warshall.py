import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_floyd_warshall import INF, floyd_warshall, reconstruir, tem_ciclo_negativo


class TestFloydWarshall(unittest.TestCase):
    def test_distancias(self):
        d, _ = floyd_warshall(4, [(0, 1, 3), (1, 2, 1), (0, 2, 7), (2, 3, 2)])
        self.assertEqual(d[0][2], 4)
        self.assertEqual(d[0][3], 6)
        self.assertEqual(d[3][0], INF)

    def test_caminho(self):
        _, p = floyd_warshall(4, [(0, 1, 3), (1, 2, 1), (0, 2, 7), (2, 3, 2)])
        self.assertEqual(reconstruir(p, 0, 3), [0, 1, 2, 3])
        self.assertEqual(reconstruir(p, 3, 0), [])
        self.assertEqual(reconstruir(p, 1, 1), [1])

    def test_ciclo_negativo(self):
        d, _ = floyd_warshall(2, [(0, 1, 1), (1, 0, -3)])
        self.assertTrue(tem_ciclo_negativo(d))

    def test_vazio(self):
        d, _ = floyd_warshall(0, [])
        self.assertEqual(d, [])

    def test_aresta_paralela_menor(self):
        d, _ = floyd_warshall(2, [(0, 1, 5), (0, 1, 2)])
        self.assertEqual(d[0][1], 2)


if __name__ == "__main__":
    unittest.main()
