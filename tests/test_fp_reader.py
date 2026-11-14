import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_reader import Reader, ask, asks, local, saudacao, sequence, unit


def mais_env(x):
    return asks(lambda env: x + env)


def vezes_env(x):
    return asks(lambda env: x * env)


class TestReader(unittest.TestCase):
    def test_leis_monad(self):
        for env in (0, 3, -2):
            self.assertEqual(unit(4).bind(mais_env).executar(env), mais_env(4).executar(env))
            r = asks(lambda e: e * 10)
            self.assertEqual(r.bind(unit).executar(env), r.executar(env))
            self.assertEqual(
                r.bind(mais_env).bind(vezes_env).executar(env),
                r.bind(lambda x: mais_env(x).bind(vezes_env)).executar(env),
            )

    def test_functor(self):
        r = ask()
        f, g = (lambda x: x + 1), (lambda x: x * 2)
        self.assertEqual(r.map(lambda x: x).executar(5), 5)
        self.assertEqual(r.map(lambda x: g(f(x))).executar(5), r.map(f).map(g).executar(5))

    def test_ap(self):
        r = Reader(lambda e: lambda x: x + e).ap(asks(lambda e: e * 2))
        self.assertEqual(r.executar(3), 9)

    def test_ask_e_local(self):
        r = local(lambda e: e + 1, ask())
        self.assertEqual(r.executar(1), 2)
        combinado = ask().bind(lambda externo: local(lambda e: e * 10, ask()).map(lambda i: (externo, i)))
        self.assertEqual(combinado.executar(2), (2, 20))

    def test_saudacao_e_ambiente_inalterado(self):
        cfg = {"prefixo": "Olá,", "nome": "Ana"}
        self.assertEqual(saudacao().executar(cfg), "Olá, Ana")
        self.assertEqual(cfg, {"prefixo": "Olá,", "nome": "Ana"})
        with self.assertRaises(KeyError):
            saudacao().executar({})

    def test_sequence(self):
        self.assertEqual(sequence([ask(), asks(lambda e: e + 1)]).executar(1), [1, 2])
        self.assertEqual(sequence([]).executar(1), [])


if __name__ == "__main__":
    unittest.main()
