import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_validacao import (
    Invalido, Valido, aplicar, erro, sequence, traverse, unit,
    valida_cadastro, valida_idade,
)


class TestValidacao(unittest.TestCase):
    def test_acumula_todos_os_erros(self):
        r = valida_cadastro("  ", 200, "xx")
        self.assertEqual(
            r, Invalido(("nome vazio", "idade fora do intervalo", "email inválido"))
        )

    def test_cadastro_valido(self):
        r = valida_cadastro(" Ana ", 30, "a@b.com")
        self.assertEqual(r, Valido({"nome": "Ana", "idade": 30, "email": "a@b.com"}))

    def test_erro_parcial(self):
        self.assertEqual(valida_cadastro("Ana", 30, "x"), erro("email inválido"))
        self.assertEqual(valida_idade(True), erro("idade deve ser inteira"))
        self.assertEqual(valida_idade(0), Valido(0))
        self.assertEqual(valida_idade(150), Valido(150))
        self.assertEqual(valida_idade(-1), erro("idade fora do intervalo"))

    def test_leis_applicative(self):
        for v in (Valido(3), erro("e")):
            self.assertEqual(unit(lambda x: x).ap(v), v)  # identidade
        f = lambda x: x + 1
        self.assertEqual(unit(f).ap(unit(2)), unit(f(2)))  # homomorfismo
        u = erro("u")
        self.assertEqual(u.ap(unit(1)), u)
        # interchange: u <*> pure y == pure ($ y) <*> u
        for u in (unit(f), erro("u")):
            self.assertEqual(u.ap(unit(5)), unit(lambda g: g(5)).ap(u))

    def test_composicao_applicative(self):
        compor = lambda g: lambda h: lambda x: g(h(x))
        u, v, w = unit(lambda x: x + 1), unit(lambda x: x * 2), unit(4)
        self.assertEqual(
            unit(compor).ap(u).ap(v).ap(w).valor, u.ap(v.ap(w)).valor
        )
        u2, v2, w2 = erro("a"), erro("b"), erro("c")
        self.assertEqual(
            unit(compor).ap(u2).ap(v2).ap(w2), u2.ap(v2.ap(w2))
        )

    def test_functor(self):
        self.assertEqual(Valido(1).map(lambda x: x + 1), Valido(2))
        self.assertEqual(erro("a").map(lambda x: x + 1), erro("a"))

    def test_sequence_traverse_aplicar(self):
        self.assertEqual(sequence([Valido(1), Valido(2)]), Valido([1, 2]))
        self.assertEqual(sequence([erro("a"), Valido(1), erro("b")]), erro("a", "b"))
        self.assertEqual(sequence([]), Valido([]))
        self.assertEqual(traverse(valida_idade, [1, -1, 999]),
                         erro("idade fora do intervalo", "idade fora do intervalo"))
        self.assertEqual(aplicar(lambda: 7), Valido(7))
        self.assertEqual(Valido(1).entao(lambda x: erro("k")), erro("k"))
        self.assertEqual(erro("a").entao(lambda x: Valido(x)), erro("a"))


if __name__ == "__main__":
    unittest.main()
