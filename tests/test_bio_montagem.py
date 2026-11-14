import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_montagem import montar, sobreposicao


class TestBioMontagem(unittest.TestCase):
    def test_sobreposicao(self):
        self.assertEqual(sobreposicao("ATTAGACCTG", "AGACCTGCCG"), 7)
        self.assertEqual(sobreposicao("AAA", "CCC"), 0)
        self.assertEqual(sobreposicao("AAC", "CTT", 2), 0)
        self.assertEqual(sobreposicao("AAC", "CTT", 1), 1)

    def test_montagem_completa(self):
        frags = ["ATTAGACCTG", "CCTGCCGGAA", "AGACCTGCCG", "GCCGGAATAC"]
        self.assertEqual(montar(frags, 3), ["ATTAGACCTGCCGGAATAC"])

    def test_ordem_irrelevante(self):
        frags = ["GCCGGAATAC", "AGACCTGCCG", "ATTAGACCTG", "CCTGCCGGAA"]
        self.assertEqual(montar(frags, 3), ["ATTAGACCTGCCGGAATAC"])

    def test_disjuntos(self):
        self.assertEqual(montar(["CCCC", "AAAA"]), ["AAAA", "CCCC"])

    def test_contido_e_duplicado(self):
        self.assertEqual(montar(["ACGTAC", "CGT", "ACGTAC"]), ["ACGTAC"])

    def test_vazio(self):
        self.assertEqual(montar([]), [])
        self.assertEqual(montar([""]), [])


if __name__ == "__main__":
    unittest.main()
