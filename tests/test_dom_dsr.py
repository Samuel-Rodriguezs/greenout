import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_dsr import calcular_dsr, dias_do_mes

D = Decimal


class TestDomDsr(unittest.TestCase):
    def test_dias_sem_feriado(self):
        # novembro/2024 tem 4 domingos (3, 10, 17, 24)
        self.assertEqual(dias_do_mes(2024, 11), (26, 4))

    def test_dias_com_feriados(self):
        fer = [date(2024, 11, 2), date(2024, 11, 15), date(2024, 11, 20)]
        self.assertEqual(dias_do_mes(2024, 11, fer), (23, 7))

    def test_feriado_em_domingo_nao_duplica(self):
        self.assertEqual(dias_do_mes(2024, 11, [date(2024, 11, 3)]), (26, 4))

    def test_feriado_de_outro_mes_ignorado(self):
        self.assertEqual(dias_do_mes(2024, 11, [date(2024, 12, 25)]), (26, 4))

    def test_dsr(self):
        self.assertEqual(calcular_dsr("260", 2024, 11), D("40.00"))
        fer = [date(2024, 11, 2), date(2024, 11, 15), date(2024, 11, 20)]
        self.assertEqual(calcular_dsr("230", 2024, 11, fer), D("70.00"))

    def test_zero_e_negativo(self):
        self.assertEqual(calcular_dsr("0", 2024, 11), D("0.00"))
        with self.assertRaises(ValueError):
            calcular_dsr("-1", 2024, 11)


if __name__ == "__main__":
    unittest.main()
