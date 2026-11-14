import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_mochila import mochila


class TesteMochila(unittest.TestCase):
    def test_exemplo_classico(self):
        self.assertEqual(mochila([1, 3, 4, 5], [1, 4, 5, 7], 7), 9)

    def test_sem_itens(self):
        self.assertEqual(mochila([], [], 10), 0)

    def test_capacidade_zero(self):
        self.assertEqual(mochila([1, 2], [10, 20], 0), 0)

    def test_item_maior_que_capacidade(self):
        self.assertEqual(mochila([10], [100], 5), 0)

    def test_item_usado_uma_vez(self):
        self.assertEqual(mochila([2], [3], 10), 3)

    def test_todos_cabem(self):
        self.assertEqual(mochila([1, 2, 3], [6, 10, 12], 6), 28)

    def test_tamanhos_diferentes(self):
        with self.assertRaises(ValueError):
            mochila([1], [1, 2], 3)

    def test_capacidade_negativa(self):
        with self.assertRaises(ValueError):
            mochila([1], [1], -1)


if __name__ == "__main__":
    unittest.main()
