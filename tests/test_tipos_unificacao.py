import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_unificacao import (BOOL, INT, ErroUnificacao, TCon, TVar, aplicar,
                              compor, lista, mostrar, par, seta, unificar,
                              unificar_todos)

a, b, c = TVar("a"), TVar("b"), TVar("c")


class TestUnificacao(unittest.TestCase):
    def test_iguais(self):
        self.assertEqual(unificar(INT, INT), {})

    def test_variavel_com_tipo(self):
        self.assertEqual(unificar(a, INT), {"a": INT})
        self.assertEqual(unificar(INT, a), {"a": INT})

    def test_variavel_com_ela_mesma(self):
        self.assertEqual(unificar(a, a), {})

    def test_conflito_de_construtores(self):
        with self.assertRaises(ErroUnificacao):
            unificar(INT, BOOL)

    def test_aridade_diferente(self):
        with self.assertRaises(ErroUnificacao):
            unificar(TCon("F", (INT,)), TCon("F", (INT, INT)))

    def test_occurs_check(self):
        with self.assertRaises(ErroUnificacao):
            unificar(a, seta(a, INT))
        with self.assertRaises(ErroUnificacao):
            unificar(lista(a), a)

    def test_estrutural(self):
        s = unificar(seta(a, b), seta(INT, lista(a)))
        self.assertEqual(aplicar(s, a), INT)
        self.assertEqual(aplicar(s, b), lista(INT))

    def test_encadeado_resolve_tudo(self):
        # a -> b -> c  ~  b -> c -> Int  =>  tudo Int
        s = unificar(seta(a, seta(b, c)), seta(b, seta(c, INT)))
        for v in (a, b, c):
            self.assertEqual(aplicar(s, v), INT)

    def test_mais_geral(self):
        s = unificar(seta(a, b), seta(b, c))
        t1 = aplicar(s, seta(a, b))
        t2 = aplicar(s, seta(b, c))
        self.assertEqual(t1, t2)
        self.assertEqual(len({aplicar(s, v) for v in (a, b, c)}), 1)

    def test_estende_substituicao_existente(self):
        s = unificar(a, INT)
        s = unificar(b, lista(a), s)
        self.assertEqual(aplicar(s, b), lista(INT))

    def test_conflito_com_substituicao_existente(self):
        s = unificar(a, INT)
        with self.assertRaises(ErroUnificacao):
            unificar(a, BOOL, s)

    def test_nao_modifica_entrada(self):
        s = {"a": INT}
        unificar(b, BOOL, s)
        self.assertEqual(s, {"a": INT})

    def test_unificar_todos(self):
        s = unificar_todos([(a, par(b, INT)), (b, BOOL)])
        self.assertEqual(aplicar(s, a), par(BOOL, INT))

    def test_compor(self):
        s1 = {"a": seta(b, INT)}
        s2 = {"b": BOOL}
        s = compor(s2, s1)
        self.assertEqual(aplicar(s, a), seta(BOOL, INT))
        self.assertEqual(aplicar(s, b), BOOL)

    def test_mostrar(self):
        self.assertEqual(mostrar(seta(seta(a, b), INT)), "('a -> 'b) -> Int")
        self.assertEqual(mostrar(seta(INT, seta(INT, INT))), "Int -> Int -> Int")
        self.assertEqual(mostrar(lista(par(INT, a))), "List<(Int * 'a)>")


if __name__ == "__main__":
    unittest.main()
