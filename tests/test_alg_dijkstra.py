import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_dijkstra import dijkstra


class TesteDijkstra(unittest.TestCase):
    def test_grafo_simples(self):
        g = {"A": {"B": 1, "C": 4}, "B": {"C": 2, "D": 5}, "C": {"D": 1}, "D": {}}
        self.assertEqual(dijkstra(g, "A"), {"A": 0, "B": 1, "C": 3, "D": 4})

    def test_no_inalcancavel(self):
        g = {"A": {"B": 1}, "B": {}, "C": {}}
        self.assertEqual(dijkstra(g, "A"), {"A": 0, "B": 1})

    def test_no_unico(self):
        self.assertEqual(dijkstra({"A": {}}, "A"), {"A": 0})

    def test_ciclo(self):
        g = {"A": {"B": 1}, "B": {"A": 1, "C": 2}, "C": {"A": 1}}
        self.assertEqual(dijkstra(g, "A"), {"A": 0, "B": 1, "C": 3})

    def test_peso_zero(self):
        g = {"A": {"B": 0}, "B": {"C": 0}, "C": {}}
        self.assertEqual(dijkstra(g, "A"), {"A": 0, "B": 0, "C": 0})

    def test_origem_inexistente(self):
        with self.assertRaises(KeyError):
            dijkstra({"A": {}}, "Z")

    def test_peso_negativo(self):
        with self.assertRaises(ValueError):
            dijkstra({"A": {"B": -1}, "B": {}}, "A")


if __name__ == "__main__":
    unittest.main()
