import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_snp import efeito, encontrar_snps


class TestBioSnp(unittest.TestCase):
    def test_snps(self):
        self.assertEqual(
            encontrar_snps("ACGT", "ATGA"), [(2, "C", "T"), (4, "T", "A")]
        )
        self.assertEqual(encontrar_snps("ACGT", "ACGT"), [])
        self.assertEqual(encontrar_snps("", ""), [])

    def test_tamanhos(self):
        with self.assertRaises(ValueError):
            encontrar_snps("AC", "A")

    def test_efeitos(self):
        cds = "ATGGCCTGG"
        self.assertEqual(efeito(cds, 6, "T"), "sinonima")  # GCC -> GCT (Ala)
        self.assertEqual(efeito(cds, 5, "A"), "missense")  # GCC -> GAC (Asp)
        self.assertEqual(efeito("ATGTGG", 6, "A"), "nonsense")  # TGG -> TGA

    def test_mesma_base_e_sinonima(self):
        self.assertEqual(efeito("ATGGCC", 4, "G"), "sinonima")

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            efeito("ATG", 4, "A")
        with self.assertRaises(ValueError):
            efeito("ATG", 0, "A")
        with self.assertRaises(ValueError):
            efeito("ATG", 1, "N")
        with self.assertRaises(ValueError):
            efeito("ATGGC", 5, "A")


if __name__ == "__main__":
    unittest.main()
