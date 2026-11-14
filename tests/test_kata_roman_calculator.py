import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_roman_calculator import para_inteiro, para_romano, somar, subtrair


class TestKataRomanCalculator(unittest.TestCase):
    def test_soma_simples(self):
        self.assertEqual(somar("I", "I"), "II")
        self.assertEqual(somar("I", "II"), "III")

    def test_soma_com_subtrativo(self):
        self.assertEqual(somar("II", "II"), "IV")
        self.assertEqual(somar("IV", "V"), "IX")
        self.assertEqual(somar("XL", "XL"), "LXXX")
        self.assertEqual(somar("CM", "C"), "M")

    def test_soma_grande(self):
        self.assertEqual(somar("MCMXCIX", "I"), "MM")
        self.assertEqual(somar("MMM", "CMXCIX"), "MMMCMXCIX")

    def test_subtracao(self):
        self.assertEqual(subtrair("V", "I"), "IV")
        self.assertEqual(subtrair("X", "I"), "IX")
        self.assertEqual(subtrair("MM", "I"), "MCMXCIX")

    def test_resultado_nao_positivo(self):
        with self.assertRaises(ValueError):
            subtrair("I", "I")
        with self.assertRaises(ValueError):
            subtrair("I", "V")

    def test_estouro(self):
        with self.assertRaises(ValueError):
            somar("MMMCMXCIX", "I")

    def test_ida_e_volta(self):
        for n in range(1, 4000):
            self.assertEqual(para_inteiro(para_romano(n)), n)

    def test_invalidos(self):
        for ruim in ["", "IIII", "VV", "IC", "ABC", "IIV", "MMMM"]:
            with self.assertRaises(ValueError, msg=ruim):
                para_inteiro(ruim)


if __name__ == "__main__":
    unittest.main()
