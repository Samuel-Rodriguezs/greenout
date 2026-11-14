import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_consenso import consenso, consenso_iupac


class TestBioConsenso(unittest.TestCase):
    def test_maioria(self):
        self.assertEqual(consenso(["ACG", "ACT", "ATG"]), "ACG")

    def test_empate_alfabetico(self):
        self.assertEqual(consenso(["AC", "GT"]), "AC")

    def test_uma_sequencia(self):
        self.assertEqual(consenso(["ACGT"]), "ACGT")

    def test_iupac(self):
        alin = ["ACG", "ACT", "ATG"]
        self.assertEqual(consenso_iupac(alin), "AYK")
        self.assertEqual(consenso_iupac(alin, 0.5), "ACG")

    def test_iupac_quatro_bases(self):
        self.assertEqual(consenso_iupac(["A", "C", "G", "T"], 0.25), "N")
        self.assertEqual(consenso_iupac(["A", "G"], 0.5), "R")

    def test_invalido(self):
        with self.assertRaises(ValueError):
            consenso([])
        with self.assertRaises(ValueError):
            consenso(["AC", "A"])


if __name__ == "__main__":
    unittest.main()
