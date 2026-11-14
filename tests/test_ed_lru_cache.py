import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_lru_cache import LRUCache


class TestLRUCache(unittest.TestCase):
    def test_capacidade_invalida(self) -> None:
        with self.assertRaises(ValueError):
            LRUCache(0)

    def test_vazio(self) -> None:
        cache = LRUCache(2)
        self.assertEqual(len(cache), 0)
        self.assertIsNone(cache.obter("a"))
        self.assertEqual(cache.obter("a", -1), -1)

    def test_despejo_do_menos_recente(self) -> None:
        cache = LRUCache(2)
        cache.colocar("a", 1)
        cache.colocar("b", 2)
        cache.colocar("c", 3)
        self.assertNotIn("a", cache)
        self.assertEqual(cache.chaves(), ["b", "c"])

    def test_obter_atualiza_recencia(self) -> None:
        cache = LRUCache(2)
        cache.colocar("a", 1)
        cache.colocar("b", 2)
        self.assertEqual(cache.obter("a"), 1)
        cache.colocar("c", 3)
        self.assertIn("a", cache)
        self.assertNotIn("b", cache)

    def test_sobrescrever_nao_despeja(self) -> None:
        cache = LRUCache(2)
        cache.colocar("a", 1)
        cache.colocar("b", 2)
        cache.colocar("a", 10)
        self.assertEqual(len(cache), 2)
        self.assertEqual(cache.obter("a"), 10)
        self.assertEqual(cache.chaves(), ["b", "a"])

    def test_valor_falsy_armazenado(self) -> None:
        cache = LRUCache(1)
        cache.colocar("a", 0)
        self.assertEqual(cache.obter("a", -1), 0)

    def test_capacidade_um(self) -> None:
        cache = LRUCache(1)
        cache.colocar("a", 1)
        cache.colocar("b", 2)
        self.assertEqual(cache.chaves(), ["b"])


if __name__ == "__main__":
    unittest.main()
