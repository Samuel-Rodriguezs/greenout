import sys
import unittest
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_dias import diferenca_em_dias, dias_uteis_entre, eh_bissexto


class TestDias(unittest.TestCase):
    def test_diferenca_basica(self):
        self.assertEqual(diferenca_em_dias("2024-01-01", "2024-01-31"), 30)

    def test_diferenca_negativa_e_zero(self):
        self.assertEqual(diferenca_em_dias("2024-02-01", "2024-01-01"), -31)
        self.assertEqual(diferenca_em_dias("2024-01-01", "2024-01-01"), 0)

    def test_ano_bissexto(self):
        self.assertEqual(diferenca_em_dias(date(2024, 2, 28), date(2024, 3, 1)), 2)
        self.assertEqual(diferenca_em_dias(date(2023, 2, 28), date(2023, 3, 1)), 1)

    def test_tipos_mistos(self):
        self.assertEqual(diferenca_em_dias(datetime(2024, 1, 1, 23, 0), "2024-01-02"), 1)

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            diferenca_em_dias("2024-13-01", "2024-01-01")
        with self.assertRaises(TypeError):
            diferenca_em_dias(20240101, "2024-01-01")

    def test_dias_uteis(self):
        # seg 2024-01-01 a seg 2024-01-08: 5 dias úteis
        self.assertEqual(dias_uteis_entre("2024-01-01", "2024-01-08"), 5)
        # sábado a segunda: 0
        self.assertEqual(dias_uteis_entre("2024-01-06", "2024-01-08"), 0)
        self.assertEqual(dias_uteis_entre("2024-01-01", "2024-01-01"), 0)
        with self.assertRaises(ValueError):
            dias_uteis_entre("2024-01-08", "2024-01-01")

    def test_bissexto(self):
        self.assertTrue(eh_bissexto(2024))
        self.assertTrue(eh_bissexto(2000))
        self.assertFalse(eh_bissexto(1900))
        self.assertFalse(eh_bissexto(2023))


if __name__ == "__main__":
    unittest.main()
