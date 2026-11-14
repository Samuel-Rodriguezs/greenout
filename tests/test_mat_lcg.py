import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_lcg import LCG


class TestLCG(unittest.TestCase):
    def test_deterministico(self):
        self.assertEqual(LCG(42).lista(5), LCG(42).lista(5))

    def test_primeiro_valor(self):
        self.assertEqual(LCG(0).proximo(), 1013904223)
        g = LCG(1, a=5, c=3, m=16)
        self.assertEqual([g.proximo() for _ in range(4)], [8, 11, 10, 5])

    def test_intervalo_float(self):
        for v in LCG(7).lista(1000):
            self.assertTrue(0.0 <= v < 1.0)

    def test_media_aproximada(self):
        v = LCG(123).lista(20000)
        self.assertAlmostEqual(sum(v) / len(v), 0.5, delta=0.02)

    def test_inteiro(self):
        g = LCG(9)
        vals = {g.inteiro(1, 6) for _ in range(500)}
        self.assertEqual(vals, {1, 2, 3, 4, 5, 6})
        self.assertEqual(g.inteiro(4, 4), 4)

    def test_erros(self):
        with self.assertRaises(ValueError):
            LCG(1, m=0)
        with self.assertRaises(ValueError):
            LCG(1).inteiro(5, 1)


if __name__ == "__main__":
    unittest.main()
