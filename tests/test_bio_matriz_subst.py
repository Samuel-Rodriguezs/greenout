import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_matriz_subst import classificar, contar_ts_tv, matriz, pontuar


class TestBioMatrizSubst(unittest.TestCase):
    def test_classificar(self):
        self.assertEqual(classificar("A", "A"), "identidade")
        self.assertEqual(classificar("A", "G"), "transicao")
        self.assertEqual(classificar("T", "C"), "transicao")
        self.assertEqual(classificar("A", "C"), "transversao")
        self.assertEqual(classificar("G", "T"), "transversao")

    def test_invalido(self):
        with self.assertRaises(ValueError):
            classificar("A", "N")
        with self.assertRaises(ValueError):
            classificar("AC", "A")

    def test_matriz(self):
        m = matriz()
        self.assertEqual(len(m), 16)
        self.assertEqual(m[("A", "A")], 2)
        self.assertEqual(m[("A", "G")], -1)
        self.assertEqual(m[("C", "G")], -2)
        self.assertEqual(m[("G", "A")], m[("A", "G")])

    def test_pontuar(self):
        self.assertEqual(pontuar("ACGT", "AGGT"), 4)
        self.assertEqual(pontuar("", ""), 0)
        self.assertEqual(pontuar("AG", "GA", matriz(1, -3, -4)), -6)

    def test_ts_tv(self):
        self.assertEqual(contar_ts_tv("AGCT", "GATT"), (3, 0))
        self.assertEqual(contar_ts_tv("AC", "CA"), (0, 2))
        with self.assertRaises(ValueError):
            contar_ts_tv("A", "AC")


if __name__ == "__main__":
    unittest.main()
