import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_tir import tir


class TestDomTir(unittest.TestCase):
    def test_simples(self):
        self.assertAlmostEqual(float(tir([-100, 110])), 0.10, places=8)

    def test_dois_fluxos(self):
        # 6x^2 + 6x - 10 = 0, x = 1/(1+r)
        self.assertAlmostEqual(float(tir([-1000, 600, 600])), 0.13066, delta=1e-4)

    def test_negativa(self):
        self.assertAlmostEqual(float(tir([-100, 90])), -0.10, places=8)

    def test_sem_troca_de_sinal(self):
        with self.assertRaises(ValueError):
            tir([100, 200])

    def test_poucos_fluxos(self):
        with self.assertRaises(ValueError):
            tir([-100])

    def test_intervalo_sem_raiz(self):
        with self.assertRaises(ValueError):
            tir([-100, 110], baixo="0.5", alto="1")


if __name__ == "__main__":
    unittest.main()
