import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_newton import newton, raiz_quadrada


class TestNewton(unittest.TestCase):
    def test_raiz_de_2(self):
        r = newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0)
        self.assertAlmostEqual(r, 2 ** 0.5, places=10)

    def test_cubica(self):
        r = newton(lambda x: x ** 3 - 27, lambda x: 3 * x * x, 5.0)
        self.assertAlmostEqual(r, 3.0, places=9)

    def test_derivada_nula(self):
        with self.assertRaises(ZeroDivisionError):
            newton(lambda x: x * x + 1, lambda x: 2 * x, 0.0)

    def test_nao_converge(self):
        with self.assertRaises(RuntimeError):
            newton(lambda x: x * x + 1, lambda x: 2 * x, 0.5, max_iter=3)

    def test_raiz_quadrada(self):
        self.assertAlmostEqual(raiz_quadrada(144), 12.0, places=9)
        self.assertAlmostEqual(raiz_quadrada(0.25), 0.5, places=9)
        self.assertEqual(raiz_quadrada(0), 0.0)
        with self.assertRaises(ValueError):
            raiz_quadrada(-1)


if __name__ == "__main__":
    unittest.main()
