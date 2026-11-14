import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_free import (
    Free, Pure, escrever, executar_puro, incrementar, interpretar, ler, logar,
    rastrear, sequence, unit,
)


@dataclass(frozen=True)
class Desconhecida:
    k: object


def obs(prog, estado=None):
    return executar_puro(prog, estado or {"a": 1})


def f(x):
    return escrever("a", x * 2).map(lambda _: x + 1)


def g(x):
    return logar(f"g{x}").bind(lambda _: ler("a").map(lambda a: (x, a)))


class TestFree(unittest.TestCase):
    def test_leis_monad_observadas_pelo_interpretador(self):
        self.assertEqual(obs(unit(3).bind(f)), obs(f(3)))
        m = ler("a")
        self.assertEqual(obs(m.bind(unit)), obs(m))
        self.assertEqual(obs(m.bind(f).bind(g)), obs(m.bind(lambda x: f(x).bind(g))))

    def test_functor_leis(self):
        m = incrementar("a")
        self.assertEqual(obs(m.map(lambda x: x)), obs(m))
        h, k = (lambda x: x + 1), (lambda x: x * 5)
        self.assertEqual(obs(m.map(lambda x: k(h(x)))), obs(m.map(h).map(k)))

    def test_programa_e_valor_ate_interpretar(self):
        p = incrementar("c")
        self.assertIsInstance(p, Free)
        self.assertIsInstance(unit(1), Pure)

    def test_incrementar(self):
        r, mem, logs = executar_puro(incrementar("n"), {})
        self.assertEqual((r, mem, logs), (1, {"n": 1}, ["n -> 1"]))
        r, mem, logs = executar_puro(incrementar("n"), {"n": 41})
        self.assertEqual((r, mem["n"]), (42, 42))

    def test_estado_de_entrada_nao_e_mutado(self):
        inicial = {"a": 1}
        executar_puro(escrever("a", 99), inicial)
        self.assertEqual(inicial, {"a": 1})

    def test_programa_reexecutavel(self):
        p = incrementar("x")
        self.assertEqual(executar_puro(p, {})[0], 1)
        self.assertEqual(executar_puro(p, {})[0], 1)

    def test_dois_interpretadores_mesmo_programa(self):
        p = ler("a").bind(lambda a: escrever("b", a + 1).bind(lambda _: logar("ok")))
        self.assertEqual(rastrear(p, {"a": 5}), ["ler a", "escrever b=6", "logar ok"])
        _, mem, logs = executar_puro(p, {"a": 5})
        self.assertEqual((mem, logs), ({"a": 5, "b": 6}, ["ok"]))

    def test_sequence(self):
        r, mem, logs = executar_puro(sequence([incrementar("x"), incrementar("x"), ler("x")]), {})
        self.assertEqual((r, mem, logs), ([1, 2, 2], {"x": 2}, ["x -> 1", "x -> 2"]))
        self.assertEqual(executar_puro(sequence([]), {})[0], [])

    def test_interpretar_customizado_e_instrucao_invalida(self):
        self.assertEqual(interpretar(ler("a").map(lambda x: x * 2), lambda i: 21), 42)
        with self.assertRaises(TypeError):
            executar_puro(Free(Desconhecida(Pure)), {})

    def test_loop_longo(self):
        prog = unit(0)
        for _ in range(150):
            prog = prog.bind(lambda n: escrever("n", n + 1).map(lambda _: n + 1))
        self.assertEqual(executar_puro(prog, {})[0], 150)


if __name__ == "__main__":
    unittest.main()
