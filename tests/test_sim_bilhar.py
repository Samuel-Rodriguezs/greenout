import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_bilhar import Bola, Mesa, colidem, resolver_colisao


class TestBilhar(unittest.TestCase):
    def test_colisao_frontal_massas_iguais_troca_velocidades(self):
        a = Bola(0, 0, 3, 0)
        b = Bola(1.9, 0, 0, 0)
        self.assertTrue(colidem(a, b))
        resolver_colisao(a, b)
        self.assertAlmostEqual(a.vx, 0)
        self.assertAlmostEqual(b.vx, 3)

    def test_conservacao(self):
        a = Bola(0, 0, 2, 1, massa=2.0)
        b = Bola(1.5, 1.0, -1, 0.5, massa=3.0)
        p0 = (a.massa * a.vx + b.massa * b.vx, a.massa * a.vy + b.massa * b.vy)
        e0 = sum(0.5 * x.massa * (x.vx ** 2 + x.vy ** 2) for x in (a, b))
        resolver_colisao(a, b)
        p1 = (a.massa * a.vx + b.massa * b.vx, a.massa * a.vy + b.massa * b.vy)
        e1 = sum(0.5 * x.massa * (x.vx ** 2 + x.vy ** 2) for x in (a, b))
        self.assertAlmostEqual(p0[0], p1[0])
        self.assertAlmostEqual(p0[1], p1[1])
        self.assertAlmostEqual(e0, e1)

    def test_massa_maior_quase_nao_muda(self):
        pesada = Bola(0, 0, 0, 0, massa=1000.0)
        leve = Bola(1.9, 0, -5, 0)
        resolver_colisao(pesada, leve)
        self.assertGreater(leve.vx, 4.9)
        self.assertLess(abs(pesada.vx), 0.02)

    def test_afastando_nao_colide(self):
        a = Bola(0, 0, -1, 0)
        b = Bola(1.5, 0, 1, 0)
        resolver_colisao(a, b)
        self.assertEqual((a.vx, b.vx), (-1, 1))

    def test_paredes(self):
        m = Mesa(10, 10, [Bola(9.5, 5, 4, 0)])
        m.passo(0.5)
        self.assertLess(m.bolas[0].vx, 0)
        self.assertLessEqual(m.bolas[0].x + 1, 10)

    def test_mesa_conserva_energia_sem_atrito(self):
        m = Mesa(20, 20, [Bola(5, 5, 3, 2), Bola(10, 10, -2, 1), Bola(15, 5, 0, -3)])
        e0 = m.energia()
        for _ in range(500):
            m.passo(0.01)
        self.assertAlmostEqual(m.energia(), e0, delta=1e-6 * e0 + 1e-6)

    def test_atrito_para_as_bolas(self):
        m = Mesa(20, 20, [Bola(5, 5, 3, 2)])
        for _ in range(2000):
            m.passo(0.01, atrito=1.0)
        self.assertLess(m.energia(), 0.01)

    def test_mesma_posicao(self):
        with self.assertRaises(ValueError):
            resolver_colisao(Bola(0, 0), Bola(0, 0))


if __name__ == "__main__":
    unittest.main()
