import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_circulos import Circulo, circulo_circulo, circulo_reta, circulo_segmento, tangentes_de_ponto


def proximos(testcase, obtido, esperado):
    testcase.assertEqual(len(obtido), len(esperado), obtido)
    for o, e in zip(sorted(obtido), sorted(esperado)):
        testcase.assertAlmostEqual(o[0], e[0])
        testcase.assertAlmostEqual(o[1], e[1])


class TestCirculos(unittest.TestCase):
    def test_dois_pontos(self):
        r = circulo_circulo(Circulo(0, 0, 5), Circulo(6, 0, 5))
        proximos(self, r, [(3, -4), (3, 4)])

    def test_tangente_externa_e_interna(self):
        proximos(self, circulo_circulo(Circulo(0, 0, 1), Circulo(2, 0, 1)), [(1, 0)])
        proximos(self, circulo_circulo(Circulo(0, 0, 3), Circulo(1, 0, 2)), [(3, 0)])

    def test_sem_interseccao(self):
        self.assertEqual(circulo_circulo(Circulo(0, 0, 1), Circulo(5, 0, 1)), [])  # longe
        self.assertEqual(circulo_circulo(Circulo(0, 0, 5), Circulo(1, 0, 1)), [])  # contido
        self.assertEqual(circulo_circulo(Circulo(0, 0, 5), Circulo(0, 0, 1)), [])  # concêntrico

    def test_coincidentes(self):
        with self.assertRaises(ValueError):
            circulo_circulo(Circulo(1, 1, 2), Circulo(1, 1, 2))

    def test_raio_negativo(self):
        with self.assertRaises(ValueError):
            Circulo(0, 0, -1)

    def test_reta_secante_tangente_fora(self):
        c = Circulo(0, 0, 5)
        proximos(self, circulo_reta(c, (-10, 3), (10, 3)), [(-4, 3), (4, 3)])
        proximos(self, circulo_reta(c, (-10, 5), (10, 5)), [(0, 5)])
        self.assertEqual(circulo_reta(c, (-10, 6), (10, 6)), [])

    def test_reta_vertical_e_degenerada(self):
        proximos(self, circulo_reta(Circulo(0, 0, 5), (3, 0), (3, 1)), [(3, -4), (3, 4)])
        with self.assertRaises(ValueError):
            circulo_reta(Circulo(0, 0, 1), (1, 1), (1, 1))

    def test_segmento_recorta(self):
        c = Circulo(0, 0, 5)
        proximos(self, circulo_segmento(c, (0, 0), (10, 0)), [(5, 0)])
        proximos(self, circulo_segmento(c, (-10, 0), (10, 0)), [(-5, 0), (5, 0)])
        self.assertEqual(circulo_segmento(c, (6, 0), (10, 0)), [])
        self.assertEqual(circulo_segmento(c, (-1, 0), (1, 0)), [])

    def test_tangentes(self):
        r = tangentes_de_ponto(Circulo(0, 0, 3), (5, 0))
        self.assertEqual(len(r), 2)
        for x, y in r:
            self.assertAlmostEqual(math.hypot(x, y), 3)
            # raio perpendicular à tangente: (t - c) . (t - p) = 0
            self.assertAlmostEqual(x * (x - 5) + y * y, 0)
        self.assertEqual(tangentes_de_ponto(Circulo(0, 0, 3), (1, 0)), [])
        self.assertEqual(tangentes_de_ponto(Circulo(0, 0, 3), (3, 0)), [(3, 0)])


if __name__ == "__main__":
    unittest.main()
