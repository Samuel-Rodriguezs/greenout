import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_state import (
    State, desempilhar, empilhar, get, gets, mapear_m, modify, put,
    rotular, sequence, unit,
)


def incrementa(x):
    return State(lambda s: (x + s, s + 1))


def dobra_estado(x):
    return State(lambda s: (x * 2, s * 2))


class TestState(unittest.TestCase):
    def test_leis_monad(self):
        for s0 in (0, 5):
            self.assertEqual(unit(3).bind(incrementa).executar(s0), incrementa(3).executar(s0))
            m = incrementa(1)
            self.assertEqual(m.bind(unit).executar(s0), m.executar(s0))
            self.assertEqual(
                m.bind(incrementa).bind(dobra_estado).executar(s0),
                m.bind(lambda x: incrementa(x).bind(dobra_estado)).executar(s0),
            )

    def test_functor(self):
        m = incrementa(1)
        self.assertEqual(m.map(lambda x: x).executar(2), m.executar(2))
        f, g = (lambda x: x + 1), (lambda x: x * 3)
        self.assertEqual(m.map(lambda x: g(f(x))).executar(2), m.map(f).map(g).executar(2))

    def test_get_put_modify(self):
        prog = get().bind(lambda s: put(s + 10)).bind(lambda _: modify(lambda s: s * 2)).bind(
            lambda _: gets(lambda s: s - 1)
        )
        self.assertEqual(prog.executar(1), (21, 22))
        self.assertEqual(prog.avaliar(1), 21)
        self.assertEqual(prog.estado_final(1), 22)

    def test_ap(self):
        r = State(lambda s: (lambda x: x + s, s + 1)).ap(State(lambda s: (s * 10, s)))
        self.assertEqual(r.executar(1), (21, 2))

    def test_rotular_arvore(self):
        arv = (("a", "b"), ("c", ("d", "e")))
        res, n = rotular(arv).executar(0)
        self.assertEqual(res, (((0, "a"), (1, "b")), ((2, "c"), ((3, "d"), (4, "e")))))
        self.assertEqual(n, 5)
        self.assertEqual(rotular("x").executar(7), ((7, "x"), 8))

    def test_pilha(self):
        prog = empilhar(1).bind(lambda _: empilhar(2)).bind(lambda _: desempilhar())
        self.assertEqual(prog.executar(()), (2, (1,)))
        with self.assertRaises(IndexError):
            desempilhar().executar(())

    def test_mapear_sequence_sem_mutar_entrada(self):
        r, s = mapear_m(incrementa, [10, 20, 30]).executar(0)
        self.assertEqual((r, s), ([10, 21, 32], 3))
        self.assertEqual(sequence([get(), get()]).executar(4), ([4, 4], 4))
        self.assertEqual(mapear_m(incrementa, []).executar(9), ([], 9))
        m = incrementa(0)
        m.executar(0)
        self.assertEqual(m.executar(0), (0, 1))  # reexecutável


if __name__ == "__main__":
    unittest.main()
