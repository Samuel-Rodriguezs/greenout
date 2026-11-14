import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_uniao_retangulos import area_soma_simples, area_sobreposta, area_uniao


def por_celulas(rects):
    cel = set()
    for x1, y1, x2, y2 in rects:
        for x in range(x1, x2):
            for y in range(y1, y2):
                cel.add((x, y))
    return len(cel)


class TestUniaoRetangulos(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(area_uniao([]), 0)

    def test_um(self):
        self.assertEqual(area_uniao([(0, 0, 3, 4)]), 12)

    def test_disjuntos(self):
        self.assertEqual(area_uniao([(0, 0, 1, 1), (5, 5, 7, 8)]), 7)

    def test_sobreposicao_parcial(self):
        self.assertEqual(area_uniao([(0, 0, 4, 4), (2, 2, 6, 6)]), 28)
        self.assertEqual(area_sobreposta([(0, 0, 4, 4), (2, 2, 6, 6)]), 4)

    def test_contido_e_identicos(self):
        self.assertEqual(area_uniao([(0, 0, 10, 10), (2, 2, 3, 3)]), 100)
        self.assertEqual(area_uniao([(0, 0, 2, 2)] * 3), 4)
        self.assertEqual(area_soma_simples([(0, 0, 2, 2)] * 3), 12)

    def test_encostados_nao_sobrepoem(self):
        self.assertEqual(area_uniao([(0, 0, 2, 2), (2, 0, 4, 2)]), 8)

    def test_degenerados_ignorados(self):
        self.assertEqual(area_uniao([(0, 0, 0, 5), (1, 1, 3, 3)]), 4)

    def test_cruz(self):
        self.assertEqual(area_uniao([(0, 1, 5, 2), (2, 0, 3, 5)]), 9)

    def test_invertido(self):
        with self.assertRaises(ValueError):
            area_uniao([(3, 0, 1, 1)])

    def test_decimais(self):
        self.assertAlmostEqual(area_uniao([(0, 0, 1.5, 1), (1, 0, 2.5, 1)]), 2.5)

    def test_aleatorio_contra_grade(self):
        rng = random.Random(6)
        for _ in range(60):
            rects = []
            for _ in range(rng.randint(1, 8)):
                x1, y1 = rng.randint(0, 9), rng.randint(0, 9)
                rects.append((x1, y1, x1 + rng.randint(1, 6), y1 + rng.randint(1, 6)))
            self.assertEqual(area_uniao(rects), por_celulas(rects), rects)


if __name__ == "__main__":
    unittest.main()
