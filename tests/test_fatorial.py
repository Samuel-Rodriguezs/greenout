import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from fatorial import fatorial_iterativo, fatorial_recursivo


class TestFatorial(unittest.TestCase):
    def test_zero_e_um(self):
        for f in (fatorial_iterativo, fatorial_recursivo):
            self.assertEqual(f(0), 1)
            self.assertEqual(f(1), 1)

    def test_valores(self):
        for f in (fatorial_iterativo, fatorial_recursivo):
            self.assertEqual(f(5), 120)
            self.assertEqual(f(10), 3628800)

    def test_numero_grande(self):
        self.assertEqual(fatorial_iterativo(25), 15511210043330985984000000)
        self.assertEqual(fatorial_recursivo(25), fatorial_iterativo(25))

    def test_negativo(self):
        for f in (fatorial_iterativo, fatorial_recursivo):
            with self.assertRaises(ValueError):
                f(-1)


if __name__ == "__main__":
    unittest.main()
