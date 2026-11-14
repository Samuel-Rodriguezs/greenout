import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_beta import (LimiteExcedido, contar_passos, e_forma_normal,
                        normalizar, passo_aplicativo, passo_normal)
from tipos_termos import alfa_equivalentes, analisar

OMEGA = "(\\x.x x) (\\x.x x)"


class TestBeta(unittest.TestCase):
    def igual(self, a, b):
        self.assertTrue(alfa_equivalentes(a, analisar(b)), (a, b))

    def test_identidade(self):
        self.igual(normalizar(analisar("(\\x.x) y")), "y")

    def test_forma_normal(self):
        self.assertTrue(e_forma_normal(analisar("\\x.x y")))
        self.assertFalse(e_forma_normal(analisar("\\x.(\\y.y) x")))

    def test_reduz_sob_lambda(self):
        self.igual(normalizar(analisar("\\x.(\\y.y) x")), "\\x.x")

    def test_omega_diverge(self):
        t = analisar(OMEGA)
        self.assertEqual(passo_normal(t), t)
        with self.assertRaises(LimiteExcedido):
            normalizar(t, limite=50)

    def test_normal_termina_onde_aplicativa_diverge(self):
        t = analisar(f"(\\x y.y) ({OMEGA})")
        self.igual(normalizar(t, "normal"), "\\y.y")
        with self.assertRaises(LimiteExcedido):
            normalizar(t, "aplicativa", limite=100)

    def test_aplicativa_reduz_argumento_primeiro(self):
        t = analisar("(\\x.x x) ((\\y.y) z)")
        self.igual(passo_aplicativo(t), "(\\x.x x) z")
        self.igual(passo_normal(t), "((\\y.y) z) ((\\y.y) z)")

    def test_contagem_de_passos_difere(self):
        t = analisar("(\\x.x x) ((\\y.y) z)")
        self.assertEqual(contar_passos(t, "aplicativa"), 2)
        self.assertEqual(contar_passos(t, "normal"), 3)

    def test_sem_captura(self):
        # (\x.\y.x) y  ->  \z.y  (e nunca \y.y)
        r = normalizar(analisar("(\\x y.x) y"))
        self.igual(r, "\\z.y")

    def test_estrategia_invalida(self):
        with self.assertRaises(ValueError):
            normalizar(analisar("x"), "preguicosa")

    def test_confluencia_em_termo_terminante(self):
        t = analisar("(\\f x.f (f x)) (\\y.y) a")
        self.igual(normalizar(t, "normal"), "a")
        self.igual(normalizar(t, "aplicativa"), "a")


if __name__ == "__main__":
    unittest.main()
