import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_reamostragem as r


class TestReamostragem(unittest.TestCase):
    def test_amostrar(self):
        x = r.amostrar(lambda t: 2 * t, 4, 1)
        self.assertEqual(x, [0, 0.5, 1.0, 1.5])
        self.assertEqual(r.amostrar(math.sin, 10, 0), [])
        with self.assertRaises(ValueError):
            r.amostrar(math.sin, 0, 1)

    def test_interpolar(self):
        x = [0, 10, 20]
        self.assertEqual(r.interpolar(x, 0.5), 5)
        self.assertEqual(r.interpolar(x, 1.25), 12.5)
        self.assertEqual(r.interpolar(x, -3), 0)
        self.assertEqual(r.interpolar(x, 9), 20)
        with self.assertRaises(ValueError):
            r.interpolar([], 0)

    def test_dobrar_taxa(self):
        self.assertEqual(r.reamostrar([0, 2, 4], 1, 2), [0, 1, 2, 3, 4, 4])

    def test_reduzir_taxa(self):
        self.assertEqual(r.reamostrar([0, 1, 2, 3], 2, 1), [0, 2])

    def test_mesma_taxa(self):
        x = [1.0, -2.0, 3.0]
        self.assertEqual(r.reamostrar(x, 8000, 8000), x)

    def test_rampa_preservada(self):
        x = [float(i) for i in range(100)]
        y = r.reamostrar(x, 100, 150)
        for k, v in enumerate(y[:-2]):
            self.assertAlmostEqual(v, k * 100 / 150)

    def test_vazio_e_invalido(self):
        self.assertEqual(r.reamostrar([], 1, 2), [])
        with self.assertRaises(ValueError):
            r.reamostrar([1], 0, 1)

    def test_decimar_e_zeros(self):
        self.assertEqual(r.decimar([1, 2, 3, 4, 5], 2), [1, 3, 5])
        self.assertEqual(r.inserir_zeros([1, 2], 3), [1, 0, 0, 2, 0, 0])
        with self.assertRaises(ValueError):
            r.decimar([1], 0)

    def test_aliasing(self):
        self.assertEqual(r.nyquist(44100), 22050)
        self.assertEqual(r.frequencia_aparente(300, 1000), 300)
        self.assertEqual(r.frequencia_aparente(700, 1000), 300)
        self.assertEqual(r.frequencia_aparente(1300, 1000), 300)
        self.assertEqual(r.frequencia_aparente(1000, 1000), 0)


if __name__ == "__main__":
    unittest.main()
