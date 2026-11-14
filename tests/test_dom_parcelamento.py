import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_parcelamento import parcelar, vencimentos

D = Decimal


class TestDomParcelamento(unittest.TestCase):
    def test_resto_na_primeira(self):
        self.assertEqual(parcelar("100", 3), [D("33.34"), D("33.33"), D("33.33")])

    def test_resto_na_ultima(self):
        self.assertEqual(parcelar("100", 3, resto_na_primeira=False),
                         [D("33.33"), D("33.33"), D("33.34")])

    def test_exato(self):
        self.assertEqual(parcelar("90", 3), [D("30"), D("30"), D("30")])

    def test_uma_parcela(self):
        self.assertEqual(parcelar("10.50", 1), [D("10.50")])

    def test_com_entrada(self):
        p = parcelar("1000", 3, entrada="100")
        self.assertEqual(p, [D("300"), D("300"), D("300")])
        self.assertEqual(sum(p) + D("100"), D("1000"))

    def test_mais_parcelas_que_centavos(self):
        p = parcelar("0.02", 5)
        self.assertEqual(sum(p), D("0.02"))
        self.assertEqual(p, [D("0.02"), D("0"), D("0"), D("0"), D("0")])

    def test_vencimentos_fim_de_mes(self):
        self.assertEqual(vencimentos(date(2024, 1, 31), 3),
                         [date(2024, 1, 31), date(2024, 2, 29), date(2024, 3, 31)])

    def test_vencimentos_virada_de_ano(self):
        self.assertEqual(vencimentos(date(2024, 11, 15), 3),
                         [date(2024, 11, 15), date(2024, 12, 15), date(2025, 1, 15)])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            parcelar("100", 0)
        with self.assertRaises(ValueError):
            parcelar("100", 2, entrada="200")
        with self.assertRaises(ValueError):
            parcelar("10.005", 2)
        with self.assertRaises(ValueError):
            vencimentos(date(2024, 1, 1), 0)


if __name__ == "__main__":
    unittest.main()
