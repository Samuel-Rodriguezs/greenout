import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_trie import Trie


class TestTrie(unittest.TestCase):
    def test_vazia(self) -> None:
        trie = Trie()
        self.assertEqual(len(trie), 0)
        self.assertFalse(trie.contem("a"))
        self.assertEqual(trie.com_prefixo(""), [])

    def test_inserir_e_contem(self) -> None:
        trie = Trie()
        trie.inserir("casa")
        self.assertTrue(trie.contem("casa"))
        self.assertFalse(trie.contem("cas"))
        self.assertTrue(trie.tem_prefixo("cas"))
        self.assertFalse(trie.tem_prefixo("x"))

    def test_duplicado(self) -> None:
        trie = Trie()
        self.assertTrue(trie.inserir("a"))
        self.assertFalse(trie.inserir("a"))
        self.assertEqual(len(trie), 1)

    def test_com_prefixo_ordenado(self) -> None:
        trie = Trie()
        for p in ("casa", "caso", "cama", "carro", "dado", "ca"):
            trie.inserir(p)
        self.assertEqual(trie.com_prefixo("ca"), ["ca", "cama", "carro", "casa", "caso"])
        self.assertEqual(trie.com_prefixo("cas"), ["casa", "caso"])
        self.assertEqual(trie.com_prefixo("z"), [])
        self.assertEqual(len(trie.com_prefixo("")), 6)

    def test_palavra_vazia(self) -> None:
        trie = Trie()
        trie.inserir("")
        self.assertTrue(trie.contem(""))
        self.assertEqual(len(trie), 1)

    def test_remover_preserva_prefixo_compartilhado(self) -> None:
        trie = Trie()
        trie.inserir("casa")
        trie.inserir("cas")
        trie.remover("casa")
        self.assertFalse(trie.contem("casa"))
        self.assertTrue(trie.contem("cas"))
        trie.remover("cas")
        self.assertFalse(trie.tem_prefixo("c"))
        self.assertEqual(len(trie), 0)

    def test_remover_inexistente(self) -> None:
        trie = Trie()
        trie.inserir("casa")
        with self.assertRaises(KeyError):
            trie.remover("cas")


if __name__ == "__main__":
    unittest.main()
