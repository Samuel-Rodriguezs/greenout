import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_fold import dobrar, dobrar_linha, main


class TestUniFold(unittest.TestCase):
    def test_curta(self):
        self.assertEqual(dobrar_linha("abc", 5), ["abc"])

    def test_exata(self):
        self.assertEqual(dobrar_linha("abcde", 5), ["abcde"])

    def test_quebra(self):
        self.assertEqual(dobrar_linha("abcdefghijk", 4), ["abcd", "efgh", "ijk"])

    def test_em_espacos(self):
        self.assertEqual(dobrar_linha("aaa bbb ccc", 8, True), ["aaa bbb ", "ccc"])

    def test_palavra_longa_sem_espaco(self):
        self.assertEqual(dobrar_linha("abcdefgh", 3, True), ["abc", "def", "gh"])

    def test_linha_vazia_preservada(self):
        self.assertEqual(dobrar(["", "abc"], 2), ["", "ab", "c"])

    def test_largura_invalida(self):
        with self.assertRaises(ValueError):
            dobrar_linha("abc", 0)

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-w", "3"], "abcdef\n", s), 0)
        self.assertEqual(s.getvalue(), "abc\ndef\n")

    def test_main_erros(self):
        self.assertEqual(main(["-w", "0"], "a\n", StringIO()), 2)
        self.assertEqual(main(["-w", "x"], "", StringIO()), 2)
        self.assertEqual(main(["-q"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
