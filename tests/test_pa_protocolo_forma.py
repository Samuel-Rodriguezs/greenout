import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_protocolo_forma import Circulo, Forma, Retangulo, area_total, maior_forma


class Quadrado:  # sem herdar de nada: tipagem estrutural
    def __init__(self, lado):
        self.lado = lado

    def area(self):
        return self.lado ** 2


class TestProtocolo(unittest.TestCase):
    def test_isinstance_estrutural(self):
        self.assertIsInstance(Quadrado(2), Forma)
        self.assertNotIsInstance("texto", Forma)

    def test_area_total(self):
        self.assertAlmostEqual(area_total([Retangulo(2, 3), Quadrado(2), Circulo(1)]), 10 + math.pi)
        self.assertEqual(area_total([]), 0.0)

    def test_area_total_rejeita_invalido(self):
        with self.assertRaises(TypeError):
            area_total([Retangulo(1, 1), 42])

    def test_maior_forma(self):
        q = Quadrado(5)
        self.assertIs(maior_forma([Retangulo(1, 1), q, Circulo(1)]), q)
        self.assertIsNone(maior_forma([]))


if __name__ == "__main__":
    unittest.main()
