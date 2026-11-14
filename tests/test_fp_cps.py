import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_cps import (
    Cont, call_cc, fatorial_cps, fibonacci_cps, mapear_cps, procurar, produto,
    produto_com_saida, soma_arvore_cps, tentar_cc, unit,
)

ident = lambda x: x


class TestCPS(unittest.TestCase):
    def test_fatorial_e_fibonacci(self):
        self.assertEqual([fatorial_cps(n, ident) for n in range(8)], [math.factorial(n) for n in range(8)])
        self.assertEqual([fibonacci_cps(n, ident) for n in range(10)], [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])
        with self.assertRaises(ValueError):
            fatorial_cps(-1, ident)

    def test_continuacao_arbitraria(self):
        self.assertEqual(fatorial_cps(5, lambda r: f"fat={r}"), "fat=120")
        saida = []
        fatorial_cps(3, saida.append)
        self.assertEqual(saida, [6])

    def test_mapear_cps(self):
        dobro = lambda x, k: k(x * 2)
        self.assertEqual(mapear_cps(dobro, [1, 2, 3], ident), [2, 4, 6])
        self.assertEqual(mapear_cps(dobro, [], ident), [])

    def test_soma_arvore(self):
        arv = ((None, 1, None), 2, ((None, 3, None), 4, None))
        self.assertEqual(soma_arvore_cps(arv, ident), 10)
        self.assertEqual(soma_arvore_cps(None, ident), 0)

    def test_produto_com_saida(self):
        self.assertEqual(produto_com_saida([2, 3], lambda v: ("saiu", v), lambda v: ("fim", v)), ("fim", 6))
        self.assertEqual(produto_com_saida([2, 0, 3], lambda v: ("saiu", v), lambda v: ("fim", v)), ("saiu", 0))


class TestCont(unittest.TestCase):
    def test_leis_monad(self):
        f = lambda x: Cont(lambda k: k(x + 1))
        g = lambda x: unit(x * 2)
        self.assertEqual(unit(3).bind(f).executar(), f(3).executar())
        m = Cont(lambda k: k(10))
        self.assertEqual(m.bind(unit).executar(), m.executar())
        self.assertEqual(m.bind(f).bind(g).executar(), m.bind(lambda x: f(x).bind(g)).executar())

    def test_functor_ap_e_continuacao_final(self):
        m = unit(4)
        self.assertEqual(m.map(lambda x: x).executar(), 4)
        self.assertEqual(m.map(lambda x: x + 1).executar(lambda v: v * 100), 500)
        self.assertEqual(unit(lambda x: x + 1).ap(unit(1)).executar(), 2)

    def test_continuacao_chamada_multiplas_vezes(self):
        escolha = Cont(lambda k: [k(1), k(2), k(3)])  # não-determinismo via k múltiplo
        self.assertEqual(escolha.map(lambda x: x * x).executar(), [1, 4, 9])

    def test_call_cc_sem_escape_equivale_ao_corpo(self):
        self.assertEqual(call_cc(lambda esc: unit(5)).executar(), 5)

    def test_call_cc_escape_descarta_o_resto(self):
        efeitos = []
        prog = call_cc(lambda esc: esc(1).bind(lambda _: Cont(lambda k: efeitos.append("nunca") or k(2))))
        self.assertEqual(prog.map(lambda x: x + 10).executar(), 11)
        self.assertEqual(efeitos, [])

    def test_produto_curto_circuito(self):
        self.assertEqual(produto([2, 3, 4]).executar(), 24)
        self.assertEqual(produto([2, 0, 4]).executar(), 0)
        self.assertEqual(produto([]).executar(), 1)

        def gen():
            yield 5
            yield 0
            raise AssertionError("não deveria consumir além do zero")
        self.assertEqual(produto(gen()).executar(), 0)

    def test_procurar(self):
        self.assertEqual(procurar(lambda x: x > 2, [1, 2, 3, 4]).executar(), 3)
        self.assertIsNone(procurar(lambda x: x > 9, [1, 2]).executar())
        self.assertEqual(procurar(lambda x: x > 2, [5]).map(lambda v: v + 1).executar(), 6)

    def test_excecao_via_continuacao(self):
        def corpo(lancar):
            return unit(10).bind(lambda x: lancar("ruim") if x > 5 else unit(x))
        r = tentar_cc(corpo, lambda e: unit(f"tratado: {e}")).executar()
        self.assertEqual(r, "tratado: ruim")
        ok = tentar_cc(lambda lancar: unit(3), lambda e: unit("x")).executar()
        self.assertEqual(ok, 3)


if __name__ == "__main__":
    unittest.main()
