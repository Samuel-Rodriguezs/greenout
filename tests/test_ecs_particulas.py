import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_particulas import Particula, passo, quicar_no_chao, simular


class TestParticulas(unittest.TestCase):
    def test_semi_implicito_usa_velocidade_nova(self):
        p = Particula(0, 0)
        passo(p, 1.0, gravidade=(0, 10))
        # v = 10 e x usa v já atualizada (Euler explícito daria y = 0)
        self.assertEqual((p.vy, p.y), (10, 10))

    def test_sem_gravidade_movimento_uniforme(self):
        p = Particula(0, 0, vx=2, vy=-1)
        simular(p, 10, 0.1, gravidade=(0, 0))
        self.assertAlmostEqual(p.x, 2.0)
        self.assertAlmostEqual(p.y, -1.0)

    def test_forca_e_massa(self):
        p = Particula(0, 0, massa=2.0)
        p.aplicar_forca(10, 0)
        passo(p, 1.0, gravidade=(0, 0))
        self.assertEqual(p.vx, 5)
        self.assertEqual((p.fx, p.fy), (0, 0))

    def test_atrito_reduz_velocidade_e_converge(self):
        p = Particula(0, 0, vx=10)
        passo(p, 0.1, gravidade=(0, 0), atrito_linear=5)
        self.assertAlmostEqual(p.vx, 10 / 1.5)
        simular(p, 1000, 0.1, gravidade=(0, 0), atrito_linear=5)
        self.assertLess(p.vx, 1e-6)
        self.assertGreater(p.vx, 0)

    def test_velocidade_terminal(self):
        p = Particula(0, 0)
        simular(p, 5000, 0.01, gravidade=(0, 10), atrito_linear=2)
        self.assertAlmostEqual(p.vy, 10 / 2, places=1)

    def test_quicar(self):
        p = Particula(0, 11, vy=10, vx=4)
        self.assertTrue(quicar_no_chao(p, 10, restituicao=0.5, atrito_solo=0.25))
        self.assertEqual((p.y, p.vy, p.vx), (10, -5, 3))
        self.assertFalse(quicar_no_chao(p, 10))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            passo(Particula(0, 0), -1)
        with self.assertRaises(ValueError):
            passo(Particula(0, 0, massa=0), 1)

    def test_deterministico(self):
        a = simular(Particula(0, 0, vx=3, vy=-8), 50, 0.02)
        b = simular(Particula(0, 0, vx=3, vy=-8), 50, 0.02)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
