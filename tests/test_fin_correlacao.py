import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_correlacao import correlacao, matriz_correlacao


class TestCorrelacao(unittest.TestCase):
    def test_perfeita(self):
        self.assertAlmostEqual(correlacao([1, 2, 3], [2, 4, 6]), 1.0)
        self.assertAlmostEqual(correlacao([1, 2, 3], [6, 4, 2]), -1.0)

    def test_a_mao(self):
        # a=[1,2,3,4], b=[1,3,2,4]: sab=4, saa=sbb=5 -> 0.8
        self.assertAlmostEqual(correlacao([1, 2, 3, 4], [1, 3, 2, 4]), 0.8)

    def test_ortogonal(self):
        self.assertAlmostEqual(correlacao([1, 0, -1, 0], [0, 1, 0, -1]), 0.0)

    def test_matriz(self):
        m = matriz_correlacao({"A": [1, 2, 3, 4], "B": [1, 3, 2, 4], "C": [4, 3, 2, 1]})
        self.assertEqual(m["A"]["A"], 1.0)
        self.assertAlmostEqual(m["A"]["B"], 0.8)
        self.assertEqual(m["A"]["B"], m["B"]["A"])
        self.assertAlmostEqual(m["A"]["C"], -1.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            correlacao([1, 2], [1])
        with self.assertRaises(ValueError):
            correlacao([1, 1, 1], [1, 2, 3])
        with self.assertRaises(ValueError):
            correlacao([1], [1])


if __name__ == "__main__":
    unittest.main()
