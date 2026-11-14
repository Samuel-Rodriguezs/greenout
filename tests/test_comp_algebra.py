import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_algebra import simplificar
from comp_gerador import gerar
from comp_parser import parse, parse_expressao
from comp_printer import formatar_expr
from comp_vm import executar


def simp(expr):
    return formatar_expr(simplificar(parse_expressao(expr)))


def roda(programa):
    return executar(gerar(programa)).saida


class TestAlgebra(unittest.TestCase):
    def test_elementos_neutros(self):
        self.assertEqual(simp("x + 0"), "x")
        self.assertEqual(simp("0 + x"), "x")
        self.assertEqual(simp("x - 0"), "x")
        self.assertEqual(simp("x * 1"), "x")
        self.assertEqual(simp("1 * x"), "x")
        self.assertEqual(simp("x / 1"), "x")

    def test_zero_a_esquerda_da_subtracao(self):
        self.assertEqual(simp("0 - x"), "-x")

    def test_absorvente_so_com_operando_puro(self):
        self.assertEqual(simp("x * 0"), "0")
        self.assertEqual(simp("0 * (a + b)"), "0")
        self.assertEqual(simp("f(1) * 0"), "f(1) * 0")
        self.assertEqual(simp("x % 1"), "0")
        self.assertEqual(simp("f() % 1"), "f() % 1")

    def test_x_menos_x(self):
        self.assertEqual(simp("a * b - a * b"), "0")
        self.assertEqual(simp("f() - f()"), "f() - f()")

    def test_comparacoes_reflexivas(self):
        self.assertEqual(simp("a + 1 == a + 1"), "true")
        self.assertEqual(simp("a <= a"), "true")
        self.assertEqual(simp("a < a"), "false")
        self.assertEqual(simp("a != a"), "false")
        self.assertEqual(simp("f() == f()"), "f() == f()")

    def test_logicos(self):
        self.assertEqual(simp("x && true"), "x")
        self.assertEqual(simp("true && x"), "x")
        self.assertEqual(simp("x || false"), "x")
        self.assertEqual(simp("false || x"), "x")
        self.assertEqual(simp("a && false"), "false")
        self.assertEqual(simp("a || true"), "true")
        self.assertEqual(simp("f() && false"), "f() && false")
        self.assertEqual(simp("p && p"), "p")

    def test_dupla_negacao(self):
        self.assertEqual(simp("!!p"), "p")
        self.assertEqual(simp("- -x"), "x")
        self.assertEqual(simp("!!!p"), "!p")

    def test_negacao_de_relacional(self):
        self.assertEqual(simp("!(a < b)"), "a >= b")
        self.assertEqual(simp("!(a >= b)"), "a < b")

    def test_efeito_cascata(self):
        self.assertEqual(simp("(x + 0) * (1 + 0) - 0"), "x")
        self.assertEqual(simp("(a - a) + b"), "b")

    def test_nao_toca_o_que_nao_conhece(self):
        self.assertEqual(simp("a + b * 2"), "a + b * 2")

    def test_simplifica_dentro_de_comandos(self):
        p = simplificar(parse("var x = 5; print(x * 1 + 0); if (!(x < 3)) { x = x + 0; }"))
        self.assertEqual(p, parse("var x = 5; print(x); if (x >= 3) { x = x; }"))

    def test_preserva_comportamento(self):
        fonte = """
        func g(n: int) -> int { print(n); return n; }
        var a = 7; var b = 3;
        print(a * 1 + 0 - 0); print(0 - a); print(a - a); print(!(a < b)); print(!!(a == b));
        print(g(2) * 1); print(a / 1 % 1); print(b == b && true);
        print(g(1) < g(1) || false);
        """
        original = parse(fonte)
        self.assertEqual(roda(simplificar(original)), roda(original))


if __name__ == "__main__":
    unittest.main()
