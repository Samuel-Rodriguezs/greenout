import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_algebricos import ErroTipo, PCon, PCoringa, PLit, PVar, universo_padrao
from tipos_exaustividade import (contra_exemplo, exaustivo, mostrar_padrao,
                                 redundantes)

U = universo_padrao()
W = PCoringa()
NIL = PCon("Nil")


def cons(a, b):
    return PCon("Cons", (a, b))


def mostra(ps):
    r = contra_exemplo(ps, U)
    return None if r is None else mostrar_padrao(r)


class TestExaustividade(unittest.TestCase):
    def test_coringa_cobre_tudo(self):
        self.assertTrue(exaustivo([W], U))
        self.assertTrue(exaustivo([PVar("x")], U))

    def test_vazio_nao_e_exaustivo(self):
        self.assertFalse(exaustivo([], U))

    def test_lista_completa(self):
        self.assertTrue(exaustivo([NIL, cons(W, W)], U))

    def test_lista_incompleta(self):
        self.assertEqual(mostra([NIL]), "Cons(_, _)")
        self.assertEqual(mostra([cons(W, W)]), "Nil")

    def test_aninhado_falta_caso(self):
        ps = [NIL, cons(W, NIL)]
        self.assertEqual(mostra(ps), "Cons(_, Cons(_, _))")

    def test_aninhado_completo(self):
        ps = [NIL, cons(W, NIL), cons(W, cons(W, W))]
        self.assertTrue(exaustivo(ps, U))

    def test_opcao(self):
        self.assertTrue(exaustivo([PCon("Nada"), PCon("Algum", (W,))], U))
        self.assertEqual(mostra([PCon("Algum", (W,))]), "Nada")

    def test_opcao_de_opcao(self):
        ps = [PCon("Nada"), PCon("Algum", (PCon("Nada"),))]
        self.assertEqual(mostra(ps), "Algum(Algum(_))")

    def test_booleanos(self):
        self.assertTrue(exaustivo([PLit(True), PLit(False)], U))
        self.assertEqual(mostra([PLit(True)]), "False")
        self.assertEqual(mostra([PLit(False)]), "True")

    def test_inteiros_nunca_se_esgotam(self):
        self.assertFalse(exaustivo([PLit(0), PLit(1), PLit(2)], U))
        self.assertEqual(mostra([PLit(0), PLit(1)]), "2")
        self.assertTrue(exaustivo([PLit(0), PVar("n")], U))

    def test_par_de_booleanos(self):
        def p(a, b):
            return PCon("MkPar", (PLit(a), PLit(b)))
        todos = [p(True, True), p(True, False), p(False, True), p(False, False)]
        self.assertTrue(exaustivo(todos, U))
        self.assertEqual(mostra(todos[:3]), "MkPar(False, False)")

    def test_par_coringa_misto(self):
        ps = [PCon("MkPar", (PLit(True), W)), PCon("MkPar", (W, PLit(True)))]
        self.assertEqual(mostra(ps), "MkPar(False, False)")

    def test_soma(self):
        self.assertTrue(exaustivo([PCon("Esq", (W,)), PCon("Dir", (W,))], U))
        self.assertEqual(mostra([PCon("Esq", (W,))]), "Dir(_)")

    def test_redundancia(self):
        self.assertEqual(redundantes([NIL, cons(W, W), W], U), [2])
        self.assertEqual(redundantes([W, NIL], U), [1])
        self.assertEqual(redundantes([NIL, NIL], U), [1])
        self.assertEqual(redundantes([cons(W, W), cons(W, NIL), NIL], U), [1])

    def test_sem_redundancia(self):
        self.assertEqual(redundantes([cons(W, NIL), cons(W, W), NIL], U), [])

    def test_redundancia_com_literais(self):
        self.assertEqual(redundantes([PLit(1), PLit(2), PLit(1), W], U), [2])
        self.assertEqual(redundantes([PLit(True), PLit(False), W], U), [2])

    def test_aridade_invalida(self):
        with self.assertRaises(ErroTipo):
            exaustivo([PCon("Cons", (W,)), NIL], U)


if __name__ == "__main__":
    unittest.main()
