import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_similaridade import cosseno, dice, jaccard, levenshtein, levenshtein_normalizada


class TestSimilaridade(unittest.TestCase):
    def test_cosseno(self):
        self.assertAlmostEqual(cosseno(["a", "b"], ["a", "b"]), 1.0)
        self.assertEqual(cosseno(["a"], ["b"]), 0.0)
        self.assertEqual(cosseno([], ["a"]), 0.0)

    def test_jaccard(self):
        self.assertAlmostEqual(jaccard({"a", "b"}, {"b", "c"}), 1 / 3)
        self.assertEqual(jaccard([], []), 1.0)
        self.assertEqual(jaccard(["a"], []), 0.0)

    def test_dice(self):
        self.assertAlmostEqual(dice({"a", "b"}, {"b", "c"}), 0.5)
        self.assertEqual(dice([], []), 1.0)

    def test_levenshtein(self):
        self.assertEqual(levenshtein("kitten", "sitting"), 3)
        self.assertEqual(levenshtein("", "abc"), 3)
        self.assertEqual(levenshtein("abc", "abc"), 0)

    def test_normalizada(self):
        self.assertEqual(levenshtein_normalizada("", ""), 1.0)
        self.assertEqual(levenshtein_normalizada("abc", "xyz"), 0.0)
        self.assertAlmostEqual(levenshtein_normalizada("casa", "caso"), 0.75)


if __name__ == "__main__":
    unittest.main()
