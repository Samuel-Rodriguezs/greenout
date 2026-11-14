import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_motivo import buscar, buscar_ambas_fitas, contar


class TestBioMotivo(unittest.TestCase):
    def test_exato(self):
        self.assertEqual(buscar("ACGTACGT", "ACG"), [(0, 0), (4, 0)])

    def test_com_mismatch(self):
        self.assertEqual(buscar("ACGTACGT", "ACC", 1), [(0, 1), (4, 1)])
        self.assertEqual(buscar("ACGTACGT", "ACC", 0), [])

    def test_sobrepostas(self):
        self.assertEqual(buscar("AAAA", "AA"), [(0, 0), (1, 0), (2, 0)])
        self.assertEqual(contar("AAAA", "AA"), 3)

    def test_motivo_maior_que_seq(self):
        self.assertEqual(buscar("AC", "ACGT"), [])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            buscar("ACGT", "")
        with self.assertRaises(ValueError):
            buscar("ACGT", "A", -1)

    def test_ambas_fitas(self):
        self.assertEqual(
            buscar_ambas_fitas("AACGTT", "AAC"), [(0, "+", 0), (3, "-", 0)]
        )

    def test_palindromo_nao_duplica(self):
        self.assertEqual(buscar_ambas_fitas("ACGT", "ACGT"), [(0, "+", 0)])


if __name__ == "__main__":
    unittest.main()
