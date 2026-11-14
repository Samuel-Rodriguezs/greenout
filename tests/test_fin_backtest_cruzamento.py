import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_backtest_cruzamento import backtest_cruzamento

P = [10, 10, 10, 11, 12, 13, 12, 10]


class TestBacktest(unittest.TestCase):
    def test_sem_custo(self):
        r = backtest_cruzamento(P, 2, 3)
        self.assertEqual(r.posicoes, [0, 0, 0, 0, 1, 1, 1, 1])
        self.assertAlmostEqual(r.patrimonio[-1], 10 / 11)
        self.assertAlmostEqual(r.patrimonio[4], 12 / 11)
        self.assertEqual(r.n_operacoes, 1)
        self.assertAlmostEqual(r.retorno_total, 10 / 11 - 1)

    def test_com_custo(self):
        r = backtest_cruzamento(P, 2, 3, custo=0.01)
        self.assertAlmostEqual(r.patrimonio[-1], 0.99 * 10 / 11)

    def test_nunca_opera(self):
        r = backtest_cruzamento([5, 4, 3, 2, 1], 1, 2, custo=0.1)
        self.assertEqual(r.n_operacoes, 0)
        self.assertEqual(r.patrimonio, [1.0] * 5)

    def test_entrada_e_saida(self):
        # sinal liga em t=2 (SMA1=2>1.5), desliga em t=4; posição vale em t=3 e 4
        r = backtest_cruzamento([1, 1, 2, 3, 1, 1], 1, 2, custo=0.0)
        self.assertEqual(r.posicoes, [0, 0, 0, 1, 1, 0])
        self.assertAlmostEqual(r.patrimonio[-1], 3 / 2 * 1 / 3)
        self.assertEqual(r.n_operacoes, 2)

    def test_erros(self):
        with self.assertRaises(ValueError):
            backtest_cruzamento(P, 3, 2)
        with self.assertRaises(ValueError):
            backtest_cruzamento(P, 1, 2, custo=1.0)
        with self.assertRaises(ValueError):
            backtest_cruzamento([1, -1], 1, 2)

    def test_serie_vazia(self):
        r = backtest_cruzamento([], 1, 2)
        self.assertEqual(r.patrimonio, [])
        self.assertEqual(r.retorno_total, 0.0)


if __name__ == "__main__":
    unittest.main()
