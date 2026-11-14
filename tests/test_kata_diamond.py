import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_diamond import losango


class TestKataDiamond(unittest.TestCase):
    def test_a(self):
        self.assertEqual(losango("A"), "A")

    def test_b(self):
        self.assertEqual(losango("B"), " A \nB B\n A ")

    def test_c(self):
        esperado = "  A  \n B B \nC   C\n B B \n  A  "
        self.assertEqual(losango("C"), esperado)

    def test_propriedades(self):
        for letra in "ADHZ":
            linhas = losango(letra).split("\n")
            n = ord(letra) - 64
            self.assertEqual(len(linhas), 2 * n - 1)
            self.assertTrue(all(len(l) == 2 * n - 1 for l in linhas))
            self.assertEqual(linhas, linhas[::-1])
            self.assertTrue(all(l == l[::-1] for l in linhas))

    def test_minuscula(self):
        self.assertEqual(losango("b"), losango("B"))

    def test_invalido(self):
        for ruim in ["", "AB", "1", "é"]:
            with self.assertRaises(ValueError):
                losango(ruim)


if __name__ == "__main__":
    unittest.main()
