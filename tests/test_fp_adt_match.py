import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_adt_match import (
    Mul, Num, Pot, Soma, Var, avaliar, classificar, derivar, mostrar,
    simplificar, variaveis,
)

X = Var("x")
Y = Var("y")


class TestAdtMatch(unittest.TestCase):
    def test_avaliar(self):
        e = Soma(Mul(Num(3), X), Pot(Y, 2))
        self.assertEqual(avaliar(e, {"x": 2, "y": 4}), 22)
        with self.assertRaises(KeyError):
            avaliar(e, {"x": 1})
        with self.assertRaises(TypeError):
            avaliar("lixo", {})

    def test_imutabilidade_e_igualdade(self):
        with self.assertRaises(Exception):
            X.nome = "z"
        self.assertEqual(Soma(Num(1), X), Soma(Num(1), Var("x")))
        self.assertEqual(hash(Mul(X, Y)), hash(Mul(Var("x"), Var("y"))))

    def test_simplificar_regras(self):
        self.assertEqual(simplificar(Soma(Num(0), X)), X)
        self.assertEqual(simplificar(Soma(X, Num(0))), X)
        self.assertEqual(simplificar(Mul(Num(1), X)), X)
        self.assertEqual(simplificar(Mul(X, Num(0))), Num(0))
        self.assertEqual(simplificar(Pot(X, 0)), Num(1))
        self.assertEqual(simplificar(Pot(X, 1)), X)
        self.assertEqual(simplificar(Pot(Num(2), 10)), Num(1024))
        self.assertEqual(simplificar(Soma(Num(2), Num(3))), Num(5))
        self.assertEqual(simplificar(Mul(Num(2), Num(3))), Num(6))

    def test_simplificar_ate_ponto_fixo(self):
        e = Soma(Mul(Num(1), Soma(X, Num(0))), Mul(Num(0), Y))
        self.assertEqual(simplificar(e), X)
        self.assertEqual(simplificar(simplificar(e)), simplificar(e))

    def test_derivadas(self):
        self.assertEqual(simplificar(derivar(Pot(X, 3), "x")), Mul(Num(3), Pot(X, 2)))
        self.assertEqual(simplificar(derivar(Mul(X, X), "x")), Soma(X, X))
        self.assertEqual(simplificar(derivar(Soma(Mul(Num(5), X), Num(7)), "x")), Num(5))
        self.assertEqual(simplificar(derivar(Y, "x")), Num(0))

    def test_derivada_numerica_confere(self):
        e = Soma(Pot(X, 3), Mul(Num(2), Pot(X, 2)))
        d = derivar(e, "x")
        h = 1e-6
        for x in (-2.0, 0.5, 3.0):
            numerica = (avaliar(e, {"x": x + h}) - avaliar(e, {"x": x - h})) / (2 * h)
            self.assertAlmostEqual(avaliar(d, {"x": x}), numerica, places=3)
            self.assertAlmostEqual(avaliar(simplificar(d), {"x": x}), avaliar(d, {"x": x}))

    def test_mostrar_precedencia(self):
        self.assertEqual(mostrar(Mul(Soma(X, Num(1)), Y)), "(x + 1) * y")
        self.assertEqual(mostrar(Soma(Mul(X, Y), Num(2.5))), "x * y + 2.5")
        self.assertEqual(mostrar(Pot(Soma(X, Num(1)), 2)), "(x + 1)^2")
        self.assertEqual(mostrar(Num(4.0)), "4")

    def test_variaveis(self):
        self.assertEqual(variaveis(Soma(Mul(X, Y), Pot(X, 2))), frozenset({"x", "y"}))
        self.assertEqual(variaveis(Num(1)), frozenset())

    def test_classificar(self):
        casos = {
            None: "nada", True: "booleano", -3: "inteiro negativo", 0: "zero",
            0.0: "zero", 7: "número positivo", 2.5: "número positivo",
            "": "texto vazio", "a": "texto", (): "sequência vazia",
        }
        for valor, esperado in casos.items():
            self.assertEqual(classificar(valor), esperado, valor)
        self.assertEqual(classificar([5]), "unitária de número positivo")
        self.assertEqual(classificar([1, 2, 3]), "sequência de 1 a 3")
        self.assertEqual(classificar({"tipo": "u", "a": 1, "b": 2}), "registro u com 2 campos")
        self.assertEqual(classificar({"a": 1}), "mapa")
        self.assertEqual(classificar(Num(1)), "átomo")
        self.assertEqual(classificar(object()), "desconhecido")


if __name__ == "__main__":
    unittest.main()
