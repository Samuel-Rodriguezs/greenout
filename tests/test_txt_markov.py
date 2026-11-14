import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_markov import CadeiaMarkov

TEXTO = "a b c a b c a b c"


class TestMarkov(unittest.TestCase):
    def test_deterministico_com_seed(self):
        m = CadeiaMarkov().treinar("o gato come o rato e o rato foge do gato")
        self.assertEqual(m.gerar(12, seed=7), m.gerar(12, seed=7))

    def test_tamanho(self):
        m = CadeiaMarkov().treinar(TEXTO)
        self.assertEqual(len(m.gerar(10, seed=1).split()), 10)
        self.assertEqual(m.gerar(0, seed=1), "")
        self.assertEqual(len(m.gerar(1, seed=1).split()), 1)

    def test_transicoes_validas(self):
        saida = CadeiaMarkov().treinar(TEXTO).gerar(30, seed=3).split()
        validos = {("a", "b"), ("b", "c"), ("c", "a")}
        for par in zip(saida, saida[1:]):
            self.assertIn(par, validos)

    def test_beco_sem_saida_reinicia(self):
        self.assertEqual(CadeiaMarkov().treinar("x y").gerar(5, seed=0), "x y x y x")

    def test_ordem_dois(self):
        m = CadeiaMarkov(ordem=2).treinar("a b c a b c")
        self.assertEqual(m.gerar(6, seed=2).split()[:3] in (["a", "b", "c"], ["b", "c", "a"], ["c", "a", "b"]), True)

    def test_erros(self):
        with self.assertRaises(ValueError):
            CadeiaMarkov(0)
        with self.assertRaises(ValueError):
            CadeiaMarkov().gerar(3)
        with self.assertRaises(ValueError):
            CadeiaMarkov(ordem=3).treinar("a b").gerar(3)


if __name__ == "__main__":
    unittest.main()
