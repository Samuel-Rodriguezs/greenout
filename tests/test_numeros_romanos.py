import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from numeros_romanos import inteiro_para_romano, romano_para_inteiro


class TestNumerosRomanos(unittest.TestCase):
    def test_para_romano(self):
        casos = {1: "I", 4: "IV", 9: "IX", 14: "XIV", 40: "XL", 90: "XC",
                 400: "CD", 1994: "MCMXCIV", 2024: "MMXXIV", 3999: "MMMCMXCIX"}
        for n, esperado in casos.items():
            self.assertEqual(inteiro_para_romano(n), esperado)

    def test_fora_do_intervalo(self):
        for n in (0, -1, 4000):
            with self.assertRaises(ValueError):
                inteiro_para_romano(n)

    def test_para_inteiro(self):
        self.assertEqual(romano_para_inteiro("MCMXCIV"), 1994)
        self.assertEqual(romano_para_inteiro("IV"), 4)

    def test_romano_invalido(self):
        for texto in ("", "IIII", "VX", "IC", "ABC", "mcm"):
            with self.assertRaises(ValueError):
                romano_para_inteiro(texto)

    def test_ida_e_volta_completa(self):
        for n in range(1, 4000):
            self.assertEqual(romano_para_inteiro(inteiro_para_romano(n)), n)


if __name__ == "__main__":
    unittest.main()
