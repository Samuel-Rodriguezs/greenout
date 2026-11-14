import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_mst import kruskal, prim

ARESTAS = [(0, 1, 4), (0, 2, 3), (1, 2, 1), (1, 3, 2), (2, 3, 4), (3, 4, 2)]


class TestMst(unittest.TestCase):
    def test_kruskal(self):
        total, esc = kruskal(5, ARESTAS)
        self.assertEqual(total, 8)
        self.assertEqual(len(esc), 4)

    def test_prim_igual_kruskal(self):
        self.assertEqual(prim(5, ARESTAS), kruskal(5, ARESTAS)[0])
        self.assertEqual(prim(5, ARESTAS, inicio=3), 8)

    def test_floresta(self):
        total, esc = kruskal(4, [(0, 1, 1), (2, 3, 5)])
        self.assertEqual((total, len(esc)), (6, 2))

    def test_prim_desconexo(self):
        with self.assertRaises(ValueError):
            prim(4, [(0, 1, 1), (2, 3, 5)])

    def test_vazio_e_unico(self):
        self.assertEqual(kruskal(0, []), (0.0, []))
        self.assertEqual(prim(0, []), 0.0)
        self.assertEqual(prim(1, []), 0.0)


if __name__ == "__main__":
    unittest.main()
