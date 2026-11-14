import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from soma_digitos import raiz_digital, soma_digitos


class TestSomaDigitos(unittest.TestCase):
    def test_soma(self):
        self.assertEqual(soma_digitos(1234), 10)

    def test_zero_e_um_digito(self):
        self.assertEqual(soma_digitos(0), 0)
        self.assertEqual(soma_digitos(7), 7)

    def test_negativo(self):
        self.assertEqual(soma_digitos(-905), 14)

    def test_raiz_digital(self):
        self.assertEqual(raiz_digital(9875), 2)
        self.assertEqual(raiz_digital(0), 0)
        self.assertEqual(raiz_digital(9), 9)
        self.assertEqual(raiz_digital(-38), 2)


if __name__ == "__main__":
    unittest.main()
