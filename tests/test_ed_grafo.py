import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_grafo import Grafo


def montar() -> Grafo:
    g = Grafo()
    for a, b in [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]:
        g.adicionar_aresta(a, b)
    g.adicionar_vertice(9)  # isolado
    return g


class TestGrafo(unittest.TestCase):
    def test_bfs(self) -> None:
        self.assertEqual(montar().bfs(1), [1, 2, 3, 4, 5])

    def test_dfs(self) -> None:
        self.assertEqual(montar().dfs(1), [1, 2, 4, 3, 5])

    def test_vertice_isolado(self) -> None:
        g = montar()
        self.assertEqual(g.bfs(9), [9])
        self.assertEqual(g.dfs(9), [9])

    def test_origem_inexistente(self) -> None:
        g = Grafo()
        with self.assertRaises(KeyError):
            g.bfs(1)
        with self.assertRaises(KeyError):
            g.dfs(1)
        with self.assertRaises(KeyError):
            g.vizinhos(1)

    def test_aresta_duplicada_e_ciclo(self) -> None:
        g = Grafo()
        g.adicionar_aresta("a", "b")
        g.adicionar_aresta("b", "a")
        g.adicionar_aresta("b", "c")
        g.adicionar_aresta("c", "a")
        self.assertEqual(g.vizinhos("a"), ["b", "c"])
        self.assertEqual(sorted(g.bfs("a")), ["a", "b", "c"])

    def test_caminho_mais_curto(self) -> None:
        g = montar()
        self.assertEqual(g.caminho_mais_curto(1, 5), [1, 2, 4, 5])
        self.assertEqual(g.caminho_mais_curto(1, 1), [1])

    def test_caminho_inalcancavel(self) -> None:
        self.assertIsNone(montar().caminho_mais_curto(1, 9))
        with self.assertRaises(KeyError):
            montar().caminho_mais_curto(1, 100)


if __name__ == "__main__":
    unittest.main()
