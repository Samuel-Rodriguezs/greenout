import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_ast import Binario, Bool, Chamada, Nome, Num
from comp_folding import (aplicar_binario, aplicar_unario, dividir,
                          dobrar_constantes, literal, resto, valor_de)
from comp_parser import parse, parse_expressao


def dobra(expr):
    return dobrar_constantes(parse_expressao(expr))


class TestSemanticaOperadores(unittest.TestCase):
    def test_divisao_trunca_para_zero(self):
        self.assertEqual(dividir(7, 2), 3)
        self.assertEqual(dividir(-7, 2), -3)
        self.assertEqual(dividir(7, -2), -3)
        self.assertEqual(dividir(-7, -2), 3)

    def test_resto_com_sinal_do_dividendo(self):
        self.assertEqual(resto(7, 3), 1)
        self.assertEqual(resto(-7, 3), -1)
        self.assertEqual(resto(7, -3), 1)
        for a in range(-9, 10):
            for b in (-4, -3, 2, 5):
                self.assertEqual(a, dividir(a, b) * b + resto(a, b))

    def test_divisao_por_zero(self):
        with self.assertRaises(ZeroDivisionError):
            dividir(1, 0)
        with self.assertRaises(ZeroDivisionError):
            aplicar_binario("%", 1, 0)

    def test_operadores(self):
        self.assertIs(aplicar_binario("<=", 2, 2), True)
        self.assertIs(aplicar_binario("&&", True, False), False)
        self.assertIs(aplicar_binario("==", True, True), True)
        self.assertEqual(aplicar_unario("-", 5), -5)
        self.assertIs(aplicar_unario("!", False), True)

    def test_literal_e_valor(self):
        self.assertEqual(literal(True), Bool(True))
        self.assertEqual(literal(0), Num(0))
        self.assertIs(valor_de(Bool(False)), False)
        self.assertIsNone(valor_de(Nome("x")))


class TestFolding(unittest.TestCase):
    def test_aritmetica(self):
        self.assertEqual(dobra("1 + 2 * 3"), Num(7))
        self.assertEqual(dobra("(10 - 4) / 2 % 2"), Num(1))
        self.assertEqual(dobra("-(3 + 4)"), Num(-7))

    def test_booleanos(self):
        self.assertEqual(dobra("1 < 2 && 3 == 3"), Bool(True))
        self.assertEqual(dobra("!(1 > 2) || false"), Bool(True))

    def test_parcial(self):
        self.assertEqual(dobra("x + 2 * 3"), Binario("+", Nome("x"), Num(6)))
        self.assertEqual(dobra("(1 + 2) * x"), Binario("*", Num(3), Nome("x")))

    def test_nao_dobra_divisao_por_zero(self):
        self.assertEqual(dobra("1 / 0"), Binario("/", Num(1), Num(0)))
        self.assertEqual(dobra("2 + 4 % (1 - 1)"),
                         Binario("+", Num(2), Binario("%", Num(4), Num(0))))

    def test_curto_circuito(self):
        self.assertEqual(dobra("false && f()"), Bool(False))
        self.assertEqual(dobra("true || f()"), Bool(True))
        self.assertEqual(dobra("true && x"), Nome("x"))
        self.assertEqual(dobra("false || x"), Nome("x"))
        self.assertEqual(dobra("f() && false"), Binario("&&", Chamada("f", []), Bool(False)))

    def test_dobra_dentro_de_comandos(self):
        p = dobrar_constantes(parse("var x = 2 * 3; if (1 < 2) { print(4 / 2); }"))
        self.assertEqual(p, parse("var x = 6; if (true) { print(2); }"))

    def test_nao_altera_original(self):
        p = parse("var x = 1 + 1;")
        dobrar_constantes(p)
        self.assertEqual(p, parse("var x = 1 + 1;"))

    def test_posicao_do_resultado(self):
        r = dobrar_constantes(parse("var x = 1 +\n 2;"))
        self.assertEqual(r.itens[0].init.pos, (1, 11))


if __name__ == "__main__":
    unittest.main()
