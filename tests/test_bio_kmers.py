import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_kmers import contar_kmers, diversidade, kmers_possiveis, mais_frequentes


class TestBioKmers(unittest.TestCase):
    def test_contagem(self):
        self.assertEqual(dict(contar_kmers("ATATAT", 2)), {"AT": 3, "TA": 2})

    def test_k3(self):
        c = contar_kmers("ACGTACGT", 3)
        self.assertEqual(dict(c), {"ACG": 2, "CGT": 2, "GTA": 1, "TAC": 1})

    def test_bordas(self):
        self.assertEqual(len(contar_kmers("ACG", 4)), 0)
        self.assertEqual(dict(contar_kmers("ACG", 3)), {"ACG": 1})
        with self.assertRaises(ValueError):
            contar_kmers("ACG", 0)

    def test_mais_frequentes(self):
        self.assertEqual(mais_frequentes("ACGTACGT", 3), ["ACG", "CGT"])
        self.assertEqual(mais_frequentes("", 2), [])

    def test_diversidade(self):
        self.assertEqual(kmers_possiveis(3), 64)
        self.assertEqual(diversidade("ACGTACGT", 1), 1.0)
        self.assertEqual(diversidade("ACGTACGT", 2), 0.25)


if __name__ == "__main__":
    unittest.main()
