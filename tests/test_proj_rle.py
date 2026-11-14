import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_rle import comprimir, descomprimir, taxa_compressao


class TestRle(unittest.TestCase):
    def test_comprimir(self):
        self.assertEqual(comprimir("aaabbc"), "3a2b1c")
        self.assertEqual(comprimir(""), "")

    def test_descomprimir(self):
        self.assertEqual(descomprimir("3a2b1c"), "aaabbc")
        self.assertEqual(descomprimir("12x"), "x" * 12)

    def test_ida_e_volta(self):
        for t in ("", "a", "abc", "aaaaaaaaaaaabbb  \n\n"):
            self.assertEqual(descomprimir(comprimir(t)), t)

    def test_taxa(self):
        self.assertAlmostEqual(taxa_compressao("aaaaaaaaaa"), 0.3)
        self.assertGreater(taxa_compressao("abcd"), 1)

    def test_erros(self):
        with self.assertRaises(ValueError):
            comprimir("a1")
        for ruim in ("abc", "3", "a3"):
            with self.assertRaises(ValueError):
                descomprimir(ruim)
        with self.assertRaises(ValueError):
            taxa_compressao("")


if __name__ == "__main__":
    unittest.main()
