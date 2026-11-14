import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from numero_perfeito import eh_perfeito, perfeitos_ate


class TestNumeroPerfeito(unittest.TestCase):
    def test_perfeitos_conhecidos(self):
        for n in (6, 28, 496, 8128):
            self.assertTrue(eh_perfeito(n))

    def test_nao_perfeitos(self):
        for n in (2, 12, 27, 100, 497):
            self.assertFalse(eh_perfeito(n))

    def test_bordas(self):
        for n in (1, 0, -6):
            self.assertFalse(eh_perfeito(n))

    def test_quadrado_perfeito_nao_duplica_divisor(self):
        self.assertFalse(eh_perfeito(16))

    def test_perfeitos_ate(self):
        self.assertEqual(perfeitos_ate(10000), [6, 28, 496, 8128])
        self.assertEqual(perfeitos_ate(5), [])


if __name__ == "__main__":
    unittest.main()
