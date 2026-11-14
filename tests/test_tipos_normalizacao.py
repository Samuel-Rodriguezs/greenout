import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_normalizacao import (Normalizacao, canonico, mult_tipada, normalizar,
                                numeral, reducoes, soma_tipada, substituir,
                                tipo_numeral)
from tipos_stlc import App, ErroTipo, Lam, Lit, Se, Var, verificar
from tipos_unificacao import BOOL, INT, seta


def aplicar(f, *args):
    for a in args:
        f = App(f, a)
    return f


class TestNormalizacao(unittest.TestCase):
    def test_numerais_tipados(self):
        self.assertEqual(verificar(numeral(3)), tipo_numeral())
        self.assertEqual(verificar(soma_tipada()), seta(tipo_numeral(), seta(tipo_numeral(), tipo_numeral())))

    def test_soma(self):
        t = aplicar(soma_tipada(), numeral(2), numeral(3))
        nf, passos = normalizar(t)
        self.assertEqual(canonico(nf), canonico(numeral(5)))
        self.assertGreater(passos, 0)

    def test_produto(self):
        t = aplicar(mult_tipada(), numeral(3), numeral(4))
        nf, _ = normalizar(t)
        self.assertEqual(canonico(nf), canonico(numeral(12)))

    def test_recusa_mal_tipado(self):
        omega = Lam("x", seta(INT, INT), App(Var("x"), Var("x")))
        with self.assertRaises(ErroTipo):
            normalizar(App(omega, omega))
        with self.assertRaises(ErroTipo):
            Normalizacao(App(Lit(1), Lit(2)))

    def test_condicional(self):
        t = Se(Lit(True), App(Lam("x", INT, Var("x")), Lit(7)), Lit(0))
        nf, passos = normalizar(t)
        self.assertEqual(nf, Lit(7))
        self.assertEqual(passos, 2)

    def test_subst_sem_captura(self):
        # (\y:Int. x)[x := y] precisa renomear y
        r = substituir(Lam("y", INT, Var("x")), "x", Var("y"))
        self.assertEqual(canonico(r), canonico(Lam("z", INT, Var("y"))))
        self.assertNotEqual(canonico(r), canonico(Lam("y", INT, Var("y"))))

    def test_canonico_alfa(self):
        a = Lam("x", INT, Lam("y", INT, Var("x")))
        b = Lam("p", INT, Lam("q", INT, Var("p")))
        self.assertEqual(canonico(a), canonico(b))
        self.assertNotEqual(canonico(a), canonico(Lam("x", INT, Lam("y", INT, Var("y")))))

    def test_reducoes_lista_todos_os_redexes(self):
        ident = Lam("x", INT, Var("x"))
        # (id 1) aplicado em contexto com dois redexes independentes
        t = Se(Lit(True), App(ident, Lit(1)), App(ident, Lit(2)))
        self.assertEqual(len(reducoes(t)), 3)  # if-true + dois betas

    def test_forma_normal_unica_confluencia(self):
        t = aplicar(soma_tipada(), numeral(1), aplicar(soma_tipada(), numeral(1), numeral(1)))
        n = Normalizacao(t)
        formas = n.formas_normais()
        self.assertEqual(len(formas), 1)
        self.assertEqual(next(iter(formas)), canonico(numeral(3)))

    def test_todas_as_sequencias_terminam_e_longest_ge_shortest(self):
        t = aplicar(mult_tipada(), numeral(2), numeral(2))
        n = Normalizacao(t)
        self.assertGreaterEqual(n.sequencia_mais_longa(), n.sequencia_mais_curta())
        self.assertGreater(n.sequencia_mais_curta(), 0)

    def test_ordens_diferentes_mesmos_resultados_comprimentos_diferentes(self):
        # Duplicar um argumento redex: (\x:Int. if True then x else x) ((\y:Int.y) 1)
        ident = Lam("y", INT, Var("y"))
        t = App(Lam("x", INT, Se(Lit(True), Var("x"), Var("x"))), App(ident, Lit(1)))
        n = Normalizacao(t)
        self.assertEqual(n.formas_normais(), frozenset({Lit(1)}))
        self.assertLess(n.sequencia_mais_curta(), n.sequencia_mais_longa())

    def test_preservacao_de_tipo(self):
        t = aplicar(soma_tipada(), numeral(2), numeral(1))
        self.assertTrue(Normalizacao(t).preserva_tipo())
        self.assertEqual(Normalizacao(t).tipo, tipo_numeral())

    def test_termo_ja_normal(self):
        n = Normalizacao(numeral(2))
        self.assertEqual(n.sequencia_mais_longa(), 0)
        self.assertEqual(n.sequencia_mais_curta(), 0)
        nf, passos = normalizar(numeral(2))
        self.assertEqual((nf, passos), (numeral(2), 0))

    def test_ordem_superior_com_contexto(self):
        ctx = {"g": seta(INT, INT)}
        t = App(Lam("h", seta(INT, INT), App(Var("h"), Lit(1))), Var("g"))
        nf, _ = normalizar(t, ctx)
        self.assertEqual(nf, App(Var("g"), Lit(1)))

    def test_bool_ordem_superior(self):
        # twice not true = true
        nao = Lam("b", BOOL, Se(Var("b"), Lit(False), Lit(True)))
        twice = Lam("f", seta(BOOL, BOOL), Lam("b", BOOL, App(Var("f"), App(Var("f"), Var("b")))))
        nf, _ = normalizar(aplicar(twice, nao, Lit(True)))
        self.assertEqual(nf, Lit(True))


if __name__ == "__main__":
    unittest.main()
