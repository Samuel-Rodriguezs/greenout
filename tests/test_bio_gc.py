import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_gc import conteudo_gc, gc_skew, janela_mais_rica, janelas_gc


class TestBioGc(unittest.TestCase):
    def test_conteudo(self):
        self.assertEqual(conteudo_gc("GGCC"), 1.0)
        self.assertEqual(conteudo_gc("ATGC"), 0.5)
        self.assertEqual(conteudo_gc("atat"), 0.0)

    def test_vazio(self):
        with self.assertRaises(ValueError):
            conteudo_gc("")

    def test_janelas(self):
        self.assertEqual(janelas_gc("AATTGGCC", 4, 2), [(0, 0.0), (2, 0.5), (4, 1.0)])
        self.assertEqual(janelas_gc("ACG", 5), [])

    def test_janelas_invalidas(self):
        with self.assertRaises(ValueError):
            janelas_gc("ACGT", 0)
        with self.assertRaises(ValueError):
            janelas_gc("ACGT", 2, 0)

    def test_skew(self):
        self.assertEqual(gc_skew("GGGC"), 0.5)
        self.assertEqual(gc_skew("CCCG"), -0.5)
        self.assertEqual(gc_skew("ATAT"), 0.0)

    def test_janela_mais_rica(self):
        self.assertEqual(janela_mais_rica("AATTGGCC", 4), (4, 1.0))
        with self.assertRaises(ValueError):
            janela_mais_rica("AC", 3)


if __name__ == "__main__":
    unittest.main()
