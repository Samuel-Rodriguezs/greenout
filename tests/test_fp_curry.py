import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_curry import _, aplicar_n, curry, curry_tupla, flip, parcial, uncurry, uncurry_tupla


def soma3(a, b, c):
    return a + b + c


class TestCurry(unittest.TestCase):
    def test_curry_formas_de_chamada(self):
        c = curry(soma3)
        self.assertEqual(c(1)(2)(3), 6)
        self.assertEqual(c(1, 2)(3), 6)
        self.assertEqual(c(1)(2, 3), 6)
        self.assertEqual(c(1, 2, 3), 6)

    def test_curry_reutilizavel(self):
        c = curry(soma3)
        mais10 = c(10)
        self.assertEqual(mais10(1)(1), 12)
        self.assertEqual(mais10(2)(2), 14)

    def test_aridade_explicita_e_varargs(self):
        c = curry(lambda *xs: sum(xs), 3)
        self.assertEqual(c(1)(2)(3), 6)
        with self.assertRaises(ValueError):
            curry(lambda *xs: sum(xs))
        with self.assertRaises(ValueError):
            curry(soma3, -1)

    def test_aridade_zero_e_defaults(self):
        self.assertEqual(curry(lambda: 5)(), 5)
        c = curry(lambda a, b=10: a + b)
        self.assertEqual(c(1), 11)  # só obrigatórios contam

    def test_uncurry_inverte_curry(self):
        f = uncurry(curry(soma3))
        self.assertEqual(f(1, 2, 3), 6)
        self.assertEqual(uncurry(lambda a: lambda b: a * b)(3, 4), 12)
        self.assertEqual(uncurry(lambda a: a + 1)(1), 2)

    def test_curry_uncurry_tupla(self):
        self.assertEqual(uncurry_tupla(soma3)((1, 2, 3)), 6)
        self.assertEqual(curry_tupla(sum)(1, 2, 3), 6)
        self.assertEqual(curry_tupla(uncurry_tupla(soma3))(1, 2, 3), 6)

    def test_flip(self):
        self.assertEqual(flip(lambda a, b: a - b)(1, 10), 9)
        self.assertEqual(flip(flip(lambda a, b: a - b))(1, 10), -9)

    def test_parcial_posicional_e_marcador(self):
        sub = lambda a, b: a - b
        self.assertEqual(parcial(sub, 10)(3), 7)
        self.assertEqual(parcial(sub, _, 3)(10), 7)
        self.assertEqual(parcial(soma3, _, 5, _)(1, 2), 8)
        self.assertEqual(parcial(soma3, _, 5)(1, 2), 8)  # sobras vão ao final
        with self.assertRaises(TypeError):
            parcial(soma3, _, _, 1)(5)

    def test_parcial_kwargs(self):
        f = parcial(int, base=2)
        self.assertEqual(f("101"), 5)
        self.assertEqual(parcial(int, base=2)("11", base=10), 11)

    def test_aplicar_n(self):
        self.assertEqual(aplicar_n(lambda x: x * 2, 5)(1), 32)
        self.assertEqual(aplicar_n(lambda x: x + 1, 0)(7), 7)
        with self.assertRaises(ValueError):
            aplicar_n(abs, -1)


if __name__ == "__main__":
    unittest.main()
