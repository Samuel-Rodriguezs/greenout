import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_data_extenso import data_por_extenso, parse_data_extenso


class TestDataExtenso(unittest.TestCase):
    def test_padrao(self) -> None:
        self.assertEqual(data_por_extenso(date(2026, 11, 14)), "14 de novembro de 2026")
        self.assertEqual(data_por_extenso(date(2026, 1, 1)), "1º de janeiro de 2026")
        self.assertEqual(data_por_extenso(date(2024, 2, 29)), "29 de fevereiro de 2024")
        self.assertEqual(data_por_extenso(date(2026, 3, 2)), "2 de março de 2026")

    def test_dia_da_semana(self) -> None:
        self.assertEqual(
            data_por_extenso(date(2026, 11, 14), com_dia_semana=True), "sábado, 14 de novembro de 2026"
        )
        self.assertEqual(
            data_por_extenso(date(2026, 11, 16), com_dia_semana=True), "segunda-feira, 16 de novembro de 2026"
        )

    def test_numeros_por_extenso(self) -> None:
        self.assertEqual(
            data_por_extenso(date(2026, 11, 14), numeros_por_extenso=True),
            "catorze de novembro de dois mil e vinte e seis",
        )
        self.assertEqual(
            data_por_extenso(date(1999, 1, 1), numeros_por_extenso=True),
            "primeiro de janeiro de mil novecentos e noventa e nove",
        )
        self.assertEqual(
            data_por_extenso(date(2000, 12, 31), com_dia_semana=True, numeros_por_extenso=True),
            "domingo, trinta e um de dezembro de dois mil",
        )

    def test_parse(self) -> None:
        self.assertEqual(parse_data_extenso("14 de novembro de 2026"), date(2026, 11, 14))
        self.assertEqual(parse_data_extenso("1º de Janeiro de 2026"), date(2026, 1, 1))
        self.assertEqual(parse_data_extenso("sábado, 14 de novembro de 2026"), date(2026, 11, 14))
        self.assertEqual(parse_data_extenso("  3 de março de 2020 "), date(2020, 3, 3))

    def test_parse_invalido(self) -> None:
        for t in ("", "14/11/2026", "14 de foo de 2026", "31 de fevereiro de 2026", "14 novembro 2026"):
            with self.subTest(t=t):
                with self.assertRaises(ValueError):
                    parse_data_extenso(t)

    def test_ida_e_volta(self) -> None:
        d = date(2023, 12, 25)
        for _ in range(800):
            self.assertEqual(parse_data_extenso(data_por_extenso(d)), d)
            self.assertEqual(parse_data_extenso(data_por_extenso(d, com_dia_semana=True)), d)
            d += timedelta(days=1)


if __name__ == "__main__":
    unittest.main()
