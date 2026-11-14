import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_ondas as o


class TestOndas(unittest.TestCase):
    def test_seno_quarto_de_ciclo(self):
        x = o.senoidal(1, 4, 4)
        for a, b in zip(x, [0, 1, 0, -1]):
            self.assertAlmostEqual(a, b, places=9)

    def test_seno_fase(self):
        self.assertAlmostEqual(o.senoidal(1, 4, 1, fase=0.25)[0], 1.0)

    def test_quadrada(self):
        self.assertEqual(o.quadrada(1, 4, 4, amp=2), [2, 2, -2, -2])

    def test_quadrada_ciclo_invalido(self):
        with self.assertRaises(ValueError):
            o.quadrada(1, 4, 4, ciclo=1.0)

    def test_dente_de_serra(self):
        self.assertEqual(o.dente_de_serra(1, 4, 4), [-1, -0.5, 0, 0.5])

    def test_triangular(self):
        self.assertEqual(o.triangular(1, 4, 4), [-1, 0, 1, 0])

    def test_ruido_seed(self):
        a = o.ruido_branco(50, seed=3)
        self.assertEqual(a, o.ruido_branco(50, seed=3))
        self.assertNotEqual(a, o.ruido_branco(50, seed=4))
        self.assertTrue(all(-1 <= v <= 1 for v in a))

    def test_rms_seno(self):
        x = o.senoidal(10, 1000, 1000)
        self.assertAlmostEqual(o.rms(x), 1 / math.sqrt(2), places=6)

    def test_bordas(self):
        self.assertEqual(o.senoidal(1, 4, 0), [])
        self.assertEqual(o.rms([]), 0.0)
        with self.assertRaises(ValueError):
            o.senoidal(1, 0, 4)


if __name__ == "__main__":
    unittest.main()
