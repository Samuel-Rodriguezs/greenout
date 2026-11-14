import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_jukes_cantor import distancia, matriz_distancias, p_distancia


class TestBioJukesCantor(unittest.TestCase):
    def test_p(self):
        self.assertEqual(p_distancia("AAAAAAAAAA", "AAAAAAAAAC"), 0.1)

    def test_identicas(self):
        self.assertEqual(distancia("ACGT", "ACGT"), 0.0)

    def test_valor(self):
        # -0,75 * ln(1 - 0,4/3) = 0,10733
        self.assertAlmostEqual(distancia("AAAAAAAAAA", "AAAAAAAAAC"), 0.10733, places=4)

    def test_maior_que_p(self):
        self.assertGreater(distancia("AAAAAAAAAA", "AAAAACCAAA"), 0.2)

    def test_saturada(self):
        with self.assertRaises(ValueError):
            distancia("ACGT", "CATG")  # p = 1
        with self.assertRaises(ValueError):
            distancia("AAAA", "CCCA")  # p = 0,75

    def test_invalidas(self):
        with self.assertRaises(ValueError):
            distancia("", "")
        with self.assertRaises(ValueError):
            distancia("A", "AC")

    def test_matriz(self):
        m = matriz_distancias(["AAAAAAAAAA", "AAAAAAAAAC", "AAAAAAAAAA"])
        self.assertEqual(m[0][2], 0.0)
        self.assertEqual(m[0][1], m[1][0])
        self.assertEqual(m[1][1], 0.0)


if __name__ == "__main__":
    unittest.main()
