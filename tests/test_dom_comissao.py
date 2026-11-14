import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_comissao import comissao_global, comissao_marginal

D = Decimal


class TestDomComissao(unittest.TestCase):
    def test_marginal(self):
        # 10000*2% + 10000*3% + 5000*5% = 200 + 300 + 250
        self.assertEqual(comissao_marginal("25000"), D("750.00"))

    def test_marginal_primeira_faixa(self):
        self.assertEqual(comissao_marginal("5000"), D("100.00"))

    def test_marginal_no_limite(self):
        self.assertEqual(comissao_marginal("10000"), D("200.00"))
        self.assertEqual(comissao_marginal("20000"), D("500.00"))

    def test_zero(self):
        self.assertEqual(comissao_marginal("0"), D("0.00"))
        self.assertEqual(comissao_global("0"), D("0.00"))

    def test_global(self):
        self.assertEqual(comissao_global("25000"), D("1250.00"))
        self.assertEqual(comissao_global("10000"), D("200.00"))
        self.assertEqual(comissao_global("10000.01"), D("300.00"))

    def test_faixas_customizadas(self):
        faixas = ((D("1000"), D("0.1")), (None, D("0.2")))
        self.assertEqual(comissao_marginal("1500", faixas), D("200.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            comissao_marginal("-1")
        with self.assertRaises(ValueError):
            comissao_marginal("10", ((D("100"), D("0.1")),))
        with self.assertRaises(ValueError):
            comissao_global("10", ((D("200"), D("0.1")), (D("100"), D("0.2")), (None, D("0.3"))))


if __name__ == "__main__":
    unittest.main()
