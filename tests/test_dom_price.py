import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_price import parcela_price, tabela_price

D = Decimal


class TestDomPrice(unittest.TestCase):
    def test_parcela(self):
        self.assertEqual(parcela_price("1000", "0.01", 12), D("88.85"))

    def test_taxa_zero(self):
        self.assertEqual(parcela_price("1200", "0", 12), D("100.00"))

    def test_tabela(self):
        t = tabela_price("1000", "0.01", 12)
        self.assertEqual(len(t), 12)
        self.assertEqual(t[0].juros, D("10.00"))
        self.assertEqual(t[0].amortizacao, D("78.85"))
        self.assertEqual(t[0].saldo, D("921.15"))
        self.assertEqual(t[-1].saldo, D("0.00"))
        self.assertEqual(sum(l.amortizacao for l in t), D("1000.00"))

    def test_uma_parcela(self):
        t = tabela_price("100", "0.10", 1)
        self.assertEqual(t[0].parcela, D("110.00"))
        self.assertEqual(t[0].saldo, D("0.00"))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            parcela_price("100", "0.1", 0)
        with self.assertRaises(ValueError):
            parcela_price("-100", "0.1", 3)


if __name__ == "__main__":
    unittest.main()
