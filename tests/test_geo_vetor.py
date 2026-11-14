import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_vetor import Vetor2, Vetor3


class TestVetor2(unittest.TestCase):
    def test_operacoes(self):
        a, b = Vetor2(1, 2), Vetor2(3, -1)
        self.assertEqual(a + b, Vetor2(4, 1))
        self.assertEqual(a - b, Vetor2(-2, 3))
        self.assertEqual(2 * a, Vetor2(2, 4))
        self.assertEqual(-a, Vetor2(-1, -2))

    def test_dot_cross_norma(self):
        self.assertEqual(Vetor2(1, 2).dot(Vetor2(3, -1)), 1)
        self.assertEqual(Vetor2(1, 0).cross(Vetor2(0, 1)), 1)
        self.assertEqual(Vetor2(3, 4).norma(), 5)

    def test_normalizar_nulo(self):
        with self.assertRaises(ValueError):
            Vetor2(0, 0).normalizado()
        self.assertAlmostEqual(Vetor2(0, 5).normalizado().y, 1)

    def test_angulos(self):
        self.assertAlmostEqual(Vetor2(1, 0).angulo_com(Vetor2(0, 1)), math.pi / 2)
        self.assertAlmostEqual(Vetor2(1, 0).angulo_com(Vetor2(-1, 0)), math.pi)
        self.assertEqual(Vetor2(1, 0).perpendicular(), Vetor2(0, 1))

    def test_projecao(self):
        self.assertEqual(Vetor2(3, 4).projetar_em(Vetor2(2, 0)), Vetor2(3, 0))
        with self.assertRaises(ValueError):
            Vetor2(1, 1).projetar_em(Vetor2(0, 0))


class TestVetor3(unittest.TestCase):
    def test_cross_canonico(self):
        self.assertEqual(Vetor3(1, 0, 0).cross(Vetor3(0, 1, 0)), Vetor3(0, 0, 1))
        self.assertEqual(Vetor3(0, 1, 0).cross(Vetor3(1, 0, 0)), Vetor3(0, 0, -1))

    def test_dot_norma(self):
        self.assertEqual(Vetor3(1, 2, 3).dot(Vetor3(4, -5, 6)), 12)
        self.assertEqual(Vetor3(2, 3, 6).norma(), 7)

    def test_produto_misto_volume(self):
        self.assertEqual(Vetor3(1, 0, 0).produto_misto(Vetor3(0, 2, 0), Vetor3(0, 0, 3)), 6)

    def test_nulo(self):
        with self.assertRaises(ValueError):
            Vetor3(0, 0, 0).normalizado()


if __name__ == "__main__":
    unittest.main()
