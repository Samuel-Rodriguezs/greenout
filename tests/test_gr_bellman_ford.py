import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_bellman_ford import INF, CicloNegativoError, bellman_ford, caminho


class TestBellmanFord(unittest.TestCase):
    def test_pesos_negativos(self):
        arestas = [("a", "b", 4), ("a", "c", 5), ("b", "c", -3), ("c", "d", 2)]
        dist, pred = bellman_ford(["a", "b", "c", "d"], arestas, "a")
        self.assertEqual(dist, {"a": 0, "b": 4, "c": 1, "d": 3})
        self.assertEqual(caminho(pred, "d"), ["a", "b", "c", "d"])

    def test_inalcancavel(self):
        dist, _ = bellman_ford(["a", "b"], [], "a")
        self.assertEqual(dist["b"], INF)

    def test_ciclo_negativo(self):
        arestas = [("a", "b", 1), ("b", "c", -2), ("c", "b", 1)]
        with self.assertRaises(CicloNegativoError):
            bellman_ford(["a", "b", "c"], arestas, "a")

    def test_ciclo_negativo_inalcancavel_ignorado(self):
        arestas = [("b", "c", -2), ("c", "b", 1)]
        dist, _ = bellman_ford(["a", "b", "c"], arestas, "a")
        self.assertEqual(dist["a"], 0)

    def test_origem_invalida(self):
        with self.assertRaises(ValueError):
            bellman_ford(["a"], [], "z")


if __name__ == "__main__":
    unittest.main()
