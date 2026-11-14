import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_upgma import upgma


class TestBioUpgma(unittest.TestCase):
    def test_um_taxon(self):
        self.assertEqual(upgma(["A"], [[0]]), "A;")

    def test_dois_taxa(self):
        self.assertEqual(upgma(["A", "B"], [[0, 4], [4, 0]]), "(A:2,B:2);")

    def test_tres_taxa(self):
        d = [[0, 4, 6], [4, 0, 6], [6, 6, 0]]
        self.assertEqual(upgma(["A", "B", "C"], d), "(C:3,(A:2,B:2):1);")

    def test_quatro_taxa(self):
        d = [[0, 2, 6, 10], [2, 0, 6, 10], [6, 6, 0, 8], [10, 10, 8, 0]]
        self.assertEqual(
            upgma(["A", "B", "C", "D"], d),
            "(D:4.66667,(C:3,(A:1,B:1):2):1.66667);",
        )

    def test_invalido(self):
        with self.assertRaises(ValueError):
            upgma([], [])
        with self.assertRaises(ValueError):
            upgma(["A", "B"], [[0]])


if __name__ == "__main__":
    unittest.main()
