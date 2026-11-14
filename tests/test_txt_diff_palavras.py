import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_diff_palavras import diff_palavras, formatar, similaridade


class TestDiffPalavras(unittest.TestCase):
    def test_substituicao(self):
        self.assertEqual(
            diff_palavras("o gato preto dorme", "o gato branco dorme"),
            [("=", "o"), ("=", "gato"), ("-", "preto"), ("+", "branco"), ("=", "dorme")],
        )

    def test_insercao_e_remocao(self):
        self.assertEqual(diff_palavras("a b", "a x b"), [("=", "a"), ("+", "x"), ("=", "b")])
        self.assertEqual(diff_palavras("a x b", "a b"), [("=", "a"), ("-", "x"), ("=", "b")])

    def test_vazios(self):
        self.assertEqual(diff_palavras("", ""), [])
        self.assertEqual(diff_palavras("", "a b"), [("+", "a"), ("+", "b")])
        self.assertEqual(diff_palavras("a b", ""), [("-", "a"), ("-", "b")])

    def test_iguais(self):
        self.assertTrue(all(op == "=" for op, _ in diff_palavras("x y z", "x  y   z")))

    def test_formatar(self):
        d = diff_palavras("o gato preto", "o gato branco")
        self.assertEqual(formatar(d), "o gato [-preto-] {+branco+}")

    def test_similaridade(self):
        self.assertEqual(similaridade("", ""), 1.0)
        self.assertEqual(similaridade("a b", "c d"), 0.0)
        self.assertAlmostEqual(similaridade("a b c", "a b d"), 2 * 2 / 6)


if __name__ == "__main__":
    unittest.main()
