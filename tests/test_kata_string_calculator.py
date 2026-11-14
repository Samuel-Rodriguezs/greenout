import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_string_calculator import somar


class TestKataStringCalculator(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(somar(""), 0)

    def test_um_e_dois(self):
        self.assertEqual(somar("1"), 1)
        self.assertEqual(somar("1,2"), 3)

    def test_varios(self):
        self.assertEqual(somar("1,2,3,4,5"), 15)

    def test_quebra_de_linha(self):
        self.assertEqual(somar("1\n2,3"), 6)

    def test_delimitador_custom(self):
        self.assertEqual(somar("//;\n1;2"), 3)

    def test_negativos(self):
        with self.assertRaises(ValueError) as ctx:
            somar("1,-2,-5")
        self.assertIn("-2, -5", str(ctx.exception))

    def test_maiores_que_mil_ignorados(self):
        self.assertEqual(somar("2,1001"), 2)
        self.assertEqual(somar("1000,1"), 1001)

    def test_delimitador_longo(self):
        self.assertEqual(somar("//[***]\n1***2***3"), 6)

    def test_multiplos_delimitadores(self):
        self.assertEqual(somar("//[*][%]\n1*2%3"), 6)

    def test_delimitador_especial_regex(self):
        self.assertEqual(somar("//.\n1.2"), 3)


if __name__ == "__main__":
    unittest.main()
