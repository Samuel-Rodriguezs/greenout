import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_maybe import (
    NADA, Just, Nothing, de_optional, filtrar, lift2, ou_else,
    para_optional, sequence, traverse, unit,
)


def inv(x):
    return NADA if x == 0 else Just(1 / x)


def meio(x):
    return Just(x // 2) if x % 2 == 0 else NADA


class TestMaybe(unittest.TestCase):
    def test_leis_monad(self):
        f, g = inv, meio
        self.assertEqual(unit(4).bind(f), f(4))  # identidade à esquerda
        for m in (Just(3), NADA, Just(0)):
            self.assertEqual(m.bind(unit), m)  # identidade à direita
            self.assertEqual(m.bind(f).bind(g), m.bind(lambda x: f(x).bind(g)))

    def test_leis_functor(self):
        for m in (Just(2), NADA):
            self.assertEqual(m.map(lambda x: x), m)
            f, g = (lambda x: x + 1), (lambda x: x * 3)
            self.assertEqual(m.map(lambda x: g(f(x))), m.map(f).map(g))

    def test_leis_applicative(self):
        f = lambda x: x + 10
        self.assertEqual(Just(f).ap(Just(1)), Just(11))  # homomorfismo
        self.assertEqual(Just(lambda x: x).ap(Just(5)), Just(5))  # identidade
        self.assertEqual(NADA.ap(Just(1)), NADA)
        self.assertEqual(Just(f).ap(NADA), NADA)

    def test_get_or_e_optional(self):
        self.assertEqual(Just(1).get_or(9), 1)
        self.assertEqual(NADA.get_or(9), 9)
        self.assertEqual(de_optional(None), NADA)
        self.assertEqual(de_optional(0), Just(0))
        self.assertIsNone(para_optional(NADA))
        self.assertEqual(para_optional(Just(3)), 3)

    def test_filtrar_ou_else(self):
        self.assertEqual(filtrar(Just(4), lambda x: x > 3), Just(4))
        self.assertEqual(filtrar(Just(1), lambda x: x > 3), NADA)
        self.assertEqual(ou_else(NADA, Just(2)), Just(2))
        self.assertEqual(ou_else(Just(1), Just(2)), Just(1))

    def test_sequence_traverse(self):
        self.assertEqual(sequence([Just(1), Just(2)]), Just([1, 2]))
        self.assertEqual(sequence([Just(1), NADA]), NADA)
        self.assertEqual(sequence([]), Just([]))
        self.assertEqual(traverse(meio, [2, 4]), Just([1, 2]))
        self.assertEqual(traverse(meio, [2, 3]), NADA)

    def test_lift2_e_imutabilidade(self):
        self.assertEqual(lift2(lambda a, b: a + b, Just(1), Just(2)), Just(3))
        self.assertEqual(lift2(lambda a, b: a + b, Just(1), NADA), NADA)
        with self.assertRaises(Exception):
            Just(1).valor = 2
        self.assertIsInstance(NADA, Nothing)


if __name__ == "__main__":
    unittest.main()
