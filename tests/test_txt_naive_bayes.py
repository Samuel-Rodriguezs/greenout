import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_naive_bayes import NaiveBayes, classificador_padrao


class TestNaiveBayes(unittest.TestCase):
    def setUp(self):
        self.nb = classificador_padrao()

    def test_spam(self):
        self.assertEqual(self.nb.prever("ganhe dinheiro grátis agora"), "spam")

    def test_ham(self):
        self.assertEqual(self.nb.prever("reunião do projeto amanhã"), "ham")

    def test_desconhecido_usa_prior(self):
        self.assertIn(self.nb.prever("xyzzy qwerty"), {"spam", "ham"})
        self.assertEqual(self.nb.prever(""), self.nb.prever("palavradesconhecida"))

    def test_nao_treinado(self):
        with self.assertRaises(ValueError):
            NaiveBayes().prever("oi")

    def test_custom(self):
        nb = NaiveBayes().treinar([("gol bola", "esporte"), ("voto urna", "politica")])
        self.assertEqual(nb.prever("bola"), "esporte")


if __name__ == "__main__":
    unittest.main()
