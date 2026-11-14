import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_topologica import CicloDetectado, ordenar_topologicamente


class TestTopologica(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(ordenar_topologicamente({}), [])

    def test_cadeia(self):
        self.assertEqual(ordenar_topologicamente({"c": ["b"], "b": ["a"]}), ["a", "b", "c"])

    def test_diamante_deterministico(self):
        deps = {"d": ["b", "c"], "b": ["a"], "c": ["a"]}
        self.assertEqual(ordenar_topologicamente(deps), ["a", "b", "c", "d"])

    def test_independentes_ordem_natural(self):
        self.assertEqual(ordenar_topologicamente({"z": [], "m": [], "a": []}), ["a", "m", "z"])

    def test_ciclo(self):
        with self.assertRaises(CicloDetectado):
            ordenar_topologicamente({"a": ["b"], "b": ["a"]})

    def test_auto_ciclo(self):
        with self.assertRaises(CicloDetectado):
            ordenar_topologicamente({"a": ["a"]})

    def test_ordem_respeita_dependencias(self):
        deps = {5: [2, 0], 4: [0, 1], 2: [3], 3: [1]}
        ordem = ordenar_topologicamente(deps)
        for no, ds in deps.items():
            for d in ds:
                self.assertLess(ordem.index(d), ordem.index(no))


if __name__ == "__main__":
    unittest.main()
