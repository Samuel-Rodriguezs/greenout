import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_pearson import pearson


class TestPearson(unittest.TestCase):
    def test_correlacao_perfeita(self):
        self.assertAlmostEqual(pearson([1, 2, 3, 4], [2, 4, 6, 8]), 1.0)
        self.assertAlmostEqual(pearson([1, 2, 3, 4], [8, 6, 4, 2]), -1.0)

    def test_sem_correlacao(self):
        self.assertAlmostEqual(pearson([1, 2, 3], [2, 1, 2]), 0.0)

    def test_valor_conhecido(self):
        self.assertAlmostEqual(pearson([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]), 0.8)

    def test_erros(self):
        with self.assertRaises(ValueError):
            pearson([1, 2], [1])
        with self.assertRaises(ValueError):
            pearson([1], [1])
        with self.assertRaises(ValueError):
            pearson([1, 1, 1], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
