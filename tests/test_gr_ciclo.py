import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_ciclo import ciclo_direcionado, tem_ciclo_nao_direcionado


class TestCiclo(unittest.TestCase):
    def test_dag(self):
        self.assertIsNone(ciclo_direcionado({"a": ["b", "c"], "b": ["c"], "c": []}))

    def test_ciclo_simples(self):
        c = ciclo_direcionado({"a": ["b"], "b": ["c"], "c": ["a"]})
        self.assertEqual(c[0], c[-1])
        self.assertEqual(set(c), {"a", "b", "c"})

    def test_auto_laco(self):
        self.assertEqual(ciclo_direcionado({1: [1]}), [1, 1])

    def test_vazio(self):
        self.assertIsNone(ciclo_direcionado({}))

    def test_ciclo_longe_da_raiz(self):
        c = ciclo_direcionado({1: [2], 2: [3], 3: [4], 4: [3]})
        self.assertEqual(c, [3, 4, 3])

    def test_nao_direcionado(self):
        self.assertFalse(tem_ciclo_nao_direcionado(4, [(0, 1), (1, 2), (2, 3)]))
        self.assertTrue(tem_ciclo_nao_direcionado(3, [(0, 1), (1, 2), (2, 0)]))
        self.assertTrue(tem_ciclo_nao_direcionado(2, [(0, 1), (1, 0)]))
        self.assertTrue(tem_ciclo_nao_direcionado(1, [(0, 0)]))
        self.assertFalse(tem_ciclo_nao_direcionado(0, []))


if __name__ == "__main__":
    unittest.main()
