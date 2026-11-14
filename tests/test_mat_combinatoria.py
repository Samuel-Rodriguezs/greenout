import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from mat_combinatoria import (arranjo, combinacao, fatorial, permutacoes,
                              permutacoes_com_repeticao)


class TestCombinatoria(unittest.TestCase):
    def test_fatorial(self):
        self.assertEqual(fatorial(0), 1)
        self.assertEqual(fatorial(10), 3628800)
        with self.assertRaises(ValueError):
            fatorial(-1)

    def test_combinacao(self):
        self.assertEqual(combinacao(5, 2), 10)
        self.assertEqual(combinacao(52, 5), 2598960)
        self.assertEqual(combinacao(10, 0), 1)
        self.assertEqual(combinacao(10, 10), 1)
        self.assertEqual(combinacao(3, 5), 0)
        self.assertEqual(combinacao(100, 50), math.comb(100, 50))

    def test_arranjo(self):
        self.assertEqual(arranjo(5, 2), 20)
        self.assertEqual(arranjo(5, 0), 1)
        self.assertEqual(arranjo(3, 4), 0)

    def test_permutacoes(self):
        p = list(permutacoes([1, 2, 3]))
        self.assertEqual(len(p), 6)
        self.assertIn((3, 1, 2), p)
        self.assertEqual(list(permutacoes([])), [()])

    def test_anagramas(self):
        self.assertEqual(permutacoes_com_repeticao("banana"), 60)
        self.assertEqual(permutacoes_com_repeticao("abc"), 6)

    def test_negativos(self):
        with self.assertRaises(ValueError):
            combinacao(-1, 2)
        with self.assertRaises(ValueError):
            arranjo(2, -1)


if __name__ == "__main__":
    unittest.main()
