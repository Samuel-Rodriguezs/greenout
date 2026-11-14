import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_ear_clipping import triangular
from geo_poligono_area import area

QUADRADO = [(0, 0), (4, 0), (4, 4), (0, 4)]
L = [(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]
SETA = [(0, 0), (4, 0), (4, 4), (2, 1), (0, 4)]  # côncavo


def soma_areas(tris):
    return sum((area(list(t)) for t in tris), Fraction(0))


class TestEarClipping(unittest.TestCase):
    def test_triangulo(self):
        t = triangular([(0, 0), (3, 0), (0, 3)])
        self.assertEqual(len(t), 1)

    def test_quadrado(self):
        t = triangular(QUADRADO)
        self.assertEqual(len(t), 2)
        self.assertEqual(soma_areas(t), 16)

    def test_concavos_preservam_area(self):
        for poli in (L, SETA):
            t = triangular(poli)
            self.assertEqual(len(t), len(poli) - 2)
            self.assertEqual(soma_areas(t), area(poli))

    def test_sentido_horario_aceito(self):
        t = triangular(L[::-1])
        self.assertEqual(soma_areas(t), 3)

    def test_triangulos_anti_horarios(self):
        from geo_orientacao import orientacao

        for tri in triangular(SETA):
            self.assertEqual(orientacao(*tri), 1)

    def test_vertice_colinear_descartado(self):
        t = triangular([(0, 0), (2, 0), (4, 0), (4, 4), (0, 4)])
        self.assertEqual(soma_areas(t), 16)
        self.assertLessEqual(len(t), 3)

    def test_triangulos_nao_contem_vertices_alheios(self):
        from geo_orientacao import orientacao

        poli = [(0, 0), (6, 0), (6, 6), (3, 2), (0, 6)]
        for a, b, c in triangular(poli):
            for q in poli:
                if q in (a, b, c):
                    continue
                dentro = (
                    orientacao(a, b, q) > 0 and orientacao(b, c, q) > 0 and orientacao(c, a, q) > 0
                )
                self.assertFalse(dentro)

    def test_degenerado(self):
        with self.assertRaises(ValueError):
            triangular([(0, 0), (1, 1), (2, 2)])
        with self.assertRaises(ValueError):
            triangular([(0, 0), (1, 0)])


if __name__ == "__main__":
    unittest.main()
