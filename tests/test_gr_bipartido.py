import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_bipartido import bipartir, eh_bipartido


class TestBipartido(unittest.TestCase):
    def test_ciclo_par(self):
        partes = bipartir({1: [2], 2: [3], 3: [4], 4: [1]})
        self.assertEqual(sorted(map(sorted, partes)), [[1, 3], [2, 4]])

    def test_ciclo_impar(self):
        self.assertFalse(eh_bipartido({1: [2], 2: [3], 3: [1]}))

    def test_vazio(self):
        self.assertEqual(bipartir({}), (set(), set()))

    def test_desconexo(self):
        g = {1: [2], 3: [4], 5: []}
        self.assertTrue(eh_bipartido(g))
        a, b = bipartir(g)
        self.assertEqual(len(a | b), 5)

    def test_auto_laco(self):
        self.assertFalse(eh_bipartido({1: [1]}))

    def test_arvore(self):
        self.assertTrue(eh_bipartido({"r": ["a", "b"], "a": ["c"]}))


if __name__ == "__main__":
    unittest.main()
