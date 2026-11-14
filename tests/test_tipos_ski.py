import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_beta import LimiteExcedido
from tipos_church import de_int
from tipos_ski import (I, K, S, Ap, Atomo, aplicar, de_lambda, mostrar,
                       normalizar, tamanho)
from tipos_termos import analisar

x, y, z, f = Atomo("x"), Atomo("y"), Atomo("z"), Atomo("f")


class TestSKI(unittest.TestCase):
    def test_regras_basicas(self):
        self.assertEqual(normalizar(aplicar(I, x)), x)
        self.assertEqual(normalizar(aplicar(K, x, y)), x)
        self.assertEqual(normalizar(aplicar(S, x, y, z)), aplicar(x, z, Ap(y, z)))

    def test_s_k_k_e_identidade(self):
        self.assertEqual(normalizar(aplicar(S, K, K, x)), x)

    def test_aplicacao_parcial_nao_reduz(self):
        self.assertEqual(normalizar(aplicar(K, x)), aplicar(K, x))
        self.assertEqual(normalizar(aplicar(S, x, y)), aplicar(S, x, y))

    def test_reduz_em_argumentos(self):
        self.assertEqual(normalizar(aplicar(x, aplicar(I, y))), aplicar(x, y))

    def test_traducao_identidade(self):
        t = de_lambda(analisar("\\a.a"))
        self.assertEqual(t, I)

    def test_traducao_constante(self):
        self.assertEqual(de_lambda(analisar("\\a.b")), aplicar(K, Atomo("b")))

    def test_traducao_k(self):
        t = de_lambda(analisar("\\a b.a"))
        self.assertEqual(normalizar(aplicar(t, x, y)), x)

    def test_traducao_troca(self):
        t = de_lambda(analisar("\\a b.b a"))
        self.assertEqual(normalizar(aplicar(t, x, f)), aplicar(f, x))

    def test_traducao_preserva_semantica_de_composicao(self):
        comp = de_lambda(analisar("\\f g x.f (g x)"))
        r = normalizar(aplicar(comp, Atomo("p"), Atomo("q"), x))
        self.assertEqual(r, aplicar(Atomo("p"), Ap(Atomo("q"), x)))

    def test_numeral_de_church_em_ski(self):
        dois = de_lambda(de_int(2))
        self.assertEqual(normalizar(aplicar(dois, f, x)), Ap(f, Ap(f, x)))
        zero = de_lambda(de_int(0))
        self.assertEqual(normalizar(aplicar(zero, f, x)), x)

    def test_soma_em_ski(self):
        soma = de_lambda(analisar("\\m n f x.m f (n f x)"))
        r = normalizar(aplicar(soma, de_lambda(de_int(2)), de_lambda(de_int(3)), f, x))
        esperado = x
        for _ in range(5):
            esperado = Ap(f, esperado)
        self.assertEqual(r, esperado)

    def test_variavel_livre_vira_atomo(self):
        self.assertEqual(de_lambda(analisar("a b")), Ap(Atomo("a"), Atomo("b")))

    def test_nome_reservado(self):
        with self.assertRaises(ValueError):
            de_lambda(analisar("\\S.S"))
        with self.assertRaises(ValueError):
            de_lambda(analisar("K"))

    def test_omega_diverge(self):
        w = de_lambda(analisar("(\\a.a a) (\\a.a a)"))
        with self.assertRaises(LimiteExcedido):
            normalizar(w, limite=200)

    def test_mostrar_e_tamanho(self):
        t = aplicar(S, K, Ap(K, I))
        self.assertEqual(mostrar(t), "S K (K I)")
        self.assertEqual(tamanho(t), 4)


if __name__ == "__main__":
    unittest.main()
