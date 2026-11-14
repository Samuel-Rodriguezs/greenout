import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from mat_complexo import NumeroComplexo as C


class TestComplexo(unittest.TestCase):
    def test_soma_sub_mult(self):
        a, b = C(1, 2), C(3, -1)
        self.assertEqual(a + b, C(4, 1))
        self.assertEqual(a - b, C(-2, 3))
        self.assertEqual(a * b, C(5, 5))

    def test_divisao(self):
        r = C(1, 2) / C(3, -1)
        self.assertAlmostEqual(r.real, 0.1)
        self.assertAlmostEqual(r.imag, 0.7)
        with self.assertRaises(ZeroDivisionError):
            C(1, 1) / C(0, 0)

    def test_i_ao_quadrado(self):
        self.assertEqual(C(0, 1) * C(0, 1), C(-1, 0))

    def test_modulo_argumento(self):
        self.assertAlmostEqual(C(3, 4).modulo(), 5.0)
        self.assertAlmostEqual(C(0, 1).argumento(), math.pi / 2)

    def test_polar(self):
        z = C.polar(2, math.pi)
        self.assertAlmostEqual(z.real, -2.0)
        self.assertAlmostEqual(z.imag, 0.0)

    def test_potencia(self):
        self.assertEqual(C(0, 1).potencia(4), C(1, 0))
        self.assertEqual(C(1, 1).potencia(0), C(1, 0))
        r = C(1, 1).potencia(-2)
        self.assertAlmostEqual(r.imag, -0.5)

    def test_str_e_escalares(self):
        self.assertEqual(str(C(1, -2)), "1 - 2i")
        self.assertEqual(C(1, 2) + 1, C(2, 2))
        self.assertEqual(2 * C(1, 2), C(2, 4))
        self.assertEqual(C(3, 4).conjugado(), C(3, -4))


if __name__ == "__main__":
    unittest.main()
