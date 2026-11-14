import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_smith_waterman import alinhar_local


class TestBioSmithWaterman(unittest.TestCase):
    def test_wikipedia(self):
        score, a, b, _, _ = alinhar_local("TGTTACGG", "GGTTGACTA", 3, -3, -2)
        self.assertEqual(score, 13)
        self.assertEqual(a, "GTT-AC")
        self.assertEqual(b, "GTTGAC")

    def test_trecho_comum(self):
        self.assertEqual(
            alinhar_local("TTACGTTT", "GGACGTGG"), (8, "ACGT", "ACGT", 2, 2)
        )

    def test_sem_similaridade(self):
        self.assertEqual(alinhar_local("AAAA", "TTTT"), (0, "", "", 0, 0))

    def test_vazias(self):
        self.assertEqual(alinhar_local("", "ACGT"), (0, "", "", 0, 0))


if __name__ == "__main__":
    unittest.main()
