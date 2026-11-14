import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_topo_tarefas import CicloDependenciaError, niveis_paralelos, ordenar_tarefas


class TestTopoTarefas(unittest.TestCase):
    def test_ordem_basica(self):
        deps = {"deploy": ["teste", "build"], "teste": ["build"], "build": []}
        self.assertEqual(ordenar_tarefas(deps), ["build", "teste", "deploy"])

    def test_dependencia_so_citada(self):
        self.assertEqual(ordenar_tarefas({"b": ["a"]}), ["a", "b"])

    def test_vazio(self):
        self.assertEqual(ordenar_tarefas({}), [])
        self.assertEqual(niveis_paralelos({}), [])

    def test_desempate_alfabetico(self):
        self.assertEqual(ordenar_tarefas({"z": [], "a": [], "m": []}), ["a", "m", "z"])

    def test_ciclo(self):
        with self.assertRaises(CicloDependenciaError):
            ordenar_tarefas({"a": ["b"], "b": ["a"]})

    def test_auto_dependencia(self):
        with self.assertRaises(CicloDependenciaError):
            ordenar_tarefas({"a": ["a"]})

    def test_dependencia_duplicada(self):
        self.assertEqual(ordenar_tarefas({"b": ["a", "a"]}), ["a", "b"])

    def test_niveis(self):
        deps = {"c": ["a", "b"], "d": ["c"], "a": [], "b": []}
        self.assertEqual(niveis_paralelos(deps), [["a", "b"], ["c"], ["d"]])


if __name__ == "__main__":
    unittest.main()
