import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_orientacao import colineares, no_segmento, orientacao, sentido_poligono


class TestOrientacao(unittest.TestCase):
    def test_sentidos(self):
        self.assertEqual(orientacao((0, 0), (1, 0), (0, 1)), 1)
        self.assertEqual(orientacao((0, 0), (0, 1), (1, 0)), -1)

    def test_colinear(self):
        self.assertTrue(colineares((0, 0), (1, 1), (5, 5)))
        self.assertTrue(colineares((1, 1), (1, 1), (2, 3)))  # degenerado

    def test_exatidao_com_decimais(self):
        self.assertEqual(orientacao((0, 0), (0.5, 0.5), (1, 1)), 0)

    def test_no_segmento(self):
        self.assertTrue(no_segmento((0, 0), (4, 4), (2, 2)))
        self.assertTrue(no_segmento((0, 0), (4, 4), (4, 4)))
        self.assertFalse(no_segmento((0, 0), (4, 4), (5, 5)))
        self.assertFalse(no_segmento((0, 0), (4, 4), (2, 3)))

    def test_sentido_poligono(self):
        quadrado = [(0, 0), (2, 0), (2, 2), (0, 2)]
        self.assertEqual(sentido_poligono(quadrado), 1)
        self.assertEqual(sentido_poligono(quadrado[::-1]), -1)
        self.assertEqual(sentido_poligono([(0, 0), (1, 1), (2, 2)]), 0)
        self.assertEqual(sentido_poligono([(0, 0), (1, 1)]), 0)


if __name__ == "__main__":
    unittest.main()
