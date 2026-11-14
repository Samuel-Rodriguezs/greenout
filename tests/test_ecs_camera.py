import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_camera import Camera


class TestCamera(unittest.TestCase):
    def test_centralizar(self):
        c = Camera(100, 60)
        c.centralizar(200, 100)
        self.assertEqual((c.x, c.y), (150, 70))
        self.assertEqual(c.centro, (200, 100))

    def test_seguir_converge(self):
        c = Camera(100, 60)
        for _ in range(300):
            c.seguir(500, 300, 1 / 60)
        self.assertAlmostEqual(c.centro[0], 500, delta=0.01)
        self.assertAlmostEqual(c.centro[1], 300, delta=0.01)

    def test_independente_de_taxa_de_quadros(self):
        a, b = Camera(100, 60), Camera(100, 60)
        a.seguir(400, 0, 0.5, velocidade=3)
        b.seguir(400, 0, 0.25, velocidade=3)
        b.seguir(400, 0, 0.25, velocidade=3)
        # alvo fixo: um passo de dt equivale a dois de dt/2
        self.assertAlmostEqual(a.x, b.x)

    def test_zona_morta(self):
        c = Camera(100, 60)
        c.centralizar(0, 0)
        c.seguir(10, 5, 1.0, zona_morta=(20, 20))
        self.assertEqual(c.centro, (0, 0))
        c.seguir(30, 0, 100.0, zona_morta=(20, 20))
        self.assertAlmostEqual(c.centro[0], 10.0)

    def test_limites(self):
        c = Camera(100, 60, limites=(0, 0, 400, 300))
        c.centralizar(0, 0)
        self.assertEqual((c.x, c.y), (0, 0))
        c.centralizar(1000, 1000)
        self.assertEqual((c.x, c.y), (300, 240))

    def test_mundo_menor_que_vista_centraliza(self):
        c = Camera(100, 60, limites=(0, 0, 40, 40))
        c.centralizar(500, 500)
        self.assertEqual((c.x, c.y), (-30, -10))

    def test_conversao_ida_e_volta(self):
        c = Camera(100, 60)
        c.centralizar(80, 90)
        sx, sy = c.mundo_para_tela(70, 95)
        self.assertEqual(c.tela_para_mundo(sx, sy), (70, 95))
        self.assertEqual((sx, sy), (70 - c.x, 95 - c.y))

    def test_visivel(self):
        c = Camera(100, 60)
        self.assertTrue(c.visivel(50, 50))
        self.assertTrue(c.visivel(-10, 0, 20, 5))
        self.assertFalse(c.visivel(101, 0))
        self.assertFalse(c.visivel(-30, 0, 20, 5))

    def test_tremor_deterministico_e_decai(self):
        def roda():
            c = Camera(100, 60, rng=random.Random(42))
            c.tremer(10, 1.0)
            return [(c.seguir(50, 30, 0.25), c.desloc_x, c.desloc_y)[1:] for _ in range(5)]
        a = roda()
        self.assertEqual(a, roda())
        self.assertNotEqual(a[0], (0.0, 0.0))
        self.assertEqual(a[3], (0.0, 0.0))  # dur 1.0, quarto passo zera amplitude
        self.assertEqual(a[4], (0.0, 0.0))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Camera(0, 10)
        with self.assertRaises(ValueError):
            Camera(10, 10).seguir(0, 0, -1)


if __name__ == "__main__":
    unittest.main()
