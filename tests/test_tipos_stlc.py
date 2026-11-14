import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_stlc import (App, ErroTipo, Lam, Lit, Se, Var, e_fechado_e_monomorfo,
                        inferir, verificar)
from tipos_unificacao import BOOL, INT, TVar, mostrar, seta

a, b, c = TVar("a"), TVar("b"), TVar("c")


class TestVerificar(unittest.TestCase):
    def test_literais(self):
        self.assertEqual(verificar(Lit(3)), INT)
        self.assertEqual(verificar(Lit(True)), BOOL)

    def test_identidade_anotada(self):
        self.assertEqual(verificar(Lam("x", INT, Var("x"))), seta(INT, INT))

    def test_aplicacao(self):
        t = App(Lam("x", INT, Var("x")), Lit(1))
        self.assertEqual(verificar(t), INT)

    def test_argumento_errado(self):
        with self.assertRaises(ErroTipo):
            verificar(App(Lam("x", INT, Var("x")), Lit(True)))

    def test_aplicar_nao_funcao(self):
        with self.assertRaises(ErroTipo):
            verificar(App(Lit(1), Lit(2)))

    def test_variavel_livre(self):
        with self.assertRaises(ErroTipo):
            verificar(Var("x"))
        self.assertEqual(verificar(Var("x"), {"x": INT}), INT)

    def test_sem_anotacao(self):
        with self.assertRaises(ErroTipo):
            verificar(Lam("x", None, Var("x")))

    def test_se(self):
        self.assertEqual(verificar(Se(Lit(True), Lit(1), Lit(2))), INT)
        with self.assertRaises(ErroTipo):
            verificar(Se(Lit(1), Lit(1), Lit(2)))
        with self.assertRaises(ErroTipo):
            verificar(Se(Lit(True), Lit(1), Lit(False)))

    def test_ordem_superior(self):
        # \f:Int->Int. \x:Int. f (f x)
        dobra = Lam("f", seta(INT, INT), Lam("x", INT, App(Var("f"), App(Var("f"), Var("x")))))
        self.assertEqual(verificar(dobra), seta(seta(INT, INT), seta(INT, INT)))

    def test_sombreamento(self):
        t = Lam("x", INT, Lam("x", BOOL, Var("x")))
        self.assertEqual(verificar(t), seta(INT, seta(BOOL, BOOL)))


class TestInferir(unittest.TestCase):
    def test_identidade(self):
        self.assertEqual(inferir(Lam("x", None, Var("x"))), seta(a, a))

    def test_k(self):
        self.assertEqual(inferir(Lam("x", None, Lam("y", None, Var("x")))),
                         seta(a, seta(b, a)))

    def test_s(self):
        s = Lam("x", None, Lam("y", None, Lam("z", None,
                App(App(Var("x"), Var("z")), App(Var("y"), Var("z"))))))
        self.assertEqual(mostrar(inferir(s)),
                         "('a -> 'b -> 'c) -> ('a -> 'b) -> 'a -> 'c")

    def test_composicao(self):
        comp = Lam("f", None, Lam("g", None, Lam("x", None,
                   App(Var("f"), App(Var("g"), Var("x"))))))
        self.assertEqual(mostrar(inferir(comp)),
                         "('a -> 'b) -> ('c -> 'a) -> 'c -> 'b")

    def test_autoaplicacao_falha_occurs_check(self):
        with self.assertRaises(ErroTipo):
            inferir(Lam("x", None, App(Var("x"), Var("x"))))

    def test_omega_nao_tem_tipo(self):
        w = Lam("x", None, App(Var("x"), Var("x")))
        with self.assertRaises(ErroTipo):
            inferir(App(w, w))

    def test_usa_contexto(self):
        ctx = {"+": seta(INT, seta(INT, INT))}
        t = Lam("x", None, App(App(Var("+"), Var("x")), Lit(1)))
        self.assertEqual(inferir(t, ctx), seta(INT, INT))

    def test_restricao_via_se(self):
        t = Lam("c", None, Lam("x", None, Se(Var("c"), Var("x"), Lit(0))))
        self.assertEqual(inferir(t), seta(BOOL, seta(INT, INT)))

    def test_conflito(self):
        t = Lam("x", None, Se(Var("x"), Var("x"), Lit(0)))
        with self.assertRaises(ErroTipo):
            inferir(t)

    def test_nao_polimorfico_em_let_via_lambda(self):
        # (\id. (id 1, id True)) nao tipa sem let-polimorfismo: simula com se
        t = Lam("id", None, Se(App(Var("id"), Lit(True)), App(Var("id"), Lit(1)), Lit(0)))
        # id : Bool -> Bool e id : Int -> Bool  => conflito
        with self.assertRaises(ErroTipo):
            inferir(t)

    def test_anotacao_respeitada(self):
        t = Lam("x", INT, Var("x"))
        self.assertEqual(inferir(t), seta(INT, INT))
        self.assertTrue(e_fechado_e_monomorfo(inferir(t)))
        self.assertFalse(e_fechado_e_monomorfo(inferir(Lam("x", None, Var("x")))))


if __name__ == "__main__":
    unittest.main()
