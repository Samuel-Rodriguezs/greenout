import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_iterator import ArvoreOrdenada, Paginas


class TestIterator(unittest.TestCase):
    def test_paginas(self):
        p = Paginas(list(range(1, 8)), 3)
        self.assertEqual(len(p), 3)
        self.assertEqual(list(p), [[1, 2, 3], [4, 5, 6], [7]])
        self.assertEqual(p[-1], [7])

    def test_paginas_invalidas(self):
        with self.assertRaises(ValueError):
            Paginas([1], 0)
        with self.assertRaises(IndexError):
            Paginas([1], 1)[5]

    def test_paginas_vazia(self):
        self.assertEqual(list(Paginas([], 2)), [])

    def test_arvore_em_ordem(self):
        a = ArvoreOrdenada()
        for v in (5, 3, 8, 1, 4, 9, 7):
            a.inserir(v)
        self.assertEqual(list(a), [1, 3, 4, 5, 7, 8, 9])

    def test_reiteravel(self):
        a = ArvoreOrdenada()
        a.inserir(2)
        self.assertEqual(list(a), list(a))
        self.assertEqual(list(ArvoreOrdenada()), [])


if __name__ == "__main__":
    unittest.main()
