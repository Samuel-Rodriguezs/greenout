import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_decimo_terceiro import (avos_no_ano, decimo_terceiro, primeira_parcela,
                                 segunda_parcela)

D = Decimal


class TestDomDecimoTerceiro(unittest.TestCase):
    def test_ano_inteiro(self):
        self.assertEqual(avos_no_ano(2024), 12)

    def test_admissao_dia_20_nao_conta_mes(self):
        # março: 20..31 = 12 dias -> não conta; abril a dezembro = 9
        self.assertEqual(avos_no_ano(2024, date(2024, 3, 20)), 9)

    def test_admissao_dia_17_conta_mes(self):
        # março: 17..31 = 15 dias -> conta
        self.assertEqual(avos_no_ano(2024, date(2024, 3, 17)), 10)

    def test_demissao(self):
        # jan-mai = 5; junho 1..14 = 14 dias não conta
        self.assertEqual(avos_no_ano(2024, None, date(2024, 6, 14)), 5)
        self.assertEqual(avos_no_ano(2024, None, date(2024, 6, 15)), 6)

    def test_admitido_em_ano_anterior_ou_posterior(self):
        self.assertEqual(avos_no_ano(2024, date(2020, 1, 1)), 12)
        self.assertEqual(avos_no_ano(2024, date(2025, 1, 1)), 0)

    def test_demissao_antes_admissao(self):
        with self.assertRaises(ValueError):
            avos_no_ano(2024, date(2024, 5, 1), date(2024, 4, 1))

    def test_valores(self):
        self.assertEqual(decimo_terceiro("2400", 7), D("1400.00"))
        self.assertEqual(primeira_parcela("2400", 7), D("700.00"))
        self.assertEqual(segunda_parcela("2400", 7, "100", "50"), D("550.00"))
        self.assertEqual(decimo_terceiro("1000", 1), D("83.33"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            decimo_terceiro("1000", 13)
        with self.assertRaises(ValueError):
            decimo_terceiro("-1", 3)


if __name__ == "__main__":
    unittest.main()
