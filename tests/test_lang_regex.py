import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_regex import ErroRegex, compilar


class TestRegex(unittest.TestCase):
    def test_literal_e_ponto(self):
        self.assertTrue(compilar("a.c").fullmatch("abc"))
        self.assertFalse(compilar("a.c").fullmatch("ac"))

    def test_quantificadores(self):
        r = compilar("ab*c")
        for s, ok in [("ac", True), ("abbbc", True), ("abd", False)]:
            self.assertEqual(r.fullmatch(s), ok, s)
        self.assertFalse(compilar("ab+c").fullmatch("ac"))
        self.assertTrue(compilar("colou?r").fullmatch("color"))
        self.assertTrue(compilar("colou?r").fullmatch("colour"))

    def test_classes(self):
        self.assertTrue(compilar("[a-c]+").fullmatch("abcabc"))
        self.assertFalse(compilar("[a-c]+").fullmatch("abd"))
        self.assertTrue(compilar("[^0-9]+").fullmatch("abc"))
        self.assertFalse(compilar("[^0-9]+").fullmatch("a1"))
        self.assertTrue(compilar(r"\d+\.\d+").fullmatch("3.14"))

    def test_alternancia_e_grupos(self):
        r = compilar("(ab|cd)+e")
        self.assertTrue(r.fullmatch("abcdabe"))
        self.assertFalse(r.fullmatch("abce"))
        self.assertTrue(compilar("gato|cao").fullmatch("cao"))

    def test_backtracking(self):
        self.assertTrue(compilar("a*a*a*b").fullmatch("aaaab"))
        self.assertTrue(compilar(".*abc").fullmatch("xxabcabc"))
        self.assertEqual(compilar("a*ab").match("aaab").texto, "aaab")

    def test_gulosidade(self):
        self.assertEqual(compilar("a+").match("aaab").texto, "aaa")
        self.assertEqual(compilar("<.*>").match("<a><b>").texto, "<a><b>")

    def test_ancoras_e_search(self):
        self.assertIsNotNone(compilar("^abc").match("abcd"))
        self.assertIsNone(compilar("^abc").search("xabc"))
        self.assertEqual(compilar("c$").search("abcabc").inicio, 5)
        m = compilar(r"\d+").search("id: 4521;")
        self.assertEqual((m.inicio, m.texto), (4, "4521"))

    def test_findall(self):
        self.assertEqual(compilar(r"\w+").findall("oi, mundo 42"), ["oi", "mundo", "42"])
        self.assertEqual(compilar("a*").findall("baa"), ["", "aa", ""])

    def test_repeticao_de_vazio_nao_trava(self):
        self.assertTrue(compilar("(a*)*b").fullmatch("aab"))
        self.assertFalse(compilar("(a*)*b").fullmatch("aac"))

    def test_concordancia_com_re(self):
        padroes = ["a(b|c)*d", "[a-z]+[0-9]?", "x.*y", "(ab)+|c?"]
        textos = ["abcbd", "abc1", "xaay", "abab", "", "c", "zz"]
        for p in padroes:
            for t in textos:
                self.assertEqual(compilar(p).fullmatch(t), re.fullmatch(p, t) is not None, (p, t))

    def test_erros(self):
        for p in ["*a", "(ab", "a)", "[abc", "a\\", "[z-a]", "a|+"]:
            with self.assertRaises(ErroRegex, msg=p):
                compilar(p)


if __name__ == "__main__":
    unittest.main()
