import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from decimal_binario import binario_para_decimal, decimal_para_binario


class TestDecimalBinario(unittest.TestCase):
    def test_para_binario(self):
        self.assertEqual(decimal_para_binario(10), "1010")
        self.assertEqual(decimal_para_binario(1), "1")

    def test_zero(self):
        self.assertEqual(decimal_para_binario(0), "0")
        self.assertEqual(binario_para_decimal("0"), 0)

    def test_negativo(self):
        self.assertEqual(decimal_para_binario(-5), "-101")
        self.assertEqual(binario_para_decimal("-101"), -5)

    def test_para_decimal(self):
        self.assertEqual(binario_para_decimal("1010"), 10)
        self.assertEqual(binario_para_decimal("00101"), 5)

    def test_invalidos(self):
        for texto in ("", "-", "102", "abc", "1 0"):
            with self.assertRaises(ValueError):
                binario_para_decimal(texto)

    def test_ida_e_volta(self):
        for n in range(-130, 131):
            self.assertEqual(binario_para_decimal(decimal_para_binario(n)), n)
            if n >= 0:
                self.assertEqual(decimal_para_binario(n), bin(n)[2:])


if __name__ == "__main__":
    unittest.main()
