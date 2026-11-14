import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_hamming import distancia, posicoes_diferentes, proporcao


class TestBioHamming(unittest.TestCase):
    def test_rosalind(self):
        self.assertEqual(distancia("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT"), 7)

    def test_iguais_e_vazias(self):
        self.assertEqual(distancia("ACGT", "ACGT"), 0)
        self.assertEqual(distancia("", ""), 0)

    def test_posicoes(self):
        self.assertEqual(posicoes_diferentes("ACGT", "AGGA"), [1, 3])

    def test_proporcao(self):
        self.assertEqual(proporcao("ACGT", "ACGA"), 0.25)
        self.assertEqual(proporcao("", ""), 0.0)

    def test_tamanhos_diferentes(self):
        with self.assertRaises(ValueError):
            distancia("AC", "ACG")
        with self.assertRaises(ValueError):
            posicoes_diferentes("AC", "A")


if __name__ == "__main__":
    unittest.main()
