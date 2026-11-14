import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from contar_vogais import contar_vogais


class TestContarVogais(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(contar_vogais("banana"), 3)

    def test_maiusculas(self):
        self.assertEqual(contar_vogais("AEIOU"), 5)

    def test_acentuadas(self):
        self.assertEqual(contar_vogais("coração é ótimo"), 8)

    def test_sem_vogais(self):
        self.assertEqual(contar_vogais("rhythm sst"), 0)

    def test_vazio(self):
        self.assertEqual(contar_vogais(""), 0)


if __name__ == "__main__":
    unittest.main()
