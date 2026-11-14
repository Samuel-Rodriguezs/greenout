import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_dna import (
    complemento,
    complemento_reverso,
    transcrever,
    transcrever_reversa,
    validar_dna,
    validar_rna,
)


class TestBioDna(unittest.TestCase):
    def test_validar(self):
        self.assertTrue(validar_dna("ACGT"))
        self.assertFalse(validar_dna("ACGU"))
        self.assertFalse(validar_dna(""))
        self.assertFalse(validar_dna("acgt"))
        self.assertTrue(validar_rna("ACGU"))
        self.assertFalse(validar_rna("ACGT"))

    def test_complemento_reverso(self):
        self.assertEqual(complemento("ATGC"), "TACG")
        self.assertEqual(complemento_reverso("ATGC"), "GCAT")
        self.assertEqual(complemento_reverso("AUGC", rna=True), "GCAU")

    def test_reverso_duas_vezes_identidade(self):
        s = "AAACCCGGGTTTA"
        self.assertEqual(complemento_reverso(complemento_reverso(s)), s)

    def test_transcricao(self):
        self.assertEqual(
            transcrever("GATGGAACTTGACTACGTAAATT"), "GAUGGAACUUGACUACGUAAAUU"
        )
        self.assertEqual(transcrever_reversa("GAUU"), "GATT")

    def test_vazio_e_invalido(self):
        self.assertEqual(complemento_reverso(""), "")
        with self.assertRaises(ValueError):
            complemento("ACGX")
        with self.assertRaises(ValueError):
            transcrever("ACGU")


if __name__ == "__main__":
    unittest.main()
