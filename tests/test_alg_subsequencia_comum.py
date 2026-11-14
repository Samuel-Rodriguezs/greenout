import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_subsequencia_comum import maior_subsequencia_comum


def eh_subsequencia(sub: str, texto: str) -> bool:
    it = iter(texto)
    return all(c in it for c in sub)


class TesteSubsequenciaComum(unittest.TestCase):
    def test_exemplo_classico(self):
        r = maior_subsequencia_comum("ABCBDAB", "BDCABA")
        self.assertEqual(len(r), 4)
        self.assertTrue(eh_subsequencia(r, "ABCBDAB"))
        self.assertTrue(eh_subsequencia(r, "BDCABA"))

    def test_strings_vazias(self):
        self.assertEqual(maior_subsequencia_comum("", "abc"), "")
        self.assertEqual(maior_subsequencia_comum("abc", ""), "")
        self.assertEqual(maior_subsequencia_comum("", ""), "")

    def test_sem_caracteres_comuns(self):
        self.assertEqual(maior_subsequencia_comum("abc", "xyz"), "")

    def test_iguais(self):
        self.assertEqual(maior_subsequencia_comum("python", "python"), "python")

    def test_uma_contida_na_outra(self):
        self.assertEqual(maior_subsequencia_comum("ace", "abcde"), "ace")

    def test_repeticoes(self):
        self.assertEqual(maior_subsequencia_comum("aaaa", "aa"), "aa")


if __name__ == "__main__":
    unittest.main()
