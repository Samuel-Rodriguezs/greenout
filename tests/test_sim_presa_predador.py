import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_presa_predador import equilibrio, passo_lv, simular_estocastico, simular_lv


class TestPresaPredador(unittest.TestCase):
    def test_equilibrio_estavel_no_ponto_fixo(self):
        x, y = equilibrio(1.0, 0.1, 0.075, 1.5)
        self.assertAlmostEqual(x, 20.0)
        self.assertAlmostEqual(y, 10.0)
        nx, ny = passo_lv(x, y, 1.0, 0.1, 0.075, 1.5)
        self.assertAlmostEqual(nx, x)
        self.assertAlmostEqual(ny, y)

    def test_sem_predadores_presas_crescem(self):
        hist = simular_lv(10, 0, 1000, dt=0.001)
        self.assertGreater(hist[-1][0], 10)
        self.assertEqual(hist[-1][1], 0)

    def test_sem_presas_predadores_morrem(self):
        hist = simular_lv(0, 10, 1000, dt=0.001)
        self.assertLess(hist[-1][1], 10)
        self.assertEqual(hist[-1][0], 0)

    def test_oscilacao(self):
        hist = simular_lv(40, 9, 30000, dt=0.001)
        presas = [p for p, _ in hist]
        self.assertGreater(max(presas), 40)
        self.assertLess(min(presas), 20)
        self.assertTrue(all(p >= 0 and q >= 0 for p, q in hist))

    def test_estocastico_deterministico(self):
        a = simular_estocastico(100, 10, 50, random.Random(1))
        b = simular_estocastico(100, 10, 50, random.Random(1))
        self.assertEqual(a, b)
        self.assertEqual(a[0], (100, 10))

    def test_estocastico_nao_negativo(self):
        hist = simular_estocastico(50, 20, 100, random.Random(2))
        self.assertTrue(all(p >= 0 and q >= 0 for p, q in hist))

    def test_estocastico_sem_predadores(self):
        hist = simular_estocastico(50, 0, 10, random.Random(3))
        self.assertGreater(hist[-1][0], 50)


if __name__ == "__main__":
    unittest.main()
