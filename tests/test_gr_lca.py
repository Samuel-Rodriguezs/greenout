import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_lca import LcaArvore, No, lca_binaria


def arvore():
    #        3
    #      5   1
    #     6 2 0 8
    #      7 4
    return No(3, No(5, No(6), No(2, No(7), No(4))), No(1, No(0), No(8)))


class TestLca(unittest.TestCase):
    def test_binaria(self):
        r = arvore()
        self.assertEqual(lca_binaria(r, 5, 1).valor, 3)
        self.assertEqual(lca_binaria(r, 5, 4).valor, 5)
        self.assertEqual(lca_binaria(r, 7, 4).valor, 2)
        self.assertEqual(lca_binaria(r, 6, 6).valor, 6)

    def test_binaria_inexistente_e_vazia(self):
        self.assertIsNone(lca_binaria(arvore(), 5, 99))
        self.assertIsNone(lca_binaria(None, 1, 2))

    def test_lifting(self):
        t = LcaArvore(7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (5, 6)])
        self.assertEqual(t.lca(3, 4), 1)
        self.assertEqual(t.lca(3, 6), 0)
        self.assertEqual(t.lca(6, 5), 5)
        self.assertEqual(t.lca(2, 2), 2)
        self.assertEqual(t.distancia(3, 6), 5)

    def test_no_unico(self):
        t = LcaArvore(1, [])
        self.assertEqual(t.lca(0, 0), 0)

    def test_cadeia_profunda(self):
        n = 1000
        t = LcaArvore(n, [(i, i + 1) for i in range(n - 1)])
        self.assertEqual(t.lca(999, 500), 500)
        self.assertEqual(t.distancia(0, 999), 999)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            LcaArvore(0, [])
        with self.assertRaises(ValueError):
            LcaArvore(3, [(0, 1)])


if __name__ == "__main__":
    unittest.main()
