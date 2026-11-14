import shlex
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_shlex import ErroShlex, citar, dividir, juntar


class TestFmtShlex(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(dividir("  ls   -la\t/tmp  "), ["ls", "-la", "/tmp"])
        self.assertEqual(dividir(""), [])

    def test_aspas(self):
        self.assertEqual(dividir("echo 'a b' \"c d\" e\\ f"), ["echo", "a b", "c d", "e f"])
        self.assertEqual(dividir("a'b'\"c\"d"), ["abcd"])
        self.assertEqual(dividir("'' \"\""), ["", ""])

    def test_escapes_em_aspas_duplas(self):
        self.assertEqual(dividir(r'"a\"b\\c\n"'), ['a"b\\c\\n'])
        self.assertEqual(dividir(r"'a\nb'"), [r"a\nb"])

    def test_comentarios(self):
        self.assertEqual(dividir("a b # resto", comentarios=True), ["a", "b"])
        self.assertEqual(dividir("a#b", comentarios=True), ["a#b"])
        self.assertEqual(dividir("a #b"), ["a", "#b"])

    def test_confere_com_stdlib(self):
        for linha in ["git commit -m 'msg com espaço' --amend", 'x "a\\"b" c\\ d', "a 'b\"c' \"d'e\""]:
            with self.subTest(linha=linha):
                self.assertEqual(dividir(linha), shlex.split(linha))

    def test_citar_e_juntar(self):
        args = ["echo", "it's", "a b", "", "$HOME", "ok-1.txt"]
        self.assertEqual(dividir(juntar(args)), args)
        self.assertEqual(citar("simples"), "simples")
        self.assertEqual(citar("a b"), "'a b'")

    def test_malformadas(self):
        for ruim in ["echo 'aberta", 'echo "aberta', "echo abc\\", 'echo "abc\\']:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroShlex):
                    dividir(ruim)


if __name__ == "__main__":
    unittest.main()
