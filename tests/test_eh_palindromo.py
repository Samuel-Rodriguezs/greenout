import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from eh_palindromo import eh_palindromo


class TestEhPalindromo(unittest.TestCase):
    def test_palavra(self):
        self.assertTrue(eh_palindromo("arara"))
        self.assertFalse(eh_palindromo("python"))

    def test_frase_com_acentos_e_pontuacao(self):
        self.assertTrue(eh_palindromo("Socorram-me, subi no ônibus em Marrocos"))
        self.assertTrue(eh_palindromo("Anotaram a data da maratona"))

    def test_vazio_e_um_caractere(self):
        self.assertTrue(eh_palindromo(""))
        self.assertTrue(eh_palindromo("a"))
        self.assertTrue(eh_palindromo("!?"))

    def test_numeros(self):
        self.assertTrue(eh_palindromo("12321"))
        self.assertFalse(eh_palindromo("1231"))


if __name__ == "__main__":
    unittest.main()
