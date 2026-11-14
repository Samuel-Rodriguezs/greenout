import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_tm import tm, tm_gc, tm_wallace


class TestBioTm(unittest.TestCase):
    def test_wallace(self):
        self.assertEqual(tm_wallace("ATGC"), 12.0)
        self.assertEqual(tm_wallace("GGGG"), 16.0)
        self.assertEqual(tm_wallace("aaaa"), 8.0)

    def test_gc(self):
        self.assertAlmostEqual(tm_gc("GCGCGCGCGCATATATATAT"), 51.78)

    def test_limite_14(self):
        self.assertEqual(tm("A" * 13), 26.0)
        self.assertAlmostEqual(tm("A" * 14), 64.9 + 41 * (-16.4) / 14)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            tm("")
        with self.assertRaises(ValueError):
            tm("ACGU")


if __name__ == "__main__":
    unittest.main()
