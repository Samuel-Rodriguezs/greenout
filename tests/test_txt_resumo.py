import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_resumo import pontuar_sentencas, resumir

TEXTO = ("Python é uma linguagem popular. Python é usada em ciência de dados. "
         "O gato dorme. Muitos programadores amam Python.")


class TestResumo(unittest.TestCase):
    def test_uma_sentenca(self):
        self.assertEqual(resumir(TEXTO, 1), "Python é uma linguagem popular.")

    def test_ordem_original(self):
        self.assertEqual(resumir(TEXTO, 2), "Python é uma linguagem popular. Python é usada em ciência de dados.")

    def test_n_maior_que_total(self):
        self.assertEqual(resumir("Oi. Tchau.", 5), "Oi. Tchau.")

    def test_vazio(self):
        self.assertEqual(resumir("", 2), "")
        self.assertEqual(pontuar_sentencas(""), [])

    def test_n_invalido(self):
        with self.assertRaises(ValueError):
            resumir(TEXTO, 0)

    def test_sentenca_so_stopwords(self):
        self.assertEqual(pontuar_sentencas("Não é o.")[0][1], 0.0)


if __name__ == "__main__":
    unittest.main()
