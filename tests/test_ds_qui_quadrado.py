import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_qui_quadrado import aderencia, esperados_independencia, independencia, qui2_sf


class TestQuiQuadrado(unittest.TestCase):
    def test_sf_conhecida(self):
        self.assertAlmostEqual(qui2_sf(2.0, 2), math.exp(-1), places=10)
        self.assertAlmostEqual(qui2_sf(3.841459, 1), 0.05, places=5)
        self.assertAlmostEqual(qui2_sf(0, 3), 1.0)
        self.assertAlmostEqual(qui2_sf(20.0, 4), math.exp(-10) * (1 + 10), places=10)

    def test_aderencia(self):
        r = aderencia([20, 30], [25, 25])
        self.assertAlmostEqual(r.estatistica, 2.0)
        self.assertEqual(r.gl, 1)
        self.assertAlmostEqual(r.p_valor, math.erfc(1.0), places=8)

    def test_aderencia_perfeita(self):
        r = aderencia([10, 10, 10], [10, 10, 10])
        self.assertEqual(r.estatistica, 0)
        self.assertAlmostEqual(r.p_valor, 1.0)

    def test_independencia(self):
        t = [[10, 20], [30, 40]]
        esp = esperados_independencia(t)
        self.assertEqual(esp, [[12, 18], [28, 42]])
        r = independencia(t)
        self.assertAlmostEqual(r.estatistica, 4 / 12 + 4 / 18 + 4 / 28 + 4 / 42)
        self.assertEqual(r.gl, 1)
        self.assertAlmostEqual(r.p_valor, math.erfc(math.sqrt(r.estatistica / 2)), places=8)

    def test_erros(self):
        with self.assertRaises(ValueError):
            aderencia([1, 2], [1])
        with self.assertRaises(ValueError):
            aderencia([1, 2], [0, 3])
        with self.assertRaises(ValueError):
            aderencia([1, 2], [2, 2])
        with self.assertRaises(ValueError):
            independencia([[1, 2]])
        with self.assertRaises(ValueError):
            independencia([[0, 0], [1, 2]])


if __name__ == "__main__":
    unittest.main()
