import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_euleriano import caminho_euleriano


def usa_todas(caminho, arestas):
    pares = sorted(tuple(sorted(p)) for p in zip(caminho, caminho[1:]))
    return pares == sorted(tuple(sorted(a)) for a in arestas)


class TestEuleriano(unittest.TestCase):
    def test_circuito(self):
        a = [(1, 2), (2, 3), (3, 1)]
        c = caminho_euleriano(a)
        self.assertEqual(c[0], c[-1])
        self.assertTrue(usa_todas(c, a))

    def test_caminho_aberto(self):
        a = [(1, 2), (2, 3), (3, 4), (4, 2)]
        c = caminho_euleriano(a)
        self.assertIn(c[0], (1, 3))
        self.assertTrue(usa_todas(c, a))

    def test_impossivel_quatro_impares(self):
        self.assertIsNone(caminho_euleriano([(1, 2), (1, 3), (1, 4), (1, 5)]))

    def test_desconexo(self):
        self.assertIsNone(caminho_euleriano([(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)]))

    def test_vazio_e_auto_laco(self):
        self.assertEqual(caminho_euleriano([]), [])
        self.assertEqual(caminho_euleriano([("a", "a")]), ["a", "a"])

    def test_pontes_konigsberg(self):
        a = [("A", "B"), ("A", "B"), ("A", "C"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")]
        self.assertIsNone(caminho_euleriano(a))


if __name__ == "__main__":
    unittest.main()
