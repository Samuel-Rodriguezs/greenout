import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_hm import (EApp, ELam, ELet, ELit, ESe, EVar, Esquema, app,
                      esquema_de, generalizar, inferir, lam)
from tipos_stlc import ErroTipo
from tipos_unificacao import BOOL, INT, TVar, mostrar, par, seta

x, y, f = EVar("x"), EVar("y"), EVar("f")


def tipo(e):
    return mostrar(inferir(e))


class TestHM(unittest.TestCase):
    def test_literais(self):
        self.assertEqual(inferir(ELit(1)), INT)
        self.assertEqual(inferir(ELit(False)), BOOL)

    def test_identidade(self):
        self.assertEqual(tipo(lam("x", x)), "'a -> 'a")

    def test_k_e_s(self):
        self.assertEqual(tipo(lam("x y", x)), "'a -> 'b -> 'a")
        s = lam("x y z", app(x, EVar("z"), app(y, EVar("z"))))
        self.assertEqual(tipo(s), "('a -> 'b -> 'c) -> ('a -> 'b) -> 'a -> 'c")

    def test_dobro(self):
        self.assertEqual(tipo(lam("f x", app(f, app(f, x)))), "('a -> 'a) -> 'a -> 'a")

    def test_let_polimorfismo(self):
        e = ELet("id", lam("x", x),
                 app(EVar("par"), app(EVar("id"), ELit(1)), app(EVar("id"), ELit(True))))
        self.assertEqual(inferir(e), par(INT, BOOL))

    def test_lambda_nao_e_polimorfico(self):
        e = lam("id", app(EVar("par"), app(EVar("id"), ELit(1)), app(EVar("id"), ELit(True))))
        with self.assertRaises(ErroTipo):
            inferir(e)

    def test_nao_generaliza_variavel_do_ambiente(self):
        # \y. let g = \x. par x y in par (g 1) (g True)
        e = lam("y", ELet("g", lam("x", app(EVar("par"), x, y)),
                          app(EVar("par"), app(EVar("g"), ELit(1)),
                              app(EVar("g"), ELit(True)))))
        self.assertEqual(tipo(e), "'a -> ((Int * 'a) * (Bool * 'a))")

    def test_nao_generaliza_variavel_ligada_por_lambda_externa(self):
        # \y. let g = \x. y in (g 1) usa y no mesmo tipo; g True : mesmo 'a
        e = lam("y", ELet("g", lam("x", y), app(EVar("g"), ELit(1))))
        self.assertEqual(tipo(e), "'a -> 'a")

    def test_autoaplicacao_falha(self):
        with self.assertRaises(ErroTipo):
            inferir(lam("x", app(x, x)))

    def test_let_com_autoaplicacao_polimorfica_ok(self):
        # let id = \x.x in id id : a -> a
        e = ELet("id", lam("x", x), app(EVar("id"), EVar("id")))
        self.assertEqual(tipo(e), "'a -> 'a")

    def test_se(self):
        e = lam("c", ESe(EVar("c"), ELit(1), ELit(2)))
        self.assertEqual(inferir(e), seta(BOOL, INT))
        with self.assertRaises(ErroTipo):
            inferir(ESe(ELit(1), ELit(1), ELit(2)))
        with self.assertRaises(ErroTipo):
            inferir(ESe(ELit(True), ELit(1), ELit(False)))

    def test_variavel_nao_ligada(self):
        with self.assertRaises(ErroTipo):
            inferir(EVar("zzz"))

    def test_fst_snd(self):
        self.assertEqual(tipo(app(EVar("fst"), app(EVar("par"), ELit(1), ELit(True)))), "Int")
        self.assertEqual(tipo(lam("p", app(EVar("snd"), EVar("p")))), "('a * 'b) -> 'b")

    def test_fix_fatorial(self):
        corpo = lam("f n", ESe(app(EVar("=="), EVar("n"), ELit(0)), ELit(1),
                               app(EVar("+"), EVar("n"), app(f, app(EVar("+"), EVar("n"), ELit(-1))))))
        self.assertEqual(inferir(app(EVar("fix"), corpo)), seta(INT, INT))

    def test_ambiente_customizado(self):
        env = {"n": Esquema((), INT)}
        self.assertEqual(inferir(lam("x", EVar("n")), env), seta(TVar("a"), INT))

    def test_generalizar(self):
        env = {"z": Esquema((), TVar("q"))}
        s = generalizar(env, seta(TVar("q"), TVar("r")))
        self.assertEqual(s.vars, ("r",))

    def test_esquema_de(self):
        s = esquema_de(lam("x", x))
        self.assertEqual(s.vars, ("a",))

    def test_aninhamento_de_lets(self):
        e = ELet("k", lam("a b", EVar("a")),
                 ELet("u", app(EVar("k"), ELit(1)),
                      app(EVar("par"), app(EVar("u"), ELit(True)), app(EVar("u"), EVar("k")))))
        self.assertEqual(inferir(e), par(INT, INT))


if __name__ == "__main__":
    unittest.main()
