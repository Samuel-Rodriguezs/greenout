import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_prime_factors import fatores_primos


class TestKataPrimeFactors(unittest.TestCase):
    def test_um(self):
        self.assertEqual(fatores_primos(1), [])

    def test_primos(self):
        self.assertEqual(fatores_primos(2), [2])
        self.assertEqual(fatores_primos(3), [3])
        self.assertEqual(fatores_primos(97), [97])

    def test_compostos(self):
        self.assertEqual(fatores_primos(4), [2, 2])
        self.assertEqual(fatores_primos(6), [2, 3])
        self.assertEqual(fatores_primos(8), [2, 2, 2])
        self.assertEqual(fatores_primos(9), [3, 3])
        self.assertEqual(fatores_primos(100), [2, 2, 5, 5])

    def test_grande(self):
        self.assertEqual(fatores_primos(2 * 3 * 5 * 7 * 11 * 13), [2, 3, 5, 7, 11, 13])
        self.assertEqual(fatores_primos(600851475143), [71, 839, 1471, 6857])

    def test_produto_recompoe(self):
        for n in range(1, 500):
            self.assertEqual(math.prod(fatores_primos(n)), n)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            fatores_primos(0)
        with self.assertRaises(ValueError):
            fatores_primos(-4)


if __name__ == "__main__":
    unittest.main()
