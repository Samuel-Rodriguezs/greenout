import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_nuvem import tamanhos_fonte, top_palavras

TEXTO = "O gato viu o rato. O gato correu atrás do rato e o cachorro viu o gato."


class TestNuvem(unittest.TestCase):
    def test_top(self):
        self.assertEqual(top_palavras(TEXTO, 3), [("gato", 3), ("rato", 2), ("viu", 2)])

    def test_n_limita(self):
        self.assertEqual(top_palavras(TEXTO, 1), [("gato", 3)])
        self.assertEqual(top_palavras(TEXTO, 0), [])

    def test_com_stopwords(self):
        r = top_palavras("de de de casa", 2, sem_stopwords=False, min_letras=1)
        self.assertEqual(r[0], ("de", 3))

    def test_vazio_e_n_negativo(self):
        self.assertEqual(top_palavras("", 5), [])
        with self.assertRaises(ValueError):
            top_palavras("a", -1)

    def test_tamanhos(self):
        self.assertEqual(tamanhos_fonte([("a", 10), ("b", 5), ("c", 1)], 10, 40), {"a": 40, "b": 23, "c": 10})
        self.assertEqual(tamanhos_fonte([("a", 2), ("b", 2)], 10, 40), {"a": 40, "b": 40})
        self.assertEqual(tamanhos_fonte([]), {})


if __name__ == "__main__":
    unittest.main()
