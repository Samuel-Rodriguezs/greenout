import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_crivo_segmentado import crivo_simples, primos_no_intervalo


class TestCrivoSegmentado(unittest.TestCase):
    def test_crivo_simples(self):
        self.assertEqual(crivo_simples(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        self.assertEqual(crivo_simples(1), [])
        self.assertEqual(crivo_simples(2), [2])

    def test_intervalo(self):
        self.assertEqual(primos_no_intervalo(10, 30), [11, 13, 17, 19, 23, 29])

    def test_inicio_abaixo_de_2(self):
        self.assertEqual(primos_no_intervalo(-10, 10), [2, 3, 5, 7])
        self.assertEqual(primos_no_intervalo(0, 1), [])

    def test_intervalo_invalido(self):
        self.assertEqual(primos_no_intervalo(20, 10), [])

    def test_coincide_com_crivo_simples(self):
        todos = crivo_simples(10000)
        self.assertEqual(primos_no_intervalo(5000, 10000), [p for p in todos if p >= 5000])

    def test_quadrado_de_primo(self):
        self.assertEqual(primos_no_intervalo(49, 49), [])
        self.assertEqual(primos_no_intervalo(47, 47), [47])


if __name__ == "__main__":
    unittest.main()
