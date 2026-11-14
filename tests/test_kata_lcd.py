import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_lcd import lcd


class TestKataLcd(unittest.TestCase):
    def test_um(self):
        self.assertEqual(lcd(1), "   \n  |\n   \n  |\n   ")

    def test_oito(self):
        self.assertEqual(lcd(8), " - \n| |\n - \n| |\n - ")

    def test_dois(self):
        self.assertEqual(lcd(2), " - \n  |\n - \n|  \n - ")

    def test_varios_digitos(self):
        esperado = "\n".join([
            "     -   - ",
            "  |   |   |",
            "     -   - ",
            "  | |     |",
            "     -   - ",
        ])
        self.assertEqual(lcd(123), esperado)

    def test_tamanho_dois(self):
        linhas = lcd(0, 2).split("\n")
        self.assertEqual(len(linhas), 7)
        self.assertEqual(linhas[0], " -- ")
        self.assertEqual(linhas[1], "|  |")
        self.assertEqual(linhas[2], "|  |")
        self.assertEqual(linhas[3], "    ")
        self.assertEqual(linhas[6], " -- ")

    def test_tamanho_larga_todas_linhas_iguais(self):
        for n in (1, 3):
            linhas = lcd("9081", n).split("\n")
            self.assertEqual(len(linhas), 2 * n + 3)
            self.assertEqual(len({len(l) for l in linhas}), 1)

    def test_numero_como_int_ou_str(self):
        self.assertEqual(lcd(42), lcd("42"))

    def test_zero_a_nove_tem_cinco_linhas(self):
        for d in "0123456789":
            self.assertEqual(len(lcd(d).split("\n")), 5)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            lcd("12a")
        with self.assertRaises(ValueError):
            lcd(-5)
        with self.assertRaises(ValueError):
            lcd(1, 0)


if __name__ == "__main__":
    unittest.main()
