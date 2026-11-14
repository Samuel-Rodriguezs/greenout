import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_thunk import (
    ErroCiclo, PorNome, Thunk, e_, forcar, ou_, preguicoso,
    propriedade_preguicosa, se,
)


class TestThunk(unittest.TestCase):
    def test_nao_avalia_ate_forcar(self):
        calls = []
        t = Thunk(lambda: calls.append(1) or 42)
        self.assertEqual(calls, [])
        self.assertFalse(t.avaliado)
        self.assertEqual(t.forcar(), 42)
        self.assertTrue(t.avaliado)

    def test_call_by_need_memoiza(self):
        calls = []
        t = Thunk(lambda: calls.append(1) or 7)
        self.assertEqual((t.forcar(), t.forcar(), t.forcar()), (7, 7, 7))
        self.assertEqual(len(calls), 1)

    def test_call_by_name_reavalia(self):
        n = PorNome(lambda: 5)
        self.assertEqual(n.forcar() + n.forcar() + n.forcar(), 15)
        self.assertEqual(n.avaliacoes, 3)

    def test_valor_falsy_e_none_sao_memoizados(self):
        calls = []
        for v in (None, 0, "", False):
            t = Thunk(lambda v=v: calls.append(v) or v)
            self.assertEqual((t.forcar(), t.forcar()), (v, v))
        self.assertEqual(len(calls), 4)
        self.assertTrue(Thunk.de_valor(None).avaliado)

    def test_excecao_nao_e_memoizada(self):
        estado = {"falhar": True}

        def f():
            if estado["falhar"]:
                raise ValueError("x")
            return 1
        t = Thunk(f)
        with self.assertRaises(ValueError):
            t.forcar()
        self.assertFalse(t.avaliado)
        estado["falhar"] = False
        self.assertEqual(t.forcar(), 1)

    def test_ciclo(self):
        caixa = []
        t = Thunk(lambda: caixa[0].forcar() + 1)
        caixa.append(t)
        with self.assertRaises(ErroCiclo):
            t.forcar()

    def test_functor_e_monad_leis(self):
        t = Thunk(lambda: 3)
        f = lambda x: Thunk(lambda: x + 1)
        g = lambda x: Thunk(lambda: x * 2)
        self.assertEqual(t.map(lambda x: x).forcar(), 3)
        self.assertEqual(Thunk.de_valor(3).bind(f).forcar(), f(3).forcar())
        self.assertEqual(t.bind(Thunk.de_valor).forcar(), 3)
        self.assertEqual(t.bind(f).bind(g).forcar(), t.bind(lambda x: f(x).bind(g)).forcar())

    def test_map_e_bind_sao_preguicosos(self):
        calls = []
        t = Thunk(lambda: calls.append("a") or 1)
        m = t.map(lambda x: calls.append("b") or x + 1).bind(lambda x: Thunk(lambda: x))
        self.assertEqual(calls, [])
        self.assertEqual(m.forcar(), 2)
        self.assertEqual(calls, ["a", "b"])

    def test_se_e_curto_circuito(self):
        boom = Thunk(lambda: 1 / 0)
        self.assertEqual(se(True, 1, boom), 1)
        self.assertEqual(se(Thunk(lambda: False), boom, "ok"), "ok")
        self.assertFalse(e_(False, boom))
        self.assertTrue(ou_(True, boom))
        with self.assertRaises(ZeroDivisionError):
            se(False, 1, boom)

    def test_forcar_aninhado_e_valores_comuns(self):
        self.assertEqual(forcar(Thunk(lambda: Thunk(lambda: 5))), 5)
        self.assertEqual(forcar(9), 9)

    def test_decorador_preguicoso(self):
        calls = []

        @preguicoso
        def caro(x):
            calls.append(x)
            return x * x
        t = caro(6)
        self.assertEqual(calls, [])
        self.assertEqual(t.forcar(), 36)
        t.forcar()
        self.assertEqual(calls, [6])
        self.assertEqual(caro.__name__, "caro")

    def test_propriedade_preguicosa_por_instancia(self):
        contador = []

        class C:
            def __init__(self, n):
                self.n = n

            @propriedade_preguicosa
            def dobro(self):
                contador.append(self.n)
                return self.n * 2
        a, b = C(1), C(2)
        self.assertEqual((a.dobro, a.dobro, b.dobro), (2, 2, 4))
        self.assertEqual(contador, [1, 2])


if __name__ == "__main__":
    unittest.main()
