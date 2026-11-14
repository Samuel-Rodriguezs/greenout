import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_stemmer import stem, stem_todos


class TestStemmer(unittest.TestCase):
    def test_sufixos(self):
        self.assertEqual(stem("felizmente"), "feliz")
        self.assertEqual(stem("cantando"), "cant")
        self.assertEqual(stem("meninos"), "menin")

    def test_variantes_mesmo_radical(self):
        self.assertEqual(stem("gatinho"), stem("gatinha"))

    def test_palavra_curta_preservada(self):
        self.assertEqual(stem("sol"), "sol")
        self.assertEqual(stem("os"), "os")

    def test_caixa_e_vazio(self):
        self.assertEqual(stem("CANTANDO"), "cant")
        self.assertEqual(stem(""), "")

    def test_lista(self):
        self.assertEqual(stem_todos(["cantando", "sol"]), ["cant", "sol"])


if __name__ == "__main__":
    unittest.main()
