import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_scc import componentes_fortes


def normalizar(comps):
    return sorted(sorted(c) for c in comps)


class TestScc(unittest.TestCase):
    def test_classico(self):
        g = {1: [2], 2: [3], 3: [1, 4], 4: [5], 5: [6], 6: [4], 7: [6, 8], 8: [7]}
        self.assertEqual(normalizar(componentes_fortes(g)), [[1, 2, 3], [4, 5, 6], [7, 8]])

    def test_dag_cada_no_sozinho(self):
        g = {"a": ["b"], "b": ["c"], "c": []}
        self.assertEqual(normalizar(componentes_fortes(g)), [["a"], ["b"], ["c"]])

    def test_vazio(self):
        self.assertEqual(componentes_fortes({}), [])

    def test_auto_laco_e_no_so_destino(self):
        g = {"a": ["a", "z"]}
        self.assertEqual(normalizar(componentes_fortes(g)), [["a"], ["z"]])

    def test_ordem_topologica_reversa(self):
        comps = componentes_fortes({1: [2], 2: []})
        self.assertEqual(comps, [[2], [1]])

    def test_cadeia_longa_sem_estourar_pilha(self):
        g = {i: [i + 1] for i in range(5000)}
        g[5000] = [0]
        comps = componentes_fortes(g)
        self.assertEqual(len(comps), 1)
        self.assertEqual(len(comps[0]), 5001)


if __name__ == "__main__":
    unittest.main()
