import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_boids import Boid, Bando


class TestBoids(unittest.TestCase):
    def test_determinismo(self):
        a = Bando(10, 50, 50, random.Random(1))
        b = Bando(10, 50, 50, random.Random(1))
        for _ in range(5):
            a.passo()
            b.passo()
        self.assertEqual(a.boids, b.boids)

    def test_velocidade_limitada_e_posicoes_na_caixa(self):
        bando = Bando(20, 30, 30, random.Random(2), vmax=1.5)
        for _ in range(50):
            bando.passo()
        for b in bando.boids:
            self.assertLessEqual(math.hypot(b.vx, b.vy), 1.5 + 1e-9)
            self.assertTrue(0 <= b.x < 30 and 0 <= b.y < 30)

    def test_alinhamento_aumenta(self):
        bando = Bando(30, 20, 20, random.Random(3), raio_visao=15)
        antes = bando.alinhamento()
        for _ in range(100):
            bando.passo(w_sep=0.01, w_ali=0.2, w_coe=0.001)
        self.assertGreater(bando.alinhamento(), antes)
        self.assertGreater(bando.alinhamento(), 0.9)

    def test_coesao_atrai(self):
        bando = Bando(0, 100, 100, random.Random(1))
        bando.boids = [Boid(10, 10, 0, 0), Boid(20, 10, 0, 0)]
        bando.passo(w_sep=0, w_ali=0, w_coe=0.1)
        self.assertGreater(bando.boids[0].vx, 0)
        self.assertLess(bando.boids[1].vx, 0)

    def test_separacao_repele(self):
        bando = Bando(0, 100, 100, random.Random(1), raio_separacao=3)
        bando.boids = [Boid(10, 10, 0, 0), Boid(11, 10, 0, 0)]
        bando.passo(w_sep=0.5, w_ali=0, w_coe=0)
        self.assertLess(bando.boids[0].vx, 0)
        self.assertGreater(bando.boids[1].vx, 0)

    def test_isolado_nao_muda_velocidade(self):
        bando = Bando(0, 100, 100, random.Random(1), raio_visao=5)
        bando.boids = [Boid(10, 10, 1, 0), Boid(80, 80, 0, 1)]
        bando.passo()
        self.assertEqual((bando.boids[0].vx, bando.boids[0].vy), (1, 0))

    def test_alinhamento_vazio(self):
        self.assertEqual(Bando(0, 10, 10).alinhamento(), 0.0)


if __name__ == "__main__":
    unittest.main()
