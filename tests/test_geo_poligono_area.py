import math
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_poligono_area import area, area_com_sinal, centroide, eh_convexo, perimetro

QUADRADO = [(0, 0), (4, 0), (4, 4), (0, 4)]
L = [(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]


class TestPoligonoArea(unittest.TestCase):
    def test_area_quadrado(self):
        self.assertEqual(area(QUADRADO), 16)
        self.assertEqual(area_com_sinal(QUADRADO), 16)
        self.assertEqual(area_com_sinal(QUADRADO[::-1]), -16)

    def test_area_triangulo_fracionaria(self):
        self.assertEqual(area([(0, 0), (3, 0), (0, 1)]), Fraction(3, 2))

    def test_area_forma_L(self):
        self.assertEqual(area(L), 3)

    def test_degenerados(self):
        self.assertEqual(area([]), 0)
        self.assertEqual(area([(0, 0), (1, 1)]), 0)
        self.assertEqual(area([(0, 0), (1, 1), (2, 2)]), 0)

    def test_perimetro(self):
        self.assertEqual(perimetro(QUADRADO), 16)
        self.assertAlmostEqual(perimetro([(0, 0), (3, 0), (0, 4)]), 12)
        self.assertEqual(perimetro([(1, 1)]), 0)

    def test_centroide(self):
        self.assertEqual(centroide(QUADRADO), (2, 2))
        self.assertEqual(centroide(QUADRADO[::-1]), (2, 2))
        self.assertEqual(centroide([(0, 0), (3, 0), (0, 3)]), (1, 1))

    def test_centroide_L(self):
        # L = 3 quadrados unitários: centroide (5/6, 5/6)
        self.assertEqual(centroide(L), (Fraction(5, 6), Fraction(5, 6)))

    def test_centroide_degenerado(self):
        self.assertEqual(centroide([(0, 0), (2, 2), (4, 4)]), (2, 2))
        with self.assertRaises(ValueError):
            centroide([])

    def test_convexo(self):
        self.assertTrue(eh_convexo(QUADRADO))
        self.assertTrue(eh_convexo(QUADRADO[::-1]))
        self.assertFalse(eh_convexo(L))
        self.assertFalse(eh_convexo([(0, 0), (1, 1)]))
        self.assertFalse(eh_convexo([(0, 0), (1, 1), (2, 2)]))
        self.assertTrue(eh_convexo([(0, 0), (2, 0), (4, 0), (4, 4), (0, 4)]))


if __name__ == "__main__":
    unittest.main()
