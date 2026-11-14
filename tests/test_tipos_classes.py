import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_classes import (ErroClasse, Sistema, mconcat, ordenar,
                           sistema_padrao)
from tipos_unificacao import BOOL, INT, TCon, TVar, lista, par

STR = TCon("Str")
S = sistema_padrao()


class TestClasses(unittest.TestCase):
    def test_show_base(self):
        self.assertEqual(S.resolver("Show", INT)["mostrar"](42), "42")
        self.assertEqual(S.resolver("Show", BOOL)["mostrar"](True), "verdadeiro")

    def test_show_lista_usa_contexto(self):
        d = S.resolver("Show", lista(INT))
        self.assertEqual(d["mostrar"]([1, 2, 3]), "[1, 2, 3]")
        d = S.resolver("Show", lista(lista(BOOL)))
        self.assertEqual(d["mostrar"]([[True], []]), "[[verdadeiro], []]")

    def test_show_par(self):
        d = S.resolver("Show", par(INT, lista(STR)))
        self.assertEqual(d["mostrar"]((1, ["a"])), "(1, ['a'])")

    def test_sem_instancia(self):
        with self.assertRaises(ErroClasse):
            S.resolver("Show", TCon("Fantasma"))
        # contexto não satisfeito: Show (List Fantasma)
        with self.assertRaises(ErroClasse):
            S.resolver("Show", lista(TCon("Fantasma")))

    def test_tipo_ambiguo(self):
        with self.assertRaises(ErroClasse):
            S.resolver("Show", TVar("a"))

    def test_classe_desconhecida(self):
        with self.assertRaises(ErroClasse):
            S.resolver("Nada", INT)

    def test_metodo_padrao(self):
        d = S.resolver("Eq", INT)
        self.assertTrue(d["diferente"](1, 2))
        self.assertFalse(d["diferente"](2, 2))

    def test_metodo_padrao_com_contexto(self):
        d = S.resolver("Eq", lista(INT))
        self.assertTrue(d["igual"]([1, 2], [1, 2]))
        self.assertTrue(d["diferente"]([1], [1, 2]))

    def test_superclasse_acessivel(self):
        d = S.resolver("Ord", INT)
        self.assertTrue(d["igual"](3, 3))        # veio de Eq
        self.assertTrue(d["menor"](2, 3))        # padrão usa menor_igual e igual
        self.assertFalse(d["menor"](3, 3))
        self.assertIn("Eq", d.supers)

    def test_metodo_inexistente(self):
        with self.assertRaises(KeyError):
            S.resolver("Show", INT)["inexistente"]

    def test_ordenar_com_dicionario(self):
        self.assertEqual(ordenar(S.resolver("Ord", INT), [3, 1, 2]), [1, 2, 3])
        self.assertEqual(ordenar(S.resolver("Ord", STR), ["b", "a", "c"]), ["a", "b", "c"])

    def test_ordenar_listas_lexicografico(self):
        d = S.resolver("Ord", lista(INT))
        r = ordenar(d, [[2], [1, 5], [1], []])
        self.assertEqual(r, [[], [1], [1, 5], [2]])

    def test_ordenar_pares(self):
        d = S.resolver("Ord", par(INT, STR))
        r = ordenar(d, [(2, "a"), (1, "z"), (1, "b")])
        self.assertEqual(r, [(1, "b"), (1, "z"), (2, "a")])

    def test_ordenar_e_estavel(self):
        d = S.resolver("Ord", par(INT, INT))
        self.assertEqual(ordenar(d, [(1, 2), (1, 1)]), [(1, 1), (1, 2)])

    def test_monoid(self):
        self.assertEqual(mconcat(S.resolver("Monoid", INT), [1, 2, 3]), 6)
        self.assertEqual(mconcat(S.resolver("Monoid", STR), ["a", "b"]), "ab")
        self.assertEqual(mconcat(S.resolver("Monoid", lista(INT)), [[1], [2, 3]]), [1, 2, 3])
        self.assertEqual(mconcat(S.resolver("Monoid", INT), []), 0)

    def test_ord_exige_eq_da_superclasse(self):
        s = Sistema()
        s.classe("Eq", ("igual",))
        s.classe("Ord", ("le",), supers=("Eq",))
        s.instancia("Ord", "T", lambda: {"le": lambda a, b: a <= b})
        with self.assertRaises(ErroClasse):  # falta instância Eq T
            s.resolver("Ord", TCon("T"))
        s.instancia("Eq", "T", lambda: {"igual": lambda a, b: a == b})
        self.assertEqual(s.resolver("Ord", TCon("T"))["igual"](1, 1), True)

    def test_declaracoes_invalidas(self):
        s = Sistema()
        s.classe("C", ("m",))
        with self.assertRaises(ErroClasse):
            s.classe("C", ("m",))
        with self.assertRaises(ErroClasse):
            s.classe("D", ("m",), supers=("Z",))
        with self.assertRaises(ErroClasse):
            s.classe("E", ("m",), padroes={"x": lambda d: None})
        s.instancia("C", "T", lambda: {"m": 1})
        with self.assertRaises(ErroClasse):
            s.instancia("C", "T", lambda: {"m": 2})
        with self.assertRaises(ErroClasse):
            s.instancia("Z", "T", lambda: {})

    def test_instancia_incompleta_ou_com_extra(self):
        s = Sistema()
        s.classe("C", ("a", "b"))
        s.instancia("C", "Falta", lambda: {"a": 1})
        s.instancia("C", "Sobra", lambda: {"a": 1, "b": 2, "c": 3})
        with self.assertRaises(ErroClasse):
            s.resolver("C", TCon("Falta"))
        with self.assertRaises(ErroClasse):
            s.resolver("C", TCon("Sobra"))

    def test_aridade_do_tipo(self):
        with self.assertRaises(ErroClasse):
            S.resolver("Show", TCon("List"))  # List sem argumento


if __name__ == "__main__":
    unittest.main()
