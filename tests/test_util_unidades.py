import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_unidades import (celsius_para_fahrenheit, celsius_para_kelvin,
                           converter_comprimento, fahrenheit_para_celsius)


class TestUnidades(unittest.TestCase):
    def test_temperatura(self):
        self.assertEqual(celsius_para_fahrenheit(0), 32)
        self.assertEqual(celsius_para_fahrenheit(100), 212)
        self.assertEqual(fahrenheit_para_celsius(212), 100)
        self.assertAlmostEqual(fahrenheit_para_celsius(-40), -40)

    def test_kelvin(self):
        self.assertAlmostEqual(celsius_para_kelvin(0), 273.15)
        self.assertAlmostEqual(celsius_para_kelvin(-273.15), 0)
        with self.assertRaises(ValueError):
            celsius_para_kelvin(-300)

    def test_comprimento(self):
        self.assertAlmostEqual(converter_comprimento(1, "km", "m"), 1000)
        self.assertAlmostEqual(converter_comprimento(1, "milha", "km"), 1.609344)
        self.assertAlmostEqual(converter_comprimento(12, "pol", "pe"), 1.0)
        self.assertEqual(converter_comprimento(0, "m", "cm"), 0)

    def test_unidade_desconhecida(self):
        with self.assertRaises(KeyError):
            converter_comprimento(1, "m", "jarda")


if __name__ == "__main__":
    unittest.main()
