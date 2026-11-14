import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from inverter_palavras import inverter_palavras


class TestInverterPalavras(unittest.TestCase):
    def test_frase(self):
        self.assertEqual(inverter_palavras("eu amo python"), "python amo eu")

    def test_uma_palavra(self):
        self.assertEqual(inverter_palavras("python"), "python")

    def test_espacos_extras(self):
        self.assertEqual(inverter_palavras("  a   b  "), "b a")

    def test_vazio_e_so_espacos(self):
        self.assertEqual(inverter_palavras(""), "")
        self.assertEqual(inverter_palavras("   "), "")


if __name__ == "__main__":
    unittest.main()
