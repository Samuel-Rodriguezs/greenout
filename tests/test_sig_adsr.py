import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_adsr as a


class TestADSR(unittest.TestCase):
    def setUp(self):
        self.e = a.ADSR(ataque=0.1, decaimento=0.2, sustentacao=0.5, liberacao=0.4)

    def test_fases(self):
        self.assertAlmostEqual(self.e.nivel(0.0, 1.0), 0.0)
        self.assertAlmostEqual(self.e.nivel(0.05, 1.0), 0.5)
        self.assertAlmostEqual(self.e.nivel(0.1, 1.0), 1.0)
        self.assertAlmostEqual(self.e.nivel(0.2, 1.0), 0.75)
        self.assertAlmostEqual(self.e.nivel(0.3, 1.0), 0.5)
        self.assertAlmostEqual(self.e.nivel(0.9, 1.0), 0.5)

    def test_liberacao(self):
        self.assertAlmostEqual(self.e.nivel(1.2, 1.0), 0.25)
        self.assertAlmostEqual(self.e.nivel(1.4, 1.0), 0.0)
        self.assertEqual(self.e.nivel(5.0, 1.0), 0.0)

    def test_soltura_durante_ataque(self):
        self.assertAlmostEqual(self.e.nivel(0.05, 0.05), 0.5)
        self.assertAlmostEqual(self.e.nivel(0.25, 0.05), 0.25)

    def test_tempo_negativo(self):
        self.assertEqual(self.e.nivel(-1, 1.0), 0.0)

    def test_amostras(self):
        env = self.e.amostras(100, 1.0)
        self.assertEqual(len(env), 140)
        self.assertAlmostEqual(max(env), 1.0, places=6)
        self.assertEqual(env[0], 0.0)

    def test_ataque_zero(self):
        e = a.ADSR(0, 0.1, 0.5, 0)
        self.assertEqual(e.nivel(0.0, 1.0), 1.0)
        self.assertEqual(e.nivel(1.0, 1.0), 0.0)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            a.ADSR(-1, 0, 0.5, 0)
        with self.assertRaises(ValueError):
            a.ADSR(0, 0, 1.5, 0)
        with self.assertRaises(ValueError):
            self.e.amostras(0, 1.0)

    def test_aplicar(self):
        self.assertEqual(a.aplicar([2, 2, 2], [0, 0.5]), [0, 1])


if __name__ == "__main__":
    unittest.main()
