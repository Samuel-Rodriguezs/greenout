import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_segmentos import intersecao, segmentos_se_cruzam


class TestSegmentos(unittest.TestCase):
    def test_cruzamento_em_x(self):
        self.assertTrue(segmentos_se_cruzam((0, 0), (4, 4), (0, 4), (4, 0)))
        self.assertEqual(intersecao((0, 0), (4, 4), (0, 4), (4, 0)), (2, 2))

    def test_ponto_racional_exato(self):
        r = intersecao((0, 0), (3, 1), (0, 1), (3, 0))
        self.assertEqual(r, (Fraction(3, 2), Fraction(1, 2)))

    def test_disjuntos(self):
        self.assertFalse(segmentos_se_cruzam((0, 0), (1, 1), (2, 2), (3, 3)))
        self.assertIsNone(intersecao((0, 0), (1, 0), (0, 1), (1, 1)))
        self.assertIsNone(intersecao((0, 0), (1, 1), (3, 0), (0, 3.5)))

    def test_toque_em_extremidade(self):
        self.assertEqual(intersecao((0, 0), (2, 2), (2, 2), (4, 0)), (2, 2))
        self.assertEqual(intersecao((0, 0), (4, 0), (2, 0), (2, 5)), (2, 0))

    def test_colineares_sobrepostos(self):
        r = intersecao((0, 0), (4, 0), (2, 0), (6, 0))
        self.assertEqual(r, ((2, 0), (4, 0)))

    def test_colineares_tocando_em_ponto(self):
        self.assertEqual(intersecao((0, 0), (2, 0), (2, 0), (5, 0)), (2, 0))

    def test_colineares_disjuntos(self):
        self.assertIsNone(intersecao((0, 0), (1, 0), (2, 0), (3, 0)))

    def test_paralelos(self):
        self.assertIsNone(intersecao((0, 0), (4, 0), (0, 1), (4, 1)))


if __name__ == "__main__":
    unittest.main()
