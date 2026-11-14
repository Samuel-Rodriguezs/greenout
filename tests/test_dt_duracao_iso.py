import sys
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_duracao_iso import Duracao, de_timedelta, formatar_duracao, parse_duracao


class TestDuracaoIso(unittest.TestCase):
    def test_pt1h30m(self) -> None:
        d = parse_duracao("PT1H30M")
        self.assertEqual(d, Duracao(horas=1, minutos=30))
        self.assertEqual(d.total_segundos(), 5400)
        self.assertEqual(d.para_timedelta(), timedelta(hours=1, minutes=30))

    def test_completa(self) -> None:
        d = parse_duracao("P1Y2M3DT4H5M6S")
        self.assertEqual(d, Duracao(1, 2, 0, 3, 4, 5, 6.0))

    def test_semanas_e_dias(self) -> None:
        self.assertEqual(parse_duracao("P2W").para_timedelta(), timedelta(days=14))
        self.assertEqual(parse_duracao("P1DT12H").total_segundos(), 129600)

    def test_fracao_e_virgula(self) -> None:
        self.assertEqual(parse_duracao("PT0.5S").segundos, 0.5)
        self.assertEqual(parse_duracao("PT1,5S").segundos, 1.5)

    def test_minusculas_e_espacos(self) -> None:
        self.assertEqual(parse_duracao(" pt45m "), Duracao(minutos=45))

    def test_mes_versus_minuto(self) -> None:
        self.assertEqual(parse_duracao("P1M").meses, 1)
        self.assertEqual(parse_duracao("PT1M").minutos, 1)

    def test_invalidas(self) -> None:
        for texto in ("", "P", "PT", "1H", "P1H", "PT1D", "P1DT", "PTH", "P-1D", "P1.5D", "xyz", "PT1H30"):
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError):
                    parse_duracao(texto)

    def test_formatar(self) -> None:
        self.assertEqual(formatar_duracao(Duracao()), "PT0S")
        self.assertEqual(formatar_duracao(Duracao(horas=1, minutos=30)), "PT1H30M")
        self.assertEqual(formatar_duracao(Duracao(dias=1, segundos=0.5)), "P1DT0.5S")
        self.assertEqual(str(Duracao(semanas=2)), "P2W")

    def test_ida_e_volta(self) -> None:
        for texto in ("P1Y2M3DT4H5M6S", "PT1H30M", "P2W", "PT0S", "PT0.25S"):
            with self.subTest(texto=texto):
                self.assertEqual(formatar_duracao(parse_duracao(texto)), texto)

    def test_de_timedelta(self) -> None:
        self.assertEqual(de_timedelta(timedelta(days=1, hours=2, minutes=3, seconds=4)), Duracao(dias=1, horas=2, minutos=3, segundos=4.0))
        self.assertEqual(formatar_duracao(de_timedelta(timedelta(minutes=90))), "PT1H30M")
        with self.assertRaises(ValueError):
            de_timedelta(timedelta(seconds=-1))


if __name__ == "__main__":
    unittest.main()
