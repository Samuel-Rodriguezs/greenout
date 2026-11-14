import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_rebalanceamento import pesos_atuais, rebalancear


class TestRebalanceamento(unittest.TestCase):
    def test_vende_e_compra(self):
        o = rebalancear({"A": 60, "B": 40}, {"A": 10, "B": 10}, {"A": 0.5, "B": 0.5})
        self.assertAlmostEqual(o["A"], -10)
        self.assertAlmostEqual(o["B"], 10)

    def test_aporte(self):
        # patrimônio 1000 + 500 = 1500; alvo 60/40 -> A 900 (90 un), B 600 (60 un)
        o = rebalancear({"A": 50, "B": 50}, {"A": 10, "B": 10}, {"A": 0.6, "B": 0.4}, caixa=500)
        self.assertAlmostEqual(o["A"], 40)
        self.assertAlmostEqual(o["B"], 10)

    def test_novo_ativo_e_ativo_fora_do_alvo(self):
        o = rebalancear({"A": 10}, {"A": 10, "B": 20}, {"B": 1.0})
        self.assertAlmostEqual(o["A"], -10)
        self.assertAlmostEqual(o["B"], 5)

    def test_inteiro_trunca_para_zero(self):
        o = rebalancear({"A": 0}, {"A": 30}, {"A": 1.0}, caixa=100, inteiro=True)
        self.assertEqual(o["A"], 3.0)

    def test_ja_balanceada(self):
        o = rebalancear({"A": 5, "B": 5}, {"A": 2, "B": 2}, {"A": 0.5, "B": 0.5})
        self.assertAlmostEqual(o["A"], 0)
        self.assertAlmostEqual(o["B"], 0)

    def test_pesos_atuais(self):
        w = pesos_atuais({"A": 1, "B": 3}, {"A": 10, "B": 10})
        self.assertAlmostEqual(w["A"], 0.25)
        self.assertAlmostEqual(w["B"], 0.75)

    def test_erros(self):
        with self.assertRaises(ValueError):
            rebalancear({"A": 1}, {"A": 1}, {"A": 0.9})
        with self.assertRaises(ValueError):
            rebalancear({"A": 1}, {"A": 0}, {"A": 1.0})
        with self.assertRaises(ValueError):
            rebalancear({"A": 1}, {"A": 1}, {"A": 1.5, "B": -0.5})
        with self.assertRaises(ValueError):
            pesos_atuais({"A": 0}, {"A": 1})


if __name__ == "__main__":
    unittest.main()
