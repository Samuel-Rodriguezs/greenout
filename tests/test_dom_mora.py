import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_mora import calcular_mora, dias_de_atraso

D = Decimal


class TestDomMora(unittest.TestCase):
    def test_dias(self):
        self.assertEqual(dias_de_atraso(date(2024, 1, 10), date(2024, 2, 9)), 30)
        self.assertEqual(dias_de_atraso(date(2024, 1, 10), date(2024, 1, 10)), 0)
        self.assertEqual(dias_de_atraso(date(2024, 1, 10), date(2024, 1, 5)), 0)

    def test_em_dia(self):
        r = calcular_mora("1000", date(2024, 1, 10), date(2024, 1, 10))
        self.assertEqual(r.total, D("1000.00"))
        self.assertEqual(r.multa, D("0.00"))

    def test_trinta_dias(self):
        r = calcular_mora("1000", date(2024, 1, 10), date(2024, 2, 9))
        self.assertEqual(r.dias, 30)
        self.assertEqual(r.multa, D("20.00"))
        self.assertEqual(r.juros, D("10.00"))
        self.assertEqual(r.total, D("1030.00"))

    def test_um_dia_e_dez_dias(self):
        r = calcular_mora("1000", date(2024, 1, 10), date(2024, 1, 20))
        self.assertEqual(r.juros, D("3.33"))
        r1 = calcular_mora("1000", date(2024, 1, 10), date(2024, 1, 11))
        self.assertEqual(r1.juros, D("0.33"))

    def test_composto_trinta_dias_igual_um_mes(self):
        r = calcular_mora("1000", date(2024, 1, 10), date(2024, 2, 9), composto=True)
        self.assertEqual(r.juros, D("10.00"))

    def test_parametros(self):
        r = calcular_mora("500", date(2024, 1, 1), date(2024, 1, 31),
                          multa=D("0.10"), juros_mensal=D("0.02"))
        self.assertEqual(r.total, D("560.00"))

    def test_negativo(self):
        with self.assertRaises(ValueError):
            calcular_mora("-1", date(2024, 1, 1), date(2024, 1, 2))


if __name__ == "__main__":
    unittest.main()
