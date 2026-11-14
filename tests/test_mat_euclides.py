import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_euclides import euclides_estendido, mdc, mmc


class TestEuclides(unittest.TestCase):
    def test_mdc(self):
        self.assertEqual(mdc(48, 18), 6)
        self.assertEqual(mdc(17, 5), 1)
        self.assertEqual(mdc(0, 7), 7)
        self.assertEqual(mdc(0, 0), 0)
        self.assertEqual(mdc(-12, 18), 6)

    def test_mmc(self):
        self.assertEqual(mmc(4, 6), 12)
        self.assertEqual(mmc(0, 5), 0)
        self.assertEqual(mmc(-3, 5), 15)

    def test_estendido(self):
        for a, b in [(240, 46), (17, 5), (0, 9), (9, 0), (-12, 18), (35, 15)]:
            g, x, y = euclides_estendido(a, b)
            self.assertEqual(g, mdc(a, b))
            self.assertEqual(a * x + b * y, g)

    def test_coeficientes_conhecidos(self):
        g, x, y = euclides_estendido(240, 46)
        self.assertEqual((g, x, y), (2, -9, 47))


if __name__ == "__main__":
    unittest.main()
