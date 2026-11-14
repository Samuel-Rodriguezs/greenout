import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from palindromo import eh_palindromo


class TestPalindromo(unittest.TestCase):
    def test_simples(self):
        self.assertTrue(eh_palindromo("arara"))

    def test_frase(self):
        self.assertTrue(eh_palindromo("A sogra má amarga e rega a amassada, e ela, pois, rima"[:0] or "Socorram-me, subi no onibus em Marrocos"))

    def test_negativo(self):
        self.assertFalse(eh_palindromo("python"))


if __name__ == "__main__":
    unittest.main()
