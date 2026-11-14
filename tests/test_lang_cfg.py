import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_cfg import ErroGramatica, Gramatica

ANBN = "S -> 'a' S 'b' | eps"
PALINDROMOS = "S -> a S a | b S b | a | b | eps"
EXPR = """
E -> E + T | T
T -> T * F | F
F -> ( E ) | 'x' | 'y'
"""


class TestCFG(unittest.TestCase):
    def test_an_bn(self):
        g = Gramatica(ANBN)
        for p in ["", "ab", "aabb", "aaabbb"]:
            self.assertTrue(g.reconhece(p), p)
        for p in ["a", "ba", "aab", "abab", "abb"]:
            self.assertFalse(g.reconhece(p), p)

    def test_palindromos(self):
        g = Gramatica(PALINDROMOS)
        for p in ["", "a", "aba", "abba", "babab"]:
            self.assertTrue(g.reconhece(p), p)
        for p in ["ab", "abab", "aab"]:
            self.assertFalse(g.reconhece(p), p)

    def test_expressoes(self):
        g = Gramatica(EXPR)
        for p in ["x", "x+y", "x*y+x", "(x+y)*x", "((x))"]:
            self.assertTrue(g.reconhece(p), p)
        for p in ["", "+", "x+", "(x", "xy", "x**y"]:
            self.assertFalse(g.reconhece(p), p)

    def test_producao_unitaria_e_anulavel_no_meio(self):
        g = Gramatica("S -> A B C\nA -> 'a' | eps\nB -> 'b'\nC -> 'c' | A")
        validas = {"b", "ab", "bc", "ba", "abc", "aba"}
        for p in validas | {"", "a", "c", "abca", "bb", "cb"}:
            self.assertEqual(g.reconhece(p), p in validas, p)

    def test_comentarios(self):
        g = Gramatica("# gramática\nS -> 'a' S | 'a' # fim")
        self.assertTrue(g.reconhece("aaa"))
        self.assertFalse(g.reconhece(""))

    def test_erros(self):
        for txt in ["", "S 'a'", "s -> a", "S -> A", "S -> ", "S -> abc", "S -> a |"]:
            with self.assertRaises(ErroGramatica, msg=txt):
                Gramatica(txt)


if __name__ == "__main__":
    unittest.main()
