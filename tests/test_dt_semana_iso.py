import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_semana_iso import formatar_semana_iso, segunda_da_semana_iso, semana_iso, semanas_no_ano_iso


class TestSemanaIso(unittest.TestCase):
    def test_valores_conhecidos(self) -> None:
        self.assertEqual(semana_iso(date(2021, 1, 3)), (2020, 53, 7))
        self.assertEqual(semana_iso(date(2024, 12, 30)), (2025, 1, 1))
        self.assertEqual(semana_iso(date(2026, 11, 14)), (2026, 46, 6))
        self.assertEqual(semana_iso(date(2016, 1, 1)), (2015, 53, 5))

    def test_igual_ao_isocalendar(self) -> None:
        d = date(1995, 1, 1)
        while d < date(2035, 1, 1):
            iso = d.isocalendar()
            self.assertEqual(semana_iso(d), (iso[0], iso[1], iso[2]), d)
            d += timedelta(days=1)

    def test_semanas_no_ano(self) -> None:
        self.assertEqual(semanas_no_ano_iso(2020), 53)
        self.assertEqual(semanas_no_ano_iso(2026), 53)
        self.assertEqual(semanas_no_ano_iso(2025), 52)

    def test_segunda_da_semana(self) -> None:
        self.assertEqual(segunda_da_semana_iso(2026, 1), date(2025, 12, 29))
        self.assertEqual(segunda_da_semana_iso(2026, 46), date(2026, 11, 9))
        self.assertEqual(segunda_da_semana_iso(2020, 53), date(2020, 12, 28))
        for ano in range(2000, 2040):
            self.assertEqual(segunda_da_semana_iso(ano, 10).isocalendar()[:2], (ano, 10))

    def test_semana_inexistente(self) -> None:
        with self.assertRaises(ValueError):
            segunda_da_semana_iso(2025, 53)
        with self.assertRaises(ValueError):
            segunda_da_semana_iso(2025, 0)

    def test_formatar(self) -> None:
        self.assertEqual(formatar_semana_iso(date(2026, 11, 14)), "2026-W46-6")
        self.assertEqual(formatar_semana_iso(date(2026, 1, 5)), "2026-W02-1")


if __name__ == "__main__":
    unittest.main()
