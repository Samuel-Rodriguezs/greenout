import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_refinados import (NAO_VAZIA, NATURAL, PORCENTAGEM, POSITIVO,
                             ErroRefinamento, ValorRefinado, comprimento,
                             contrato, elementos, faixa, implica, refinar)


class TestRefinados(unittest.TestCase):
    def test_contem(self):
        self.assertTrue(POSITIVO.contem(3))
        self.assertFalse(POSITIVO.contem(0))
        self.assertFalse(POSITIVO.contem(-1))

    def test_base_e_verificada(self):
        self.assertFalse(POSITIVO.contem("3"))
        self.assertFalse(POSITIVO.contem(2.5))
        self.assertFalse(POSITIVO.contem(True))  # bool não é int aqui

    def test_validar_devolve_ou_levanta(self):
        self.assertEqual(NATURAL.validar(0), 0)
        with self.assertRaisesRegex(ErroRefinamento, "Natural"):
            NATURAL.validar(-5)

    def test_predicado_que_explode_vira_falso(self):
        r = refinar("PrimeiroPar", list, lambda xs: xs[0] % 2 == 0)
        self.assertTrue(r.contem([2, 3]))
        self.assertFalse(r.contem([]))      # IndexError no predicado

    def test_faixa(self):
        self.assertTrue(PORCENTAGEM.contem(0) and PORCENTAGEM.contem(100))
        self.assertFalse(PORCENTAGEM.contem(101))
        f = faixa(0.0, 1.0, float)
        self.assertTrue(f.contem(0.5))
        self.assertFalse(f.contem(1))  # int não é float

    def test_comprimento(self):
        self.assertTrue(NAO_VAZIA.contem("a"))
        self.assertFalse(NAO_VAZIA.contem(""))
        s = comprimento(2, 4)
        self.assertEqual([s.contem(x) for x in ("a", "ab", "abcd", "abcde")],
                         [False, True, True, False])

    def test_refinamento_sobre_refinamento(self):
        par_positivo = refinar("ParPositivo", POSITIVO, lambda v: v % 2 == 0)
        self.assertTrue(par_positivo.contem(4))
        self.assertFalse(par_positivo.contem(0))   # falha na base
        self.assertFalse(par_positivo.contem(3))   # falha no predicado

    def test_conjuncao_e_disjuncao(self):
        pequeno = refinar("Pequeno", int, lambda v: v < 10)
        r = POSITIVO & pequeno
        self.assertTrue(r.contem(5))
        self.assertFalse(r.contem(10))
        self.assertFalse(r.contem(-1))
        u = refinar("Zero", int, lambda v: v == 0) | POSITIVO
        self.assertTrue(u.contem(0) and u.contem(7))
        self.assertFalse(u.contem(-2))

    def test_elementos(self):
        nats = elementos(NATURAL)
        self.assertTrue(nats.contem([0, 1, 2]))
        self.assertTrue(nats.contem([]))
        self.assertFalse(nats.contem([1, -1]))
        self.assertFalse(nats.contem((1, 2)))      # base é list
        strs = elementos(str, tuple)
        self.assertTrue(strs.contem(("a", "b")))
        self.assertFalse(strs.contem(("a", 1)))

    def test_valor_refinado_e_imutavel(self):
        v = POSITIVO.criar(5)
        self.assertEqual(v.valor, 5)
        with self.assertRaises(Exception):
            v.valor = 6  # dataclass congelada

    def test_mapear_revalida(self):
        v = POSITIVO.criar(5)
        self.assertEqual(v.mapear(lambda x: x * 2).valor, 10)
        with self.assertRaises(ErroRefinamento):
            v.mapear(lambda x: x - 5)
        w = v.mapear(lambda x: x - 5, NATURAL)
        self.assertEqual(w, ValorRefinado(NATURAL, 0))

    def test_implica_como_subtipagem_amostral(self):
        amostras = range(-5, 20)
        self.assertTrue(implica(POSITIVO, NATURAL, amostras))
        self.assertFalse(implica(NATURAL, POSITIVO, amostras))

    def test_contrato_argumentos(self):
        @contrato(x=POSITIVO, y=int)
        def f(x, y=1):
            return x + y
        self.assertEqual(f(2), 3)
        self.assertEqual(f(x=2, y=5), 7)
        with self.assertRaisesRegex(ErroRefinamento, r"f\(x\)"):
            f(0)
        with self.assertRaisesRegex(ErroRefinamento, r"f\(y\)"):
            f(1, "a")

    def test_contrato_retorno(self):
        @contrato(NATURAL, a=int, b=int)
        def sub(a, b):
            return a - b
        self.assertEqual(sub(5, 2), 3)
        with self.assertRaisesRegex(ErroRefinamento, "retorno"):
            sub(2, 5)

    def test_contrato_preserva_metadados(self):
        @contrato(x=int)
        def g(x):
            """doc"""
            return x
        self.assertEqual(g.__name__, "g")
        self.assertEqual(g.__doc__, "doc")

    def test_contrato_parametro_inexistente(self):
        with self.assertRaises(TypeError):
            @contrato(z=int)
            def h(x):
                return x

    def test_divisao_segura(self):
        nao_zero = refinar("NaoZero", int, lambda v: v != 0)

        @contrato(a=int, b=nao_zero)
        def dividir(a, b):
            return a // b
        self.assertEqual(dividir(7, 2), 3)
        with self.assertRaises(ErroRefinamento):
            dividir(7, 0)


if __name__ == "__main__":
    unittest.main()
