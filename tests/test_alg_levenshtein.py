import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_levenshtein import distancia_edicao


class TesteLevenshtein(unittest.TestCase):
    def test_kitten_sitting(self):
        self.assertEqual(distancia_edicao("kitten", "sitting"), 3)

    def test_iguais(self):
        self.assertEqual(distancia_edicao("abc", "abc"), 0)

    def test_vazias(self):
        self.assertEqual(distancia_edicao("", ""), 0)

    def test_uma_vazia(self):
        self.assertEqual(distancia_edicao("", "abcd"), 4)
        self.assertEqual(distancia_edicao("abcd", ""), 4)

    def test_simetria(self):
        self.assertEqual(distancia_edicao("domingo", "dominó"), distancia_edicao("dominó", "domingo"))

    def test_substituicao_unica(self):
        self.assertEqual(distancia_edicao("casa", "cala"), 1)

    def test_totalmente_diferentes(self):
        self.assertEqual(distancia_edicao("abc", "xyz"), 3)


if __name__ == "__main__":
    unittest.main()
