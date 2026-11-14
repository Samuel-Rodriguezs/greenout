import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_cambio import comprar_moeda, taxa_efetiva_compra, vender_moeda

D = Decimal


class TestDomCambio(unittest.TestCase):
    def test_compra_simples(self):
        self.assertEqual(comprar_moeda("1000", "5"), D("200.00"))

    def test_compra_com_spread(self):
        # 1000 / (5 * 1,02) = 196,0784...
        self.assertEqual(comprar_moeda("1000", "5", "0.02"), D("196.08"))

    def test_compra_com_spread_e_iof(self):
        # 965 / 5,10 = 189,2156...
        self.assertEqual(comprar_moeda("1000", "5", "0.02", "0.035"), D("189.22"))

    def test_venda(self):
        self.assertEqual(vender_moeda("100", "5"), D("500.00"))
        # 100 * 4,90 = 490; IOF 1,1% = 5,39
        self.assertEqual(vender_moeda("100", "5", "0.02", "0.011"), D("484.61"))

    def test_zero(self):
        self.assertEqual(comprar_moeda("0", "5"), D("0.00"))
        self.assertEqual(vender_moeda("0", "5"), D("0.00"))

    def test_taxa_efetiva(self):
        self.assertEqual(taxa_efetiva_compra("5"), D("5"))
        self.assertAlmostEqual(float(taxa_efetiva_compra("5", "0.02", "0.035")),
                               5.1 / 0.965, places=9)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            comprar_moeda("100", "0")
        with self.assertRaises(ValueError):
            comprar_moeda("-1", "5")
        with self.assertRaises(ValueError):
            vender_moeda("1", "5", "1")


if __name__ == "__main__":
    unittest.main()
