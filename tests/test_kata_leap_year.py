import calendar
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_leap_year import bissexto, dias_no_ano


class TestKataLeapYear(unittest.TestCase):
    def test_nao_divisivel_por_4(self):
        self.assertFalse(bissexto(2001))
        self.assertFalse(bissexto(2023))

    def test_divisivel_por_4(self):
        self.assertTrue(bissexto(1996))
        self.assertTrue(bissexto(2024))

    def test_seculo_nao_bissexto(self):
        for ano in (1700, 1800, 1900, 2100):
            self.assertFalse(bissexto(ano))

    def test_seculo_divisivel_por_400(self):
        for ano in (1600, 2000, 2400):
            self.assertTrue(bissexto(ano))

    def test_dias_no_ano(self):
        self.assertEqual(dias_no_ano(2024), 366)
        self.assertEqual(dias_no_ano(2023), 365)

    def test_confere_com_calendar(self):
        for ano in range(1, 2500):
            self.assertEqual(bissexto(ano), calendar.isleap(ano))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            bissexto(0)


if __name__ == "__main__":
    unittest.main()
