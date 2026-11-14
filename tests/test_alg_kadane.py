import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_kadane import soma_maxima_subarray


def forca_bruta(v: list[int]) -> int:
    return max(sum(v[i:j]) for i in range(len(v)) for j in range(i + 1, len(v) + 1))


class TesteKadane(unittest.TestCase):
    def test_exemplo_classico(self):
        self.assertEqual(soma_maxima_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]), 6)

    def test_um_elemento(self):
        self.assertEqual(soma_maxima_subarray([7]), 7)

    def test_todos_negativos(self):
        self.assertEqual(soma_maxima_subarray([-5, -2, -8]), -2)

    def test_todos_positivos(self):
        self.assertEqual(soma_maxima_subarray([1, 2, 3]), 6)

    def test_zeros(self):
        self.assertEqual(soma_maxima_subarray([0, 0, 0]), 0)

    def test_vazia(self):
        with self.assertRaises(ValueError):
            soma_maxima_subarray([])

    def test_contra_forca_bruta(self):
        rng = random.Random(42)
        for _ in range(100):
            v = [rng.randint(-10, 10) for _ in range(rng.randint(1, 12))]
            self.assertEqual(soma_maxima_subarray(v), forca_bruta(v))


if __name__ == "__main__":
    unittest.main()
