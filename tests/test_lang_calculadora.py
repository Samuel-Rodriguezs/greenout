import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_calculadora import Calculadora, ErroCalculadora, calcular


class TestCalculadora(unittest.TestCase):
    def test_precedencia(self):
        self.assertEqual(calcular("2 + 3 * 4"), 14)
        self.assertEqual(calcular("(2 + 3) * 4"), 20)
        self.assertEqual(calcular("10 - 4 - 3"), 3)
        self.assertEqual(calcular("7 % 4"), 3)

    def test_potencia_associativa_a_direita_e_unario(self):
        self.assertEqual(calcular("2 ^ 3 ^ 2"), 512)
        self.assertEqual(calcular("-2 ^ 2"), -4)
        self.assertEqual(calcular("2 ^ -1"), 0.5)
        self.assertEqual(calcular("--3"), 3)

    def test_variaveis(self):
        c = Calculadora()
        self.assertEqual(c.avaliar("x = 5"), 5)
        self.assertEqual(c.avaliar("y = x * 2"), 10)
        self.assertEqual(c.avaliar("x + y"), 15)

    def test_funcoes_nativas_e_constantes(self):
        c = Calculadora()
        self.assertEqual(c.avaliar("sqrt(16) + max(1, 7, 3)"), 11)
        self.assertAlmostEqual(c.avaliar("sin(pi / 2)"), 1.0)
        self.assertAlmostEqual(c.avaliar("e"), math.e)

    def test_funcao_definida(self):
        c = Calculadora()
        self.assertIsNone(c.avaliar("hip(a, b) = sqrt(a^2 + b^2)"))
        self.assertEqual(c.avaliar("hip(3, 4)"), 5)
        c.avaliar("k = 10")
        c.avaliar("g(x) = x + k")
        self.assertEqual(c.avaliar("g(1)"), 11)

    def test_funcao_recursiva_limitada(self):
        c = Calculadora()
        c.avaliar("f(x) = f(x)")
        with self.assertRaises(ErroCalculadora):
            c.avaliar("f(1)")

    def test_erros(self):
        c = Calculadora()
        invalidos = ["1 / 0", "2 +", "(1 + 2", "1 2", "z", "foo(1)", "1 $ 2", "", "sqrt(-1)",
                     "3 = 4", "pi = 3", "f(a, a) = a", "g(1,) = 1", "x =", "sqrt(1, 2)", ")"]
        for linha in invalidos:
            with self.assertRaises(ErroCalculadora, msg=linha):
                c.avaliar(linha)

    def test_aridade_de_funcao_definida(self):
        c = Calculadora()
        c.avaliar("dobro(x) = x * 2")
        with self.assertRaises(ErroCalculadora):
            c.avaliar("dobro(1, 2)")


if __name__ == "__main__":
    unittest.main()
