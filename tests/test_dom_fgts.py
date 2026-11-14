import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_fgts import (ALIQUOTA_APRENDIZ, deposito_mensal, multa_rescisoria,
                      saldo_acumulado)

D = Decimal


class TestDomFgts(unittest.TestCase):
    def test_deposito(self):
        self.assertEqual(deposito_mensal("3000"), D("240.00"))
        self.assertEqual(deposito_mensal("1000.50"), D("80.04"))
        self.assertEqual(deposito_mensal("1000", ALIQUOTA_APRENDIZ), D("20.00"))

    def test_saldo(self):
        self.assertEqual(saldo_acumulado(["100", "100"], "0.01"), D("201.00"))
        self.assertEqual(saldo_acumulado(["100"] * 12), D("1200.00"))
        self.assertEqual(saldo_acumulado([]), D("0.00"))

    def test_multa(self):
        self.assertEqual(multa_rescisoria("10000"), D("4000.00"))
        self.assertEqual(multa_rescisoria("10000", D("0.20")), D("2000.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            deposito_mensal("-1")
        with self.assertRaises(ValueError):
            multa_rescisoria("-1")
        with self.assertRaises(ValueError):
            saldo_acumulado(["1"], "-0.1")


if __name__ == "__main__":
    unittest.main()
