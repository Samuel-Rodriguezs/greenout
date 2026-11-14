import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_needleman_wunsch import alinhar, identidade


class TestBioNeedlemanWunsch(unittest.TestCase):
    def test_identicas(self):
        self.assertEqual(alinhar("ACGT", "ACGT"), (4, "ACGT", "ACGT"))

    def test_gap(self):
        self.assertEqual(alinhar("ACGT", "AGT"), (2, "ACGT", "A-GT"))

    def test_mismatch(self):
        self.assertEqual(alinhar("AC", "AG"), (0, "AC", "AG"))

    def test_vazia(self):
        self.assertEqual(alinhar("", "AC"), (-2, "--", "AC"))
        self.assertEqual(alinhar("", ""), (0, "", ""))

    def test_parametros(self):
        # gap caro: prefere mismatch (2 + -1 = 1)
        self.assertEqual(alinhar("AC", "AG", match=2, mismatch=-1, gap=-5)[0], 1)

    def test_identidade(self):
        self.assertEqual(identidade("ACGT", "A-GT"), 0.75)
        self.assertEqual(identidade("", ""), 0.0)
        with self.assertRaises(ValueError):
            identidade("AC", "A")


if __name__ == "__main__":
    unittest.main()
