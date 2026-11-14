import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_btree import BTree


class TestBTree(unittest.TestCase):
    def test_grau_invalido(self):
        with self.assertRaises(ValueError):
            BTree(1)

    def test_vazia(self):
        b = BTree()
        self.assertIsNone(b.buscar(1))
        self.assertFalse(b.remover(1))
        self.assertEqual(list(b.itens()), [])

    def test_inserir_buscar_ordenado(self):
        b = BTree(2)
        for i in range(100):
            b.inserir(i, str(i))
        self.assertEqual(len(b), 100)
        self.assertEqual(b.buscar(37), "37")
        self.assertEqual([k for k, _ in b.itens()], list(range(100)))
        self.assertTrue(b.validar())
        self.assertGreater(b.altura(), 1)

    def test_substitui_duplicada(self):
        b = BTree(3)
        b.inserir(5, "a")
        b.inserir(5, "b")
        self.assertEqual(len(b), 1)
        self.assertEqual(b.buscar(5), "b")

    def test_contem_valor_none(self):
        b = BTree()
        b.inserir(1)
        self.assertIn(1, b)
        self.assertNotIn(2, b)

    def test_remocao_aleatoria_mantem_invariantes(self):
        rnd = random.Random(7)
        for t in (2, 3, 5):
            b = BTree(t)
            chaves = list(range(300))
            rnd.shuffle(chaves)
            for k in chaves:
                b.inserir(k, k * 2)
            rnd.shuffle(chaves)
            restantes = set(chaves)
            for k in chaves[:250]:
                self.assertTrue(b.remover(k))
                restantes.discard(k)
                self.assertTrue(b.validar())
            self.assertEqual([k for k, _ in b.itens()], sorted(restantes))
            self.assertFalse(b.remover(chaves[0]))
            for k in chaves[250:]:
                b.remover(k)
            self.assertEqual(len(b), 0)
            self.assertEqual(b.altura(), 1)

    def test_remover_inexistente(self):
        b = BTree()
        b.inserir(1)
        self.assertFalse(b.remover(2))
        self.assertEqual(len(b), 1)


if __name__ == "__main__":
    unittest.main()
