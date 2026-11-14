import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_aabb import AABB
from geo_quadtree import Quadtree


class TestQuadtree(unittest.TestCase):
    def setUp(self):
        self.q = Quadtree(AABB(0, 0, 100, 100), capacidade=2)

    def test_vazio(self):
        self.assertEqual(len(self.q), 0)
        self.assertEqual(self.q.buscar(AABB(0, 0, 100, 100)), [])
        self.assertIsNone(self.q.mais_proximo((5, 5)))

    def test_inserir_fora_rejeita(self):
        self.assertFalse(self.q.inserir((101, 5)))
        self.assertTrue(self.q.inserir((100, 100)))
        self.assertEqual(len(self.q), 1)

    def test_busca_retangulo(self):
        pts = [(10, 10), (20, 20), (80, 80), (50, 50), (51, 51), (49, 10)]
        for p in pts:
            self.q.inserir(p)
        self.assertEqual(sorted(self.q.buscar(AABB(0, 0, 50, 50))), [(10, 10), (20, 20), (49, 10), (50, 50)])
        self.assertEqual(self.q.buscar(AABB(60, 0, 70, 10)), [])
        self.assertEqual(len(self.q.buscar(AABB(0, 0, 100, 100))), 6)

    def test_pontos_repetidos_nao_estouram_recursao(self):
        for _ in range(50):
            self.q.inserir((7, 7))
        self.assertEqual(len(self.q), 50)
        self.assertEqual(len(self.q.buscar(AABB(7, 7, 7, 7))), 50)

    def test_mais_proximo(self):
        for p in [(10, 10), (90, 90), (50, 52)]:
            self.q.inserir(p)
        self.assertEqual(self.q.mais_proximo((52, 50)), (50, 52))
        self.assertEqual(self.q.mais_proximo((100, 100)), (90, 90))

    def test_capacidade_invalida(self):
        with self.assertRaises(ValueError):
            Quadtree(AABB(0, 0, 1, 1), capacidade=0)

    def test_aleatorio_contra_forca_bruta(self):
        rng = random.Random(4)
        pts = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(300)]
        for p in pts:
            self.q.inserir(p)
        self.assertEqual(len(self.q), 300)
        for _ in range(30):
            x, y = rng.uniform(0, 100), rng.uniform(0, 100)
            area = AABB(x, y, x + 20, y + 15)
            esperado = sorted(p for p in pts if area.contem_ponto(p))
            self.assertEqual(sorted(self.q.buscar(area)), esperado)
            alvo = (rng.uniform(-10, 110), rng.uniform(-10, 110))
            self.assertEqual(math.dist(self.q.mais_proximo(alvo), alvo), min(math.dist(p, alvo) for p in pts))


if __name__ == "__main__":
    unittest.main()
