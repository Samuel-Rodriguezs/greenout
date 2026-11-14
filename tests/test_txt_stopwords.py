import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_stopwords import e_stopword, remover_stopwords, remover_stopwords_texto


class TestStopwords(unittest.TestCase):
    def test_basico(self):
        self.assertEqual(remover_stopwords(["O", "gato", "e", "o", "rato"]), ["gato", "rato"])

    def test_extras(self):
        self.assertEqual(remover_stopwords(["gato", "RATO"], {"rato"}), ["gato"])

    def test_vazio(self):
        self.assertEqual(remover_stopwords([]), [])

    def test_e_stopword(self):
        self.assertTrue(e_stopword("Não"))
        self.assertFalse(e_stopword("casa"))

    def test_texto(self):
        self.assertEqual(remover_stopwords_texto("A casa de Maria, e o carro!"), "casa Maria carro")


if __name__ == "__main__":
    unittest.main()
