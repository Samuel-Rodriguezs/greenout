import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_zeller import dia_da_semana, para_weekday, zeller


class TestZeller(unittest.TestCase):
    def test_datas_conhecidas(self) -> None:
        self.assertEqual(dia_da_semana(2000, 1, 1), "sábado")
        self.assertEqual(dia_da_semana(1969, 7, 20), "domingo")  # pouso na Lua
        self.assertEqual(dia_da_semana(2026, 11, 14), "sábado")
        self.assertEqual(dia_da_semana(2024, 2, 29), "quinta-feira")
        self.assertEqual(dia_da_semana(1822, 9, 7), "sábado")  # Independência

    def test_indice(self) -> None:
        self.assertEqual(zeller(2000, 1, 1), 0)
        self.assertEqual(zeller(2026, 11, 15), 1)

    def test_concorda_com_datetime_por_vinte_anos_e_viradas_de_seculo(self) -> None:
        for inicio in (date(1899, 12, 1), date(1999, 12, 1), date(2099, 12, 1)):
            d = inicio
            for _ in range(800):
                with self.subTest(d=d):
                    self.assertEqual(para_weekday(d.year, d.month, d.day), d.weekday())
                d += timedelta(days=1)

    def test_data_invalida(self) -> None:
        with self.assertRaises(ValueError):
            zeller(2025, 2, 29)
        with self.assertRaises(ValueError):
            zeller(2025, 13, 1)


if __name__ == "__main__":
    unittest.main()
