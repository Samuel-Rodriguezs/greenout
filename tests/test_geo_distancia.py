import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_distancia import (
    distancia,
    distancia_ponto_reta,
    distancia_ponto_segmento,
    distancia_segmentos,
    ponto_mais_proximo_no_segmento,
)


class TestDistancia(unittest.TestCase):
    def test_distancia_basica(self):
        self.assertEqual(distancia((0, 0), (3, 4)), 5)

    def test_ponto_reta(self):
        self.assertAlmostEqual(distancia_ponto_reta((0, 3), (-5, 0), (5, 0)), 3)
        # fora do segmento mas a reta ainda está a 3
        self.assertAlmostEqual(distancia_ponto_reta((100, 3), (0, 0), (1, 0)), 3)
        self.assertAlmostEqual(distancia_ponto_reta((1, 0), (0, 0), (1, 1)), math.sqrt(2) / 2)

    def test_reta_degenerada(self):
        self.assertEqual(distancia_ponto_reta((3, 4), (0, 0), (0, 0)), 5)

    def test_segmento_projecao_interna(self):
        self.assertEqual(distancia_ponto_segmento((2, 5), (0, 0), (4, 0)), 5)
        self.assertEqual(ponto_mais_proximo_no_segmento((2, 5), (0, 0), (4, 0)), (2, 0))

    def test_segmento_extremidades(self):
        self.assertEqual(distancia_ponto_segmento((7, 4), (0, 0), (4, 0)), 5)
        self.assertEqual(ponto_mais_proximo_no_segmento((-3, 1), (0, 0), (4, 0)), (0, 0))

    def test_segmento_degenerado(self):
        self.assertEqual(distancia_ponto_segmento((3, 4), (0, 0), (0, 0)), 5)

    def test_ponto_sobre_segmento(self):
        self.assertEqual(distancia_ponto_segmento((2, 0), (0, 0), (4, 0)), 0)

    def test_entre_segmentos(self):
        self.assertEqual(distancia_segmentos((0, 0), (4, 4), (0, 4), (4, 0)), 0)
        self.assertEqual(distancia_segmentos((0, 0), (1, 0), (0, 2), (1, 2)), 2)
        self.assertEqual(distancia_segmentos((0, 0), (1, 0), (4, 4), (4, 0)), 3)


if __name__ == "__main__":
    unittest.main()
