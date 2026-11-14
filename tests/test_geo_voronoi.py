import random
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_poligono_area import area
from geo_voronoi import celulas_voronoi, sitio_mais_proximo

CAIXA = (0, 0, 10, 10)


class TestVoronoi(unittest.TestCase):
    def test_dois_sitios_dividem_ao_meio(self):
        c = celulas_voronoi([(2, 5), (8, 5)], CAIXA)
        self.assertEqual(area(c[0]), 50)
        self.assertEqual(area(c[1]), 50)
        self.assertEqual(max(p[0] for p in c[0]), 5)

    def test_um_sitio_ocupa_caixa(self):
        c = celulas_voronoi([(3, 3)], CAIXA)
        self.assertEqual(area(c[0]), 100)

    def test_quatro_sitios_quadrantes(self):
        c = celulas_voronoi([(2, 2), (8, 2), (2, 8), (8, 8)], CAIXA)
        self.assertEqual([area(x) for x in c], [25, 25, 25, 25])

    def test_areas_somam_caixa(self):
        rng = random.Random(5)
        sitios = list({(rng.randint(0, 10), rng.randint(0, 10)) for _ in range(8)})
        c = celulas_voronoi(sitios, CAIXA)
        self.assertEqual(sum((area(x) for x in c), Fraction(0)), 100)

    def test_pontos_da_celula_estao_mais_perto_do_sitio(self):
        sitios = [(1, 1), (9, 2), (5, 8), (3, 5)]
        celulas = celulas_voronoi(sitios, CAIXA)
        for i, cel in enumerate(celulas):
            for v in cel:
                d = (v[0] - sitios[i][0]) ** 2 + (v[1] - sitios[i][1]) ** 2
                for j, t in enumerate(sitios):
                    self.assertLessEqual(d, (v[0] - t[0]) ** 2 + (v[1] - t[1]) ** 2)

    def test_sitio_fora_da_caixa_pode_ficar_vazio(self):
        c = celulas_voronoi([(5, 5), (1000, 1000)], CAIXA)
        self.assertEqual(area(c[0]), 100)
        self.assertEqual(c[1], [])

    def test_erros(self):
        with self.assertRaises(ValueError):
            celulas_voronoi([(1, 1), (1, 1)], CAIXA)
        with self.assertRaises(ValueError):
            celulas_voronoi([(1, 1)], (0, 0, 0, 5))
        with self.assertRaises(ValueError):
            sitio_mais_proximo((0, 0), [])

    def test_sitio_mais_proximo(self):
        s = [(0, 0), (10, 0), (5, 9)]
        self.assertEqual(sitio_mais_proximo((1, 1), s), 0)
        self.assertEqual(sitio_mais_proximo((9, 1), s), 1)
        self.assertEqual(sitio_mais_proximo((5, 5), s), 2)
        self.assertEqual(sitio_mais_proximo((5, 0), s), 0)  # empate: menor índice


if __name__ == "__main__":
    unittest.main()
