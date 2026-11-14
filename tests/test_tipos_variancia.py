import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_variancia import (TA, TB, TP, Var, combinar, compor, declarar, fn,
                             inferir_variancias, inverter, mostrar, subtipo,
                             tabela_padrao, variancia_em)

GATO, ANIMAL, INT = TB("Gato"), TB("Animal"), TB("Int")
BASES = {("Gato", "Animal")}
T = tabela_padrao()
a = TP("a")


def sub(x, y):
    return subtipo(x, y, T, BASES)


class TestVariancia(unittest.TestCase):
    def test_algebra(self):
        self.assertEqual(inverter(Var.CO), Var.CONTRA)
        self.assertEqual(inverter(Var.INV), Var.INV)
        self.assertEqual(compor(Var.CONTRA, Var.CONTRA), Var.CO)
        self.assertEqual(compor(Var.CONTRA, Var.CO), Var.CONTRA)
        self.assertEqual(compor(Var.INV, Var.CO), Var.INV)
        self.assertEqual(compor(Var.BI, Var.INV), Var.BI)
        self.assertEqual(combinar(Var.CO, Var.CONTRA), Var.INV)
        self.assertEqual(combinar(Var.BI, Var.CONTRA), Var.CONTRA)
        self.assertEqual(combinar(Var.CO, Var.CO), Var.CO)

    def test_lista_covariante(self):
        self.assertTrue(sub(TA("Lista", (GATO,)), TA("Lista", (ANIMAL,))))
        self.assertFalse(sub(TA("Lista", (ANIMAL,)), TA("Lista", (GATO,))))

    def test_escritor_contravariante(self):
        self.assertTrue(sub(TA("Escritor", (ANIMAL,)), TA("Escritor", (GATO,))))
        self.assertFalse(sub(TA("Escritor", (GATO,)), TA("Escritor", (ANIMAL,))))

    def test_ref_invariante(self):
        self.assertFalse(sub(TA("Ref", (GATO,)), TA("Ref", (ANIMAL,))))
        self.assertFalse(sub(TA("Ref", (ANIMAL,)), TA("Ref", (GATO,))))
        self.assertTrue(sub(TA("Ref", (GATO,)), TA("Ref", (GATO,))))

    def test_constante_bivariante(self):
        self.assertTrue(sub(TA("Constante", (GATO,)), TA("Constante", (INT,))))

    def test_funcao(self):
        self.assertTrue(sub(fn(ANIMAL, GATO), fn(GATO, ANIMAL)))
        self.assertFalse(sub(fn(GATO, GATO), fn(ANIMAL, GATO)))
        self.assertFalse(sub(fn(ANIMAL, ANIMAL), fn(ANIMAL, GATO)))

    def test_funcao_ordem_superior_dupla_contravariancia(self):
        # (Animal -> Int) -> Int  e  (Gato -> Int) -> Int : o parâmetro aparece
        # em posição contra-contra = covariante
        f = fn(fn(ANIMAL, INT), INT)
        g = fn(fn(GATO, INT), INT)
        self.assertTrue(sub(f, g) is False and sub(g, f) is True)

    def test_variancia_em_posicoes(self):
        self.assertEqual(variancia_em(fn(a, INT), "a", T), Var.CONTRA)
        self.assertEqual(variancia_em(fn(INT, a), "a", T), Var.CO)
        self.assertEqual(variancia_em(fn(fn(a, INT), INT), "a", T), Var.CO)
        self.assertEqual(variancia_em(fn(a, a), "a", T), Var.INV)
        self.assertEqual(variancia_em(TA("Ref", (a,)), "a", T), Var.INV)
        self.assertEqual(variancia_em(fn(INT, INT), "a", T), Var.BI)
        self.assertEqual(variancia_em(TA("Lista", (fn(INT, a),)), "a", T), Var.CO)
        self.assertEqual(variancia_em(TA("Escritor", (fn(a, INT),)), "a", T), Var.CO)

    def test_inferir_varios(self):
        corpo = fn(TP("x"), TA("Par", (TP("y"), TP("y"))))
        self.assertEqual(inferir_variancias(("x", "y", "z"), corpo, T),
                         (Var.CONTRA, Var.CO, Var.BI))

    def test_declarar_infere(self):
        t = tabela_padrao()
        # Produtor[a] = () -> a  ;  Consumidor[a] = a -> ()
        self.assertEqual(declarar(t, "Produtor", ("a",), fn(TB("U"), a)), (Var.CO,))
        self.assertEqual(declarar(t, "Consumidor", ("a",), fn(a, TB("U"))), (Var.CONTRA,))
        self.assertTrue(subtipo(TA("Produtor", (GATO,)), TA("Produtor", (ANIMAL,)), t, BASES))
        self.assertTrue(subtipo(TA("Consumidor", (ANIMAL,)), TA("Consumidor", (GATO,)), t, BASES))

    def test_declarar_anotacao_valida_e_invalida(self):
        t = tabela_padrao()
        declarar(t, "P", ("a",), fn(TB("U"), a), (Var.CO,))
        declarar(t, "Q", ("a",), fn(a, TB("U")), (Var.INV,))  # invariante é sempre seguro
        declarar(t, "F", ("a",), TB("U"), (Var.CO,))           # bivariante cabe em covariante
        with self.assertRaises(TypeError):
            declarar(t, "R", ("a",), fn(a, TB("U")), (Var.CO,))
        with self.assertRaises(TypeError):
            declarar(t, "S", ("a",), fn(TB("U"), a), (Var.CONTRA,))
        with self.assertRaises(TypeError):
            declarar(t, "V", ("a",), fn(a, a), (Var.CO,))
        with self.assertRaises(TypeError):
            declarar(t, "W", ("a",), fn(TB("U"), a), (Var.BI,))
        self.assertNotIn("R", t)

    def test_declarar_recursivo_depende_de_tabela(self):
        t = tabela_padrao()
        declarar(t, "Caixa", ("a",), TA("Lista", (a,)))
        self.assertEqual(t["Caixa"], (Var.CO,))
        declarar(t, "Caixa2", ("a",), fn(TA("Caixa", (a,)), TB("U")))
        self.assertEqual(t["Caixa2"], (Var.CONTRA,))

    def test_erros(self):
        with self.assertRaises(KeyError):
            variancia_em(TA("Desconhecido", (a,)), "a", T)
        with self.assertRaises(ValueError):
            variancia_em(TA("Lista", (a, a)), "a", T)
        with self.assertRaises(ValueError):
            declarar(tabela_padrao(), "X", ("a",), a, ())

    def test_construtores_diferentes(self):
        self.assertFalse(sub(TA("Lista", (GATO,)), TA("Par", (GATO, GATO))))
        self.assertFalse(sub(GATO, TA("Lista", (GATO,))))

    def test_mostrar(self):
        self.assertEqual(mostrar(fn(fn(a, INT), TA("Lista", (a,)))), "(a -> Int) -> Lista[a]")


if __name__ == "__main__":
    unittest.main()
