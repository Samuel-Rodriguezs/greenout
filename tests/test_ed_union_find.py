import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_union_find import UnionFind


class TestUnionFind(unittest.TestCase):
    def test_inicial(self) -> None:
        uf = UnionFind(5)
        self.assertEqual(uf.componentes, 5)
        self.assertFalse(uf.conectados(0, 1))
        self.assertTrue(uf.conectados(2, 2))
        self.assertEqual(uf.tamanho(3), 1)

    def test_vazio(self) -> None:
        uf = UnionFind(0)
        self.assertEqual(uf.componentes, 0)
        with self.assertRaises(IndexError):
            uf.encontrar(0)

    def test_n_negativo(self) -> None:
        with self.assertRaises(ValueError):
            UnionFind(-1)

    def test_unir(self) -> None:
        uf = UnionFind(6)
        self.assertTrue(uf.unir(0, 1))
        self.assertTrue(uf.unir(1, 2))
        self.assertTrue(uf.conectados(0, 2))
        self.assertEqual(uf.componentes, 4)
        self.assertEqual(uf.tamanho(2), 3)

    def test_unir_repetido(self) -> None:
        uf = UnionFind(3)
        uf.unir(0, 1)
        self.assertFalse(uf.unir(1, 0))
        self.assertEqual(uf.componentes, 2)

    def test_fora_do_intervalo(self) -> None:
        uf = UnionFind(3)
        with self.assertRaises(IndexError):
            uf.unir(0, 3)
        with self.assertRaises(IndexError):
            uf.encontrar(-1)

    def test_cadeia_longa(self) -> None:
        uf = UnionFind(1000)
        for i in range(999):
            uf.unir(i, i + 1)
        self.assertEqual(uf.componentes, 1)
        self.assertTrue(uf.conectados(0, 999))
        self.assertEqual(uf.tamanho(500), 1000)


if __name__ == "__main__":
    unittest.main()
