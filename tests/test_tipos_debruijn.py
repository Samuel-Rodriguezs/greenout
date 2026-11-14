import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_beta import normalizar as normalizar_nomes
from tipos_church import de_int
from tipos_debruijn import (Ap, Idx, Lam, beta, de_debruijn, desloca,
                            mostrar, normalizar, para_debruijn, substituir)
from tipos_termos import alfa_equivalentes, analisar


class TestDeBruijn(unittest.TestCase):
    def test_identidade_e_constante(self):
        self.assertEqual(para_debruijn(analisar("\\x.x")), Lam(Idx(0)))
        self.assertEqual(para_debruijn(analisar("\\x y.x")), Lam(Lam(Idx(1))))

    def test_combinador_s(self):
        t = para_debruijn(analisar("\\x y z.x z (y z)"))
        self.assertEqual(mostrar(t), "λ λ λ 2 0 (1 0)")

    def test_alfa_equivalencia_vira_igualdade(self):
        a = para_debruijn(analisar("\\x.\\y.x y"))
        b = para_debruijn(analisar("\\p.\\q.p q"))
        self.assertEqual(a, b)

    def test_sombreamento(self):
        self.assertEqual(para_debruijn(analisar("\\x.\\x.x")), Lam(Lam(Idx(0))))

    def test_livres_usam_contexto(self):
        t = analisar("\\x.x y z")
        d = para_debruijn(t, ("y", "z"))
        self.assertEqual(d, Lam(Ap(Ap(Idx(0), Idx(1)), Idx(2))))

    def test_livre_fora_do_contexto(self):
        with self.assertRaises(ValueError):
            para_debruijn(analisar("\\x.y"), ("z",))

    def test_roundtrip_alfa(self):
        for s in ["\\x y.x", "\\f.(\\x.f (x x)) (\\x.f (x x))", "\\a.\\a.a"]:
            t = analisar(s)
            self.assertTrue(alfa_equivalentes(de_debruijn(para_debruijn(t)), t))

    def test_roundtrip_com_livres(self):
        t = analisar("\\x.x y")
        r = de_debruijn(para_debruijn(t, ("y",)), ("y",))
        self.assertTrue(alfa_equivalentes(r, t))

    def test_desloca(self):
        self.assertEqual(desloca(2, 0, Lam(Ap(Idx(0), Idx(1)))),
                         Lam(Ap(Idx(0), Idx(3))))
        with self.assertRaises(ValueError):
            desloca(-1, 0, Idx(0))

    def test_substituir_sob_binder_desloca(self):
        # (λ 1)[0 := 5] = λ 6
        self.assertEqual(substituir(0, Idx(5), Lam(Idx(1))), Lam(Idx(6)))

    def test_beta_sem_captura(self):
        # (λ λ 1) 0  ->  λ 1   (a livre 0 passa a ser 1 sob o novo binder)
        self.assertEqual(beta(Lam(Idx(1)), Idx(0)), Lam(Idx(1)))

    def test_normalizacao_concorda_com_nomes(self):
        t = analisar("(\\m n f x.m f (n f x)) (\\f x.f x) (\\f x.f (f x))")
        pelo_nome = para_debruijn(normalizar_nomes(t))
        self.assertEqual(normalizar(para_debruijn(t)), pelo_nome)
        self.assertEqual(pelo_nome, para_debruijn(de_int(3)))

    def test_captura_classica(self):
        t = analisar("(\\x y.x) y")
        d = normalizar(para_debruijn(t, ("y",)), 100)
        self.assertEqual(d, Lam(Idx(1)))  # λ. y, com y livre = índice 1 sob o binder


if __name__ == "__main__":
    unittest.main()
