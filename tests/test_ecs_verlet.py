import sys
import unittest
from math import hypot
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_verlet import SistemaVerlet


class TestVerlet(unittest.TestCase):
    def test_queda_livre_discreta(self):
        s = SistemaVerlet(gravidade=(0, 10))
        i = s.adicionar_ponto(0, 0)
        s.passo(1.0)
        s.passo(1.0)
        # Verlet: y1 = 10, y2 = 2*10 - 0 + 10 = 30
        self.assertEqual(s.pontos[i].y, 30)
        self.assertEqual(s.velocidade(i), (0, 20))

    def test_ponto_fixo_nao_move(self):
        s = SistemaVerlet()
        i = s.adicionar_ponto(3, 4, fixo=True)
        s.passo(0.1)
        self.assertEqual((s.pontos[i].x, s.pontos[i].y), (3, 4))

    def test_pendulo_mantem_comprimento(self):
        s = SistemaVerlet(gravidade=(0, 9.8))
        a = s.adicionar_ponto(0, 0, fixo=True)
        b = s.adicionar_ponto(5, 0)
        s.ligar(a, b)
        for _ in range(300):
            s.passo(1 / 60, iteracoes=20)
        p = s.pontos[b]
        self.assertAlmostEqual(hypot(p.x, p.y), 5.0, delta=0.05)
        self.assertGreater(p.y, 0)

    def test_restricao_corrige_distancia_inicial(self):
        s = SistemaVerlet(gravidade=(0, 0))
        a = s.adicionar_ponto(0, 0)
        b = s.adicionar_ponto(10, 0)
        s.ligar(a, b, comprimento=4)
        for _ in range(30):
            s.passo(0.1, iteracoes=4)
        pa, pb = s.pontos
        self.assertAlmostEqual(hypot(pb.x - pa.x, pb.y - pa.y), 4.0, places=3)
        # simétrico: o centro de massa se conserva
        self.assertAlmostEqual((pa.x + pb.x) / 2, 5.0, places=6)

    def test_corda_pendura(self):
        s = SistemaVerlet()
        ids = [s.adicionar_ponto(i * 1.0, 0, fixo=(i == 0)) for i in range(6)]
        for u, v in zip(ids, ids[1:]):
            s.ligar(u, v)
        for _ in range(600):
            s.passo(1 / 60, iteracoes=30)
        ponta = s.pontos[-1]
        self.assertGreater(ponta.y, 3.5)

    def test_pontos_coincidentes_ignorados(self):
        s = SistemaVerlet(gravidade=(0, 0))
        a, b = s.adicionar_ponto(1, 1), s.adicionar_ponto(1, 1)
        s.ligar(a, b, comprimento=2)
        s.passo(0.1)
        self.assertEqual((s.pontos[a].x, s.pontos[b].x), (1, 1))


if __name__ == "__main__":
    unittest.main()
