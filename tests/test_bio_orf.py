import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_dna import complemento_reverso
from bio_orf import Orf, encontrar_orfs


class TestBioOrf(unittest.TestCase):
    def test_fita_direta(self):
        self.assertEqual(encontrar_orfs("CCATGAAATAGCC"), [Orf(2, 11, "+", "MK")])

    def test_fita_reversa(self):
        s = complemento_reverso("CCATGAAATAGCC")
        self.assertEqual(encontrar_orfs(s), [Orf(2, 11, "-", "MK")])

    def test_sem_stop_nao_conta(self):
        self.assertEqual(encontrar_orfs("ATGAAAAAA"), [])

    def test_minimo_aminoacidos(self):
        self.assertEqual(encontrar_orfs("ATGTAA"), [Orf(0, 6, "+", "M")])
        self.assertEqual(encontrar_orfs("ATGTAA", min_aa=2), [])

    def test_dois_orfs_em_fases_diferentes(self):
        orfs = encontrar_orfs("ATGTAACATGGGTTGA")
        self.assertEqual(
            [(o.inicio, o.fim, o.proteina) for o in orfs if o.fita == "+"],
            [(0, 6, "M"), (7, 16, "MG")],
        )

    def test_invalido(self):
        with self.assertRaises(ValueError):
            encontrar_orfs("ATGXAA")


if __name__ == "__main__":
    unittest.main()
