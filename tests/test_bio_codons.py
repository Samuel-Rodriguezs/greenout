import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_codons import TABELA, codons_sinonimos, traduzir


class TestBioCodons(unittest.TestCase):
    def test_tabela(self):
        self.assertEqual(len(TABELA), 64)
        self.assertEqual(TABELA["ATG"], "M")
        self.assertEqual(TABELA["TGG"], "W")
        self.assertEqual(TABELA["TTT"], "F")
        self.assertEqual(TABELA["GGG"], "G")
        self.assertEqual(TABELA["TGA"], "*")

    def test_traduzir_rna(self):
        rna = "AUGGCCAUGGCGCCCAGAACUGAGAUCAAUAGUACCCGUAUUAACGGGUGA"
        self.assertEqual(traduzir(rna), "MAMAPRTEINSTRING")

    def test_stop(self):
        self.assertEqual(traduzir("ATGTAAGCC"), "M")
        self.assertEqual(traduzir("ATGTAAGCC", ate_stop=False), "M*A")

    def test_codon_incompleto_e_vazio(self):
        self.assertEqual(traduzir("ATGGC"), "M")
        self.assertEqual(traduzir(""), "")

    def test_invalido(self):
        with self.assertRaises(ValueError):
            traduzir("ATN")

    def test_sinonimos(self):
        self.assertEqual(codons_sinonimos("M"), ["ATG"])
        self.assertEqual(codons_sinonimos("*"), ["TAA", "TAG", "TGA"])
        self.assertEqual(len(codons_sinonimos("L")), 6)


if __name__ == "__main__":
    unittest.main()
