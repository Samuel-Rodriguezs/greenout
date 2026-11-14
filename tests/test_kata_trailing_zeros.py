import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_trailing_zeros import zeros_fatorial


def forca_bruta(n: int, base: int) -> int:
    f, zeros = math.factorial(n), 0
    while f % base == 0:
        f //= base
        zeros += 1
    return zeros


class TestKataTrailingZeros(unittest.TestCase):
    def test_pequenos(self):
        self.assertEqual(zeros_fatorial(0), 0)
        self.assertEqual(zeros_fatorial(1), 0)
        self.assertEqual(zeros_fatorial(4), 0)
        self.assertEqual(zeros_fatorial(5), 1)

    def test_valores_conhecidos(self):
        self.assertEqual(zeros_fatorial(10), 2)
        self.assertEqual(zeros_fatorial(25), 6)
        self.assertEqual(zeros_fatorial(100), 24)
        self.assertEqual(zeros_fatorial(1000), 249)

    def test_muito_grande(self):
        self.assertEqual(zeros_fatorial(10 ** 9), 249999998)

    def test_confere_com_forca_bruta_base_10(self):
        for n in range(0, 300):
            self.assertEqual(zeros_fatorial(n), forca_bruta(n, 10), n)

    def test_outras_bases(self):
        for base in (2, 3, 4, 6, 8, 12, 16, 36):
            for n in (0, 1, 7, 20, 50, 120):
                self.assertEqual(zeros_fatorial(n, base), forca_bruta(n, base), (n, base))

    def test_base_prima_grande(self):
        self.assertEqual(zeros_fatorial(100, 97), 1)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            zeros_fatorial(-1)
        with self.assertRaises(ValueError):
            zeros_fatorial(5, 1)


if __name__ == "__main__":
    unittest.main()
