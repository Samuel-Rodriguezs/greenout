import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_soma_alvo import three_sum, two_sum


class TestSomaAlvo(unittest.TestCase):
    def test_two_sum(self):
        self.assertEqual(two_sum([2, 7, 11, 15], 9), (0, 1))
        self.assertEqual(two_sum([3, 2, 4], 6), (1, 2))

    def test_two_sum_duplicado_e_negativo(self):
        self.assertEqual(two_sum([3, 3], 6), (0, 1))
        self.assertEqual(two_sum([-1, -2, -3, -4], -6), (1, 3))

    def test_two_sum_nao_reusa_elemento(self):
        self.assertIsNone(two_sum([3], 6))
        self.assertIsNone(two_sum([], 0))
        self.assertIsNone(two_sum([1, 2], 10))

    def test_three_sum_classico(self):
        self.assertEqual(three_sum([-1, 0, 1, 2, -1, -4]), [(-1, -1, 2), (-1, 0, 1)])

    def test_three_sum_bordas(self):
        self.assertEqual(three_sum([]), [])
        self.assertEqual(three_sum([0, 0]), [])
        self.assertEqual(three_sum([0, 0, 0, 0]), [(0, 0, 0)])
        self.assertEqual(three_sum([1, 2, 3], 6), [(1, 2, 3)])

    def test_three_sum_contra_forca_bruta(self):
        rnd = random.Random(5)
        for _ in range(50):
            nums = [rnd.randint(-5, 5) for _ in range(rnd.randint(0, 12))]
            esperado = sorted({tuple(sorted(t)) for t in itertools.combinations(nums, 3) if sum(t) == 0})
            self.assertEqual(three_sum(nums), esperado)


if __name__ == "__main__":
    unittest.main()
