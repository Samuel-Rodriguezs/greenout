import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_fibonacci_words import caractere, comprimento, palavra, palavra_infinita_prefixo, palavras


class TestKataFibonacciWords(unittest.TestCase):
    def test_primeiras_palavras(self):
        self.assertEqual(list(palavras(6)), ["0", "01", "010", "01001", "01001010", "0100101001001"])

    def test_palavra_individual(self):
        self.assertEqual(palavra(0), "0")
        self.assertEqual(palavra(1), "01")
        self.assertEqual(palavra(5), "0100101001001")

    def test_recorrencia(self):
        for n in range(2, 15):
            self.assertEqual(palavra(n), palavra(n - 1) + palavra(n - 2))

    def test_comprimento(self):
        for n in range(0, 20):
            self.assertEqual(comprimento(n), len(palavra(n)))
        self.assertEqual(comprimento(30), 2178309)

    def test_caractere_confere_com_palavra(self):
        longa = palavra(15)
        for i, c in enumerate(longa):
            self.assertEqual(caractere(i), c)

    def test_prefixo_infinito(self):
        self.assertEqual(palavra_infinita_prefixo(0), "")
        self.assertEqual(palavra_infinita_prefixo(1), "0")
        self.assertEqual(palavra_infinita_prefixo(8), "01001010")
        self.assertEqual(palavra_infinita_prefixo(30), palavra(8)[:30])

    def test_nao_ha_dois_uns_seguidos(self):
        self.assertNotIn("11", palavra(12))

    def test_invalidos(self):
        for f in (palavra, comprimento, caractere, palavra_infinita_prefixo):
            with self.assertRaises(ValueError):
                f(-1)


if __name__ == "__main__":
    unittest.main()
