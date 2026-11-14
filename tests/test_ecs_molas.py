import sys
import unittest
from math import pi, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_molas import Corpo, Mola, energia, passo


class TestMolas(unittest.TestCase):
    def test_forca_hooke(self):
        a, b = Corpo(0, 0, fixo=True), Corpo(3, 0)
        m = Mola(a, b, repouso=1, k=10)
        self.assertEqual(m.forca_em_a(), (20.0, 0.0))  # estica 2 -> puxa a para b

    def test_comprimida_empurra(self):
        a, b = Corpo(0, 0), Corpo(0.5, 0)
        fx, _ = Mola(a, b, 1, 4).forca_em_a()
        self.assertEqual(fx, -2.0)

    def test_oscilacao_periodo(self):
        # massa 1, k = 4 pi^2 => periodo 1 s
        k = 4 * pi ** 2
        a, b = Corpo(0, 0, fixo=True), Corpo(1.5, 0)
        mola = Mola(a, b, repouso=1, k=k)
        dt, t = 0.0005, 0.0
        cruzamentos = []
        ant = 0.5
        while t < 3:
            passo([a, b], [mola], dt)
            t += dt
            atual = b.x - 1
            if ant > 0 >= atual:
                cruzamentos.append(t)
            ant = atual
        self.assertEqual(len(cruzamentos), 3)
        self.assertAlmostEqual(cruzamentos[1] - cruzamentos[0], 1.0, delta=0.01)

    def test_amortecimento_dissipa_energia(self):
        a, b = Corpo(0, 0, fixo=True), Corpo(2, 0)
        mola = Mola(a, b, 1, 20, amortecimento=2)
        e0 = energia([a, b], [mola])
        for _ in range(4000):
            passo([a, b], [mola], 0.005)
        self.assertLess(energia([a, b], [mola]), e0 * 1e-3)
        self.assertAlmostEqual(b.x, 1.0, places=2)

    def test_energia_quase_conservada_sem_amortecimento(self):
        a, b = Corpo(0, 0, fixo=True), Corpo(2, 0)
        mola = Mola(a, b, 1, 10)
        e0 = energia([a, b], [mola])
        for _ in range(2000):
            passo([a, b], [mola], 0.001)
        self.assertAlmostEqual(energia([a, b], [mola]), e0, delta=e0 * 0.01)

    def test_dois_corpos_conservam_momento(self):
        a, b = Corpo(0, 0, massa=1), Corpo(2, 0, massa=3)
        mola = Mola(a, b, 1, 5)
        for _ in range(100):
            passo([a, b], [mola], 0.01)
        self.assertAlmostEqual(a.vx * a.massa + b.vx * b.massa, 0.0)

    def test_gravidade_e_equilibrio(self):
        a, b = Corpo(0, 0, fixo=True), Corpo(0, 1)
        mola = Mola(a, b, 1, 10, amortecimento=3)
        for _ in range(5000):
            passo([a, b], [mola], 0.005, gravidade=(0, 10))
        self.assertAlmostEqual(b.y, 1 + 10 / 10, places=2)

    def test_diagonal(self):
        a, b = Corpo(0, 0), Corpo(3, 4)
        fx, fy = Mola(a, b, 3, 1).forca_em_a()
        self.assertAlmostEqual(fx, 2 * 0.6)
        self.assertAlmostEqual(fy, 2 * 0.8)
        self.assertAlmostEqual(sqrt(fx ** 2 + fy ** 2), 2.0)


if __name__ == "__main__":
    unittest.main()
