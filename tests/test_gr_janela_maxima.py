import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_janela_maxima import janela_maxima, janela_minima


class TestJanela(unittest.TestCase):
    def test_classico(self):
        self.assertEqual(janela_maxima([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7])

    def test_minimo(self):
        self.assertEqual(janela_minima([1, 3, -1, -3, 5, 3, 6, 7], 3), [-1, -3, -3, -3, 3, 3])

    def test_k_um_e_k_igual_n(self):
        self.assertEqual(janela_maxima([4, 2, 9], 1), [4, 2, 9])
        self.assertEqual(janela_maxima([4, 2, 9], 3), [9])

    def test_k_maior_que_n_e_vazio(self):
        self.assertEqual(janela_maxima([1, 2], 5), [])
        self.assertEqual(janela_maxima([], 1), [])

    def test_k_invalido(self):
        with self.assertRaises(ValueError):
            janela_maxima([1], 0)

    def test_repetidos(self):
        self.assertEqual(janela_maxima([5, 5, 5, 5], 2), [5, 5, 5])

    def test_aleatorio(self):
        rnd = random.Random(9)
        nums = [rnd.randint(-20, 20) for _ in range(100)]
        for k in (1, 2, 7, 50, 100):
            self.assertEqual(janela_maxima(nums, k), [max(nums[i:i + k]) for i in range(len(nums) - k + 1)])
            self.assertEqual(janela_minima(nums, k), [min(nums[i:i + k]) for i in range(len(nums) - k + 1)])


if __name__ == "__main__":
    unittest.main()
