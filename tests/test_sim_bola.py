import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_bola import Bola, Caixa


class TestBola(unittest.TestCase):
    def test_queda_livre(self):
        c = Caixa(10, 100)
        b = Bola(5, 50, 0, 0)
        for _ in range(100):
            c.passo(b, 0.01)
        self.assertAlmostEqual(b.vy, -9.8, places=6)
        self.assertLess(b.y, 50)
        self.assertEqual(b.x, 5)

    def test_quica_no_chao(self):
        c = Caixa(10, 100, restituicao=0.5)
        b = Bola(5, 1, 0, -10)
        c.passo(b, 0.1)
        self.assertGreater(b.vy, 0)
        self.assertGreaterEqual(b.y - b.raio, 0)
        self.assertEqual(c.quicadas, 1)

    def test_paredes_laterais(self):
        c = Caixa(10, 100, gravidade=0, restituicao=1.0)
        b = Bola(9, 50, 5, 0)
        c.passo(b, 0.5)
        self.assertLess(b.vx, 0)
        self.assertLessEqual(b.x + b.raio, 10)
        b2 = Bola(1, 50, -5, 0)
        c.passo(b2, 0.5)
        self.assertGreater(b2.vx, 0)

    def test_restituicao_unitaria_conserva_energia_aprox(self):
        c = Caixa(10, 100, restituicao=1.0)
        b = Bola(5, 20, 1, 0)
        e0 = Caixa.energia(b, c.g)
        for _ in range(2000):
            c.passo(b, 0.001)
        self.assertAlmostEqual(Caixa.energia(b, c.g), e0, delta=0.05 * e0)

    def test_perda_de_energia_e_repouso(self):
        c = Caixa(10, 10, restituicao=0.6)
        b = Bola(5, 5, 0, 0)
        for _ in range(20000):
            c.passo(b, 0.002)
        self.assertLess(Caixa.energia(b, c.g), 0.2 * 9.8 * 5)
        self.assertGreater(c.quicadas, 3)

    def test_restituicao_invalida(self):
        with self.assertRaises(ValueError):
            Caixa(1, 1, restituicao=1.5)


if __name__ == "__main__":
    unittest.main()
