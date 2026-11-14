import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from potencia_rapida import potencia_rapida


class TestPotenciaRapida(unittest.TestCase):
    def test_basico(self):
        self.assertEqual(potencia_rapida(2, 10), 1024)

    def test_expoente_zero(self):
        self.assertEqual(potencia_rapida(5, 0), 1)
        self.assertEqual(potencia_rapida(0, 0), 1)

    def test_base_zero_e_negativa(self):
        self.assertEqual(potencia_rapida(0, 5), 0)
        self.assertEqual(potencia_rapida(-2, 3), -8)
        self.assertEqual(potencia_rapida(-2, 4), 16)

    def test_modulo(self):
        self.assertEqual(potencia_rapida(3, 200, 13), pow(3, 200, 13))
        self.assertEqual(potencia_rapida(7, 0, 1), 0)
        self.assertEqual(potencia_rapida(2, 10, 1000), 24)

    def test_expoente_grande(self):
        self.assertEqual(potencia_rapida(2, 100), 2 ** 100)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            potencia_rapida(2, -1)
        with self.assertRaises(ValueError):
            potencia_rapida(2, 3, 0)


if __name__ == "__main__":
    unittest.main()
