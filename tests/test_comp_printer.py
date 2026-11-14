import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_ast import Binario, Num, Unario
from comp_parser import parse, parse_expressao
from comp_printer import dump, formatar, formatar_expr

PROGRAMA = """
func fat(n: int) -> int { if (n <= 1) { return 1; } return n * fat(n - 1); }
func ola() { print(1); }
var x = 3;  var y: bool = !(x > 2) || false;
while (x > 0) { x = x - 1; if (x == 1) { print(x); } else if (x == 2) { ola(); } else { { } } }
print(fat(5) % 3);
"""


class TestPrinter(unittest.TestCase):
    def test_roundtrip_programa(self):
        ast = parse(PROGRAMA)
        self.assertEqual(parse(formatar(ast)), ast)

    def test_formatacao_estavel(self):
        saida = formatar(parse(PROGRAMA))
        self.assertEqual(formatar(parse(saida)), saida)

    def test_formato_exato(self):
        fonte = "func f(a: int,b: bool)->int{if(b){return a;}else{return 0;}}"
        esperado = (
            "func f(a: int, b: bool) -> int {\n"
            "    if (b) {\n        return a;\n    } else {\n        return 0;\n    }\n"
            "}\n")
        self.assertEqual(formatar(parse(fonte)), esperado)

    def test_else_if_encadeado(self):
        s = formatar(parse("if (a) {} else if (b) {} else {}"))
        self.assertEqual(s, "if (a) {} else if (b) {} else {}\n")

    def test_parenteses_minimos(self):
        self.assertEqual(formatar_expr(parse_expressao("(1 + 2) * 3")), "(1 + 2) * 3")
        self.assertEqual(formatar_expr(parse_expressao("(1 * 2) + 3")), "1 * 2 + 3")
        self.assertEqual(formatar_expr(parse_expressao("1 - (2 - 3)")), "1 - (2 - 3)")
        self.assertEqual(formatar_expr(parse_expressao("(1 - 2) - 3")), "1 - 2 - 3")
        self.assertEqual(formatar_expr(parse_expressao("-(a + b)")), "-(a + b)")
        self.assertEqual(formatar_expr(parse_expressao("!(a && b)")), "!(a && b)")

    def test_numero_negativo_gerado_por_otimizador(self):
        e = Unario("-", Num(-3))
        self.assertEqual(formatar_expr(e), "-(-3)")
        self.assertEqual(parse_expressao(formatar_expr(Binario("-", Num(1), Num(-2)))),
                         Binario("-", Num(1), Unario("-", Num(2))))

    def test_vazio(self):
        self.assertEqual(formatar(parse("")), "")

    def test_dump(self):
        d = dump(parse("var x = 1 + 2;"))
        self.assertEqual(d.splitlines(), [
            "Programa", "  Var(nome='x')", "    Binario(op='+')",
            "      Num(valor=1)", "      Num(valor=2)"])


if __name__ == "__main__":
    unittest.main()
