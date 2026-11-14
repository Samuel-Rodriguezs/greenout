import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_word_wrap import quebrar


class TestKataWordWrap(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(quebrar("", 5), "")

    def test_palavra_curta(self):
        self.assertEqual(quebrar("oi", 5), "oi")

    def test_palavra_longa_cortada(self):
        self.assertEqual(quebrar("abcdefgh", 3), "abc\ndef\ngh")

    def test_quebra_no_espaco(self):
        self.assertEqual(quebrar("uma frase", 5), "uma\nfrase")

    def test_varias_palavras(self):
        self.assertEqual(quebrar("a b c d e", 3), "a b\nc d\ne")

    def test_largura_exata(self):
        self.assertEqual(quebrar("abc def", 7), "abc def")
        self.assertEqual(quebrar("abc def", 6), "abc\ndef")

    def test_espacos_extras(self):
        self.assertEqual(quebrar("  a    b  ", 10), "a b")

    def test_palavra_longa_no_meio(self):
        self.assertEqual(quebrar("oi abcdefg ok", 4), "oi\nabcd\nefg\nok")

    def test_paragrafos_preservados(self):
        self.assertEqual(quebrar("ab cd\nef", 5), "ab cd\nef")

    def test_largura_invalida(self):
        with self.assertRaises(ValueError):
            quebrar("x", 0)

    def test_nenhuma_linha_excede(self):
        texto = "o rato roeu a roupa do rei de Roma " * 5
        for l in quebrar(texto, 11).split("\n"):
            self.assertLessEqual(len(l), 11)


if __name__ == "__main__":
    unittest.main()
