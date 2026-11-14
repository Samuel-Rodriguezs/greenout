import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_tfidf import idf, termos_principais, tf, tfidf


class TestTfidf(unittest.TestCase):
    def test_tf(self):
        self.assertEqual(tf(["a", "a", "b", "c"])["a"], 0.5)
        self.assertEqual(tf([]), {})

    def test_idf_raro_maior(self):
        corpus = [["a", "b"], ["a", "c"], ["a"]]
        w = idf(corpus)
        self.assertGreater(w["b"], w["a"])
        self.assertAlmostEqual(w["a"], 1.0)

    def test_tfidf_e_termos(self):
        corpus = [["gato", "come", "peixe"], ["cão", "come", "osso"], ["gato", "gato", "dorme"]]
        v = tfidf(corpus)
        self.assertEqual(len(v), 3)
        self.assertGreater(v[0]["peixe"], v[0]["come"])
        self.assertEqual(termos_principais(v[2], 1), ["gato"])

    def test_corpus_vazio(self):
        self.assertEqual(tfidf([]), [])
        self.assertEqual(tfidf([[]]), [{}])
        self.assertTrue(math.isfinite(sum(idf([["x"]]).values())))


if __name__ == "__main__":
    unittest.main()
