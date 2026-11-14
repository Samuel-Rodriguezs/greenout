import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from cifra_cesar import cifrar_cesar, decifrar_cesar


class TestCifraCesar(unittest.TestCase):
    def test_deslocamento_simples(self):
        self.assertEqual(cifrar_cesar("abc", 3), "def")

    def test_volta_ao_alfabeto(self):
        self.assertEqual(cifrar_cesar("xyz", 3), "abc")

    def test_preserva_maiusculas_e_simbolos(self):
        self.assertEqual(cifrar_cesar("Olá, Mundo!", 1), "Pmá, Nvoep!")

    def test_deslocamento_negativo_e_grande(self):
        self.assertEqual(cifrar_cesar("abc", -1), "zab")
        self.assertEqual(cifrar_cesar("abc", 29), "def")

    def test_texto_vazio(self):
        self.assertEqual(cifrar_cesar("", 5), "")

    def test_decifrar_inverte_cifrar(self):
        self.assertEqual(decifrar_cesar(cifrar_cesar("Teste ZzAa", 7), 7), "Teste ZzAa")


if __name__ == "__main__":
    unittest.main()
