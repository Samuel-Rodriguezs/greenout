import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_spearman import postos, spearman, spearman_p_valor


class TestSpearman(unittest.TestCase):
    def test_postos_com_empate(self):
        self.assertEqual(postos([5, 6, 7, 8, 7]), [1, 2, 3.5, 5, 3.5])
        self.assertEqual(postos([10, 10, 10]), [2, 2, 2])

    def test_monotonica_nao_linear(self):
        x = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(spearman(x, [v ** 3 for v in x]), 1.0)
        self.assertAlmostEqual(spearman(x, [-v for v in x]), -1.0)

    def test_com_empates(self):
        # sum dxdy = 8; sum dx2 = 10; sum dy2 = 9.5 -> 8/sqrt(95)
        r = spearman([1, 2, 3, 4, 5], [5, 6, 7, 8, 7])
        self.assertAlmostEqual(r, 8 / 95 ** 0.5, places=6)

    def test_nao_ordenado(self):
        # postos x [3,1,2], y [1,2,3]: dx=[1,-1,0], dy=[-1,0,1] -> sxy=-1; r=-1/2
        self.assertAlmostEqual(spearman([30, 10, 20], [1, 2, 3]), -0.5)

    def test_erros(self):
        with self.assertRaises(ValueError):
            spearman([1, 2], [1])
        with self.assertRaises(ValueError):
            spearman([1, 1, 1], [1, 2, 3])
        with self.assertRaises(ValueError):
            spearman([1], [1])

    def test_p_valor(self):
        self.assertEqual(spearman_p_valor(1.0, 10), 0.0)
        self.assertAlmostEqual(spearman_p_valor(0.0, 10), 1.0)
        # correlação alta com n grande: p pequeno
        self.assertLess(spearman_p_valor(0.8, 30), 0.001)


if __name__ == "__main__":
    unittest.main()
