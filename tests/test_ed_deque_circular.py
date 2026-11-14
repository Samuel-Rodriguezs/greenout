import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_deque_circular import DequeCircular


class TestDequeCircular(unittest.TestCase):
    def test_capacidade_invalida(self) -> None:
        with self.assertRaises(ValueError):
            DequeCircular(0)

    def test_vazio(self) -> None:
        d = DequeCircular(2)
        self.assertTrue(d.vazio())
        with self.assertRaises(IndexError):
            d.remover_inicio()
        with self.assertRaises(IndexError):
            d.remover_fim()

    def test_cheio(self) -> None:
        d = DequeCircular(2)
        d.adicionar_fim(1)
        d.adicionar_fim(2)
        self.assertTrue(d.cheio())
        with self.assertRaises(OverflowError):
            d.adicionar_fim(3)
        with self.assertRaises(OverflowError):
            d.adicionar_inicio(0)

    def test_ordem_misturada(self) -> None:
        d = DequeCircular(4)
        d.adicionar_fim(2)
        d.adicionar_inicio(1)
        d.adicionar_fim(3)
        d.adicionar_inicio(0)
        self.assertEqual(list(d), [0, 1, 2, 3])
        self.assertEqual(d.remover_fim(), 3)
        self.assertEqual(d.remover_inicio(), 0)
        self.assertEqual(list(d), [1, 2])

    def test_volta_circular(self) -> None:
        d = DequeCircular(3)
        for rodada in range(10):
            d.adicionar_fim(rodada)
            d.adicionar_fim(rodada + 100)
            self.assertEqual(d.remover_inicio(), rodada)
            self.assertEqual(d.remover_inicio(), rodada + 100)
        self.assertTrue(d.vazio())

    def test_len(self) -> None:
        d = DequeCircular(3)
        d.adicionar_inicio(1)
        d.adicionar_inicio(2)
        self.assertEqual(len(d), 2)
        self.assertEqual(list(d), [2, 1])


if __name__ == "__main__":
    unittest.main()
