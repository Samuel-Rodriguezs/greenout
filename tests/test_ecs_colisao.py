import sys
import unittest
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_colisao import AABB, Circulo, aabb_aabb, mtv_aabb, mtv_circulo_aabb, mtv_circulos, resolver


class TestColisao(unittest.TestCase):
    def test_aabb_sobreposicao_e_toque(self):
        self.assertTrue(aabb_aabb(AABB(0, 0, 10, 10), AABB(5, 5, 10, 10)))
        self.assertFalse(aabb_aabb(AABB(0, 0, 10, 10), AABB(10, 0, 5, 5)))
        self.assertFalse(aabb_aabb(AABB(0, 0, 1, 1), AABB(5, 5, 1, 1)))

    def test_mtv_aabb_menor_eixo(self):
        self.assertEqual(mtv_aabb(AABB(0, 0, 10, 10), AABB(8, 0, 10, 10)), (-2, 0.0))
        self.assertEqual(mtv_aabb(AABB(8, 0, 10, 10), AABB(0, 0, 10, 10)), (2, 0.0))
        self.assertEqual(mtv_aabb(AABB(0, 0, 10, 10), AABB(0, 9, 10, 10)), (0.0, -1))
        self.assertIsNone(mtv_aabb(AABB(0, 0, 1, 1), AABB(1, 0, 1, 1)))

    def test_mtv_realmente_separa(self):
        a, b = AABB(0, 0, 10, 10), AABB(7, 4, 10, 10)
        dx, dy = mtv_aabb(a, b)
        a.x += dx
        a.y += dy
        self.assertFalse(aabb_aabb(a, b))

    def test_circulos(self):
        self.assertIsNone(mtv_circulos(Circulo(0, 0, 1), Circulo(2, 0, 1)))
        mtv = mtv_circulos(Circulo(0, 0, 2), Circulo(3, 0, 2))
        self.assertAlmostEqual(mtv[0], -1.0)
        self.assertAlmostEqual(mtv[1], 0.0)
        self.assertEqual(mtv_circulos(Circulo(1, 1, 1), Circulo(1, 1, 2)), (3, 0.0))

    def test_circulo_aabb_lateral_e_canto(self):
        caixa = AABB(0, 0, 10, 10)
        mtv = mtv_circulo_aabb(Circulo(12, 5, 3), caixa)
        self.assertAlmostEqual(mtv[0], 1.0)
        self.assertAlmostEqual(mtv[1], 0.0)
        mtv = mtv_circulo_aabb(Circulo(11, 11, 2), caixa)
        self.assertAlmostEqual(mtv[0], (2 - sqrt(2)) / sqrt(2))
        self.assertAlmostEqual(mtv[0], mtv[1])
        self.assertIsNone(mtv_circulo_aabb(Circulo(14, 5, 3), caixa))

    def test_circulo_centro_dentro(self):
        mtv = mtv_circulo_aabb(Circulo(9, 5, 1), AABB(0, 0, 10, 10))
        self.assertEqual(mtv, (2.0, 0.0))

    def test_resolver_massas(self):
        a, b = AABB(0, 0, 10, 10), AABB(8, 0, 10, 10)
        self.assertTrue(resolver(a, b, 1, 1))
        self.assertEqual((a.x, b.x), (-1, 9))
        a, b = AABB(0, 0, 10, 10), AABB(8, 0, 10, 10)
        resolver(a, b, 1, float("inf"))
        self.assertEqual((a.x, b.x), (-2, 8))
        self.assertFalse(resolver(AABB(0, 0, 1, 1), AABB(5, 5, 1, 1)))
        self.assertTrue(resolver(AABB(0, 0, 10, 10), AABB(8, 0, 10, 10), float("inf"), float("inf")))


if __name__ == "__main__":
    unittest.main()
