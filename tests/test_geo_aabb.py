import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_aabb import AABB


class TestAABB(unittest.TestCase):
    def test_de_pontos(self):
        b = AABB.de_pontos([(1, 5), (-2, 3), (4, -1)])
        self.assertEqual(b, AABB(-2, -1, 4, 5))
        self.assertEqual((b.largura, b.altura, b.area), (6, 6, 36))
        self.assertEqual(b.centro, (1, 2))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            AABB(2, 0, 1, 1)
        with self.assertRaises(ValueError):
            AABB.de_pontos([])

    def test_ponto_unico_degenerado(self):
        b = AABB.de_pontos([(3, 3)])
        self.assertEqual(b.area, 0)
        self.assertTrue(b.contem_ponto((3, 3)))

    def test_contem(self):
        b = AABB(0, 0, 10, 10)
        self.assertTrue(b.contem_ponto((0, 10)))
        self.assertFalse(b.contem_ponto((10.01, 5)))
        self.assertTrue(b.contem(AABB(2, 2, 3, 3)))
        self.assertTrue(b.contem(b))
        self.assertFalse(b.contem(AABB(5, 5, 11, 6)))

    def test_intersecta_inclui_encostar(self):
        a = AABB(0, 0, 2, 2)
        self.assertTrue(a.intersecta(AABB(1, 1, 3, 3)))
        self.assertTrue(a.intersecta(AABB(2, 2, 4, 4)))  # só o canto
        self.assertTrue(a.intersecta(AABB(2, 0, 4, 2)))  # aresta
        self.assertFalse(a.intersecta(AABB(2.1, 0, 4, 2)))
        self.assertFalse(a.intersecta(AABB(0, 3, 2, 4)))

    def test_intersecao_e_uniao(self):
        a, b = AABB(0, 0, 4, 4), AABB(2, 1, 6, 3)
        self.assertEqual(a.intersecao(b), AABB(2, 1, 4, 3))
        self.assertEqual(a.uniao(b), AABB(0, 0, 6, 4))
        self.assertIsNone(a.intersecao(AABB(5, 5, 6, 6)))
        self.assertEqual(a.intersecao(AABB(4, 0, 5, 4)), AABB(4, 0, 4, 4))

    def test_expandir_e_distancia(self):
        b = AABB(0, 0, 2, 2)
        self.assertEqual(b.expandir(1), AABB(-1, -1, 3, 3))
        self.assertEqual(b.distancia_ao_ponto((1, 1)), 0)
        self.assertEqual(b.distancia_ao_ponto((5, 1)), 3)
        self.assertEqual(b.distancia_ao_ponto((5, 6)), 5)

    def test_segmento(self):
        b = AABB(0, 0, 4, 4)
        self.assertTrue(b.intersecta_segmento((-1, 2), (5, 2)))  # atravessa
        self.assertTrue(b.intersecta_segmento((1, 1), (2, 2)))  # dentro
        self.assertTrue(b.intersecta_segmento((-1, -1), (0, 0)))  # toca o canto
        self.assertFalse(b.intersecta_segmento((-2, 5), (5, 6)))
        self.assertFalse(b.intersecta_segmento((5, 0), (5, 4)))  # paralelo fora
        self.assertTrue(b.intersecta_segmento((4, -3), (4, 7)))  # sobre a aresta
        self.assertFalse(b.intersecta_segmento((-3, 5), (-1, 7)))
        self.assertTrue(b.intersecta_segmento((-1, 3), (3, 7)))  # roça exatamente o canto
        self.assertFalse(b.intersecta_segmento((-1, 4), (2, 7)))  # passa rente, por fora


if __name__ == "__main__":
    unittest.main()
