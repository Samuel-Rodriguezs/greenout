import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_sac import tabela_sac, total_juros

D = Decimal


class TestDomSac(unittest.TestCase):
    def test_tabela(self):
        t = tabela_sac("1200", "0.01", 4)
        self.assertEqual([l.parcela for l in t],
                         [D("312.00"), D("309.00"), D("306.00"), D("303.00")])
        self.assertEqual([l.saldo for l in t],
                         [D("900.00"), D("600.00"), D("300.00"), D("0.00")])
        self.assertEqual(total_juros(t), D("30.00"))

    def test_residuo_na_ultima(self):
        t = tabela_sac("100", "0", 3)
        self.assertEqual([l.amortizacao for l in t],
                         [D("33.33"), D("33.33"), D("33.34")])
        self.assertEqual(t[-1].saldo, D("0.00"))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            tabela_sac("100", "0.1", 0)
        with self.assertRaises(ValueError):
            tabela_sac("100", "-0.1", 2)


if __name__ == "__main__":
    unittest.main()
