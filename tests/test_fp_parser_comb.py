import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_parser_comb import (
    ErroParse, calcular, char, digito, entre, executar, falha, fim, inteiro,
    item, lista_de_inteiros, many, many1, numero, opcional, sat, sep_by,
    sep_by1, simbolo, string, unit,
)

ENTRADAS = ["", "a", "abc", "123", "1+2"]


def igual(p, q):
    return all(p.parse(s) == q.parse(s) for s in ENTRADAS)


class TestParserBasico(unittest.TestCase):
    def test_primitivas(self):
        self.assertEqual(item().parse("ab"), ("a", "b"))
        self.assertIsNone(item().parse(""))
        self.assertEqual(char("a").parse("abc"), ("a", "bc"))
        self.assertIsNone(char("a").parse("xbc"))
        self.assertEqual(string("ab").parse("abc"), ("ab", "c"))
        self.assertIsNone(string("ab").parse("a"))
        self.assertEqual(digito().parse("7x"), ("7", "x"))
        self.assertEqual(unit(5).parse("z"), (5, "z"))
        self.assertIsNone(falha().parse("z"))
        self.assertEqual(fim().parse(""), (None, ""))
        self.assertIsNone(fim().parse("x"))

    def test_leis_monad(self):
        f = lambda c: char(c).map(str.upper) | unit("?")
        g = lambda c: sat(lambda x: x.isdigit()).map(lambda d: c + d)
        self.assertTrue(igual(unit("a").bind(f), f("a")))
        m = item()
        self.assertTrue(igual(m.bind(unit), m))
        self.assertTrue(igual(m.bind(f).bind(g), m.bind(lambda x: f(x).bind(g))))

    def test_leis_functor_e_alternativa(self):
        m = many1(digito())
        self.assertTrue(igual(m.map(lambda x: x), m))
        self.assertTrue(igual(falha() | m, m))
        self.assertTrue(igual(m | falha(), m))
        self.assertTrue(igual((m | char("a")) | item(), m | (char("a") | item())))

    def test_ap(self):
        p = unit(lambda a: lambda b: a + b).ap(item()).ap(item())
        self.assertEqual(p.parse("xyz"), ("xy", "z"))

    def test_alternativa_retrocede(self):
        p = string("ab") | string("a")
        self.assertEqual(p.parse("ac"), ("a", "c"))
        q = (string("a") >> string("b")) | string("ac")
        self.assertEqual(q.parse("ac"), ("ac", ""))

    def test_many_many1(self):
        self.assertEqual(many(digito()).parse("12a"), (["1", "2"], "a"))
        self.assertEqual(many(digito()).parse("a"), ([], "a"))
        self.assertIsNone(many1(digito()).parse("a"))
        self.assertEqual(many(unit(1)).parse("abc")[1], "abc")  # sem laço infinito

    def test_opcional_sep_by_entre(self):
        self.assertEqual(opcional(char("-"), "+").parse("5"), ("+", "5"))
        v = sep_by(digito(), char(","))
        self.assertEqual(v.parse("1,2,3x"), (["1", "2", "3"], "x"))
        self.assertEqual(v.parse("x"), ([], "x"))
        self.assertIsNone(sep_by1(digito(), char(",")).parse("x"))
        self.assertEqual(sep_by(digito(), char(",")).parse("1,"), (["1"], ","))
        self.assertEqual(entre(char("("), digito(), char(")")).parse("(7)!"), ("7", "!"))
        self.assertIsNone(entre(char("("), digito(), char(")")).parse("(7"))

    def test_inteiros(self):
        self.assertEqual(inteiro().parse("-42a"), (-42, "a"))
        self.assertEqual(numero().parse("12   +"), (12, "+"))
        self.assertIsNone(inteiro().parse("-"))
        self.assertEqual(simbolo("+").parse("+  1"), ("+", "1"))


class TestExpressoes(unittest.TestCase):
    def test_precedencia_e_associatividade(self):
        self.assertEqual(calcular("1 + 2 * 3"), 7)
        self.assertEqual(calcular("(1 + 2) * 3"), 9)
        self.assertEqual(calcular("10 - 4 - 3"), 3)  # à esquerda
        self.assertEqual(calcular("100 / 5 / 2"), 10)
        self.assertEqual(calcular("  ((2))  "), 2)
        self.assertEqual(calcular("-3 + 5"), 2)
        self.assertEqual(calcular("2 * (3 + 4) - 5 * (2 - 1)"), 9)

    def test_erros(self):
        for ruim in ("", "1 +", "(1", "1 2", "abc", "1 + * 2", ")"):
            with self.assertRaises(ErroParse, msg=ruim):
                calcular(ruim)
        with self.assertRaises(ZeroDivisionError):
            calcular("1 / 0")

    def test_lista_de_inteiros(self):
        self.assertEqual(executar(lista_de_inteiros(), "[1, 2 ,-3]"), [1, 2, -3])
        self.assertEqual(executar(lista_de_inteiros(), "[]"), [])
        with self.assertRaises(ErroParse):
            executar(lista_de_inteiros(), "[1,]")

    def test_aninhamento_profundo(self):
        n = 100
        self.assertEqual(calcular("(" * n + "7" + ")" * n), 7)


if __name__ == "__main__":
    unittest.main()
