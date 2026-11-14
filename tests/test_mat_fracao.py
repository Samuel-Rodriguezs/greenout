import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_fracao import Fracao


class TestFracao(unittest.TestCase):
    def test_simplificacao_e_sinal(self):
        f = Fracao(6, -8)
        self.assertEqual((f.num, f.den), (-3, 4))
        self.assertEqual(str(Fracao(4, 2)), "2")
        self.assertEqual(str(Fracao(0, 5)), "0")

    def test_operacoes(self):
        a, b = Fracao(1, 2), Fracao(1, 3)
        self.assertEqual(a + b, Fracao(5, 6))
        self.assertEqual(a - b, Fracao(1, 6))
        self.assertEqual(a * b, Fracao(1, 6))
        self.assertEqual(a / b, Fracao(3, 2))
        self.assertEqual(-a, Fracao(-1, 2))

    def test_com_inteiros(self):
        self.assertEqual(Fracao(1, 2) + 1, Fracao(3, 2))
        self.assertEqual(2 * Fracao(1, 4), Fracao(1, 2))
        self.assertEqual(1 - Fracao(1, 4), Fracao(3, 4))

    def test_comparacao(self):
        self.assertTrue(Fracao(1, 3) < Fracao(1, 2))
        self.assertTrue(Fracao(1, 2) <= Fracao(2, 4))
        self.assertEqual(hash(Fracao(1, 2)), hash(Fracao(2, 4)))

    def test_float(self):
        self.assertAlmostEqual(float(Fracao(1, 3)), 0.333333333, places=8)

    def test_erros(self):
        with self.assertRaises(ZeroDivisionError):
            Fracao(1, 0)
        with self.assertRaises(ZeroDivisionError):
            Fracao(1, 2) / Fracao(0, 3)
        with self.assertRaises(TypeError):
            Fracao(1, 2) + "x"


if __name__ == "__main__":
    unittest.main()
