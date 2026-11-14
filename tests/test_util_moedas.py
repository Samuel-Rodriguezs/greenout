import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_moedas import converter


class TestMoedas(unittest.TestCase):
    def test_usd_para_brl(self):
        self.assertEqual(converter(10, "USD", "BRL"), Decimal("50.00"))

    def test_brl_para_eur(self):
        self.assertEqual(converter(11, "BRL", "EUR"), Decimal("2.00"))

    def test_mesma_moeda(self):
        self.assertEqual(converter("12.34", "usd", "USD"), Decimal("12.34"))

    def test_arredondamento(self):
        # 1 BRL -> GBP = 0.15625 -> 0.16
        self.assertEqual(converter(1, "BRL", "GBP"), Decimal("0.16"))

    def test_zero(self):
        self.assertEqual(converter(0, "USD", "EUR"), Decimal("0.00"))

    def test_moeda_desconhecida(self):
        with self.assertRaises(KeyError):
            converter(1, "USD", "XYZ")

    def test_negativo(self):
        with self.assertRaises(ValueError):
            converter(-1, "USD", "BRL")

    def test_taxas_customizadas(self):
        taxas = {"A": Decimal("2"), "B": Decimal("4")}
        self.assertEqual(converter(8, "B", "A", taxas), Decimal("16.00"))


if __name__ == "__main__":
    unittest.main()
