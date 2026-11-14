import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_dijkstra_caminho import dijkstra, menor_caminho

G = {
    "A": [("B", 7), ("C", 9), ("F", 14)],
    "B": [("C", 10), ("D", 15)],
    "C": [("D", 11), ("F", 2)],
    "D": [("E", 6)],
    "F": [("E", 9)],
    "E": [],
}


class TestDijkstra(unittest.TestCase):
    def test_caminho(self):
        self.assertEqual(menor_caminho(G, "A", "E"), (20, ["A", "C", "F", "E"]))

    def test_distancias(self):
        dist, _ = dijkstra(G, "A")
        self.assertEqual(dist["D"], 20)
        self.assertEqual(dist["F"], 11)

    def test_origem_igual_destino(self):
        self.assertEqual(menor_caminho(G, "A", "A"), (0, ["A"]))

    def test_inalcancavel(self):
        self.assertIsNone(menor_caminho(G, "E", "A"))
        self.assertIsNone(menor_caminho({}, "x", "y"))

    def test_peso_negativo(self):
        with self.assertRaises(ValueError):
            dijkstra({"a": [("b", -1)]}, "a")

    def test_pesos_zero_e_ciclo(self):
        g = {1: [(2, 0)], 2: [(1, 0), (3, 5)], 3: []}
        self.assertEqual(menor_caminho(g, 1, 3), (5, [1, 2, 3]))

    def test_nos_nao_comparaveis(self):
        g = {1: [("a", 1)], "a": [(2, 1)], 2: []}
        self.assertEqual(menor_caminho(g, 1, 2), (2, [1, "a", 2]))


if __name__ == "__main__":
    unittest.main()
