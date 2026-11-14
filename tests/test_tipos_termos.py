import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_termos import (Abs, App, Var, alfa_equivalentes, analisar, livres,
                          mostrar, substituir)


class TestTermos(unittest.TestCase):
    def test_livres(self):
        self.assertEqual(livres(analisar("\\x.x y")), {"y"})
        self.assertEqual(livres(analisar("(\\x.x) x")), {"x"})
        self.assertEqual(livres(analisar("\\x y.x y")), frozenset())

    def test_subst_simples(self):
        r = substituir(analisar("x y"), "x", Var("z"))
        self.assertEqual(r, analisar("z y"))

    def test_subst_variavel_ligada_nao_muda(self):
        t = analisar("\\x.x")
        self.assertEqual(substituir(t, "x", Var("y")), t)

    def test_subst_evita_captura(self):
        r = substituir(analisar("\\y.x"), "x", Var("y"))
        self.assertTrue(alfa_equivalentes(r, analisar("\\z.y")))
        self.assertFalse(alfa_equivalentes(r, analisar("\\y.y")))
        self.assertEqual(livres(r), {"y"})

    def test_subst_sem_renomear_quando_desnecessario(self):
        r = substituir(analisar("\\y.y"), "x", Var("y"))
        self.assertEqual(r, analisar("\\y.y"))

    def test_alfa(self):
        self.assertTrue(alfa_equivalentes(analisar("\\x.x"), analisar("\\y.y")))
        self.assertTrue(alfa_equivalentes(analisar("\\x y.x"), analisar("\\a b.a")))
        self.assertFalse(alfa_equivalentes(analisar("\\x y.x"), analisar("\\x y.y")))
        self.assertFalse(alfa_equivalentes(analisar("\\x.y"), analisar("\\x.z")))
        self.assertTrue(alfa_equivalentes(analisar("\\x.y"), analisar("\\z.y")))

    def test_alfa_sombreamento(self):
        self.assertTrue(alfa_equivalentes(analisar("\\x.\\x.x"), analisar("\\a.\\b.b")))
        self.assertFalse(alfa_equivalentes(analisar("\\x.\\x.x"), analisar("\\a.\\b.a")))

    def test_alfa_livre_vs_ligada(self):
        self.assertFalse(alfa_equivalentes(analisar("\\x.x"), analisar("\\y.x")))

    def test_parse_associatividade(self):
        self.assertEqual(analisar("a b c"), App(App(Var("a"), Var("b")), Var("c")))
        self.assertEqual(analisar("\\x y.x"), Abs("x", Abs("y", Var("x"))))
        self.assertEqual(analisar("λx.x"), Abs("x", Var("x")))

    def test_parse_abstracao_estende_a_direita(self):
        self.assertEqual(analisar("\\x.x y"), Abs("x", App(Var("x"), Var("y"))))
        self.assertEqual(analisar("a \\x.x"), App(Var("a"), Abs("x", Var("x"))))

    def test_mostrar_roundtrip(self):
        for s in ["\\x.x", "(\\x.x x) (\\x.x x)", "a (b c)", "\\f.\\x.f (f x)"]:
            t = analisar(s)
            self.assertEqual(analisar(mostrar(t)), t)

    def test_erros(self):
        for s in ["(x", "x)", "\\.x", "\\x x", "", "x $"]:
            with self.assertRaises(ValueError):
                analisar(s)


if __name__ == "__main__":
    unittest.main()
