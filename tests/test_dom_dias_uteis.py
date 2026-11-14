import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_dias_uteis import (contar_dias_uteis, eh_dia_util, feriados_nacionais,
                            pascoa, somar_dias_uteis)


class TestDomDiasUteis(unittest.TestCase):
    def test_pascoa(self):
        self.assertEqual(pascoa(2024), date(2024, 3, 31))
        self.assertEqual(pascoa(2025), date(2025, 4, 20))
        self.assertEqual(pascoa(2000), date(2000, 4, 23))

    def test_feriados_moveis_2024(self):
        f = feriados_nacionais(2024)
        self.assertIn(date(2024, 2, 13), f)   # Carnaval (terça)
        self.assertIn(date(2024, 3, 29), f)   # Sexta-feira Santa
        self.assertIn(date(2024, 5, 30), f)   # Corpus Christi
        self.assertNotIn(date(2024, 2, 13), feriados_nacionais(2024, False))

    def test_consciencia_negra_so_a_partir_de_2024(self):
        self.assertNotIn(date(2023, 11, 20), feriados_nacionais(2023))
        self.assertIn(date(2024, 11, 20), feriados_nacionais(2024))

    def test_eh_dia_util(self):
        self.assertTrue(eh_dia_util(date(2024, 11, 14)))    # quinta
        self.assertFalse(eh_dia_util(date(2024, 11, 16)))   # sábado
        self.assertFalse(eh_dia_util(date(2024, 11, 15)))   # feriado
        self.assertFalse(eh_dia_util(date(2024, 12, 25)))

    def test_contar_novembro_2024(self):
        self.assertEqual(contar_dias_uteis(date(2024, 11, 1), date(2024, 11, 30)), 19)

    def test_contar_um_dia_e_invalido(self):
        self.assertEqual(contar_dias_uteis(date(2024, 11, 14), date(2024, 11, 14)), 1)
        self.assertEqual(contar_dias_uteis(date(2024, 11, 16), date(2024, 11, 16)), 0)
        with self.assertRaises(ValueError):
            contar_dias_uteis(date(2024, 11, 2), date(2024, 11, 1))

    def test_somar(self):
        # sexta 20/12 + 3: seg 23, ter 24, (quarta 25 feriado) quinta 26
        self.assertEqual(somar_dias_uteis(date(2024, 12, 20), 3), date(2024, 12, 26))
        self.assertEqual(somar_dias_uteis(date(2024, 12, 26), -3), date(2024, 12, 20))
        self.assertEqual(somar_dias_uteis(date(2024, 12, 20), 0), date(2024, 12, 20))

    def test_somar_cruzando_ano(self):
        # 31/12/2024 (ter) + 1 -> 01/01 feriado -> quinta 02/01
        self.assertEqual(somar_dias_uteis(date(2024, 12, 31), 1), date(2025, 1, 2))

    def test_feriados_customizados(self):
        self.assertEqual(somar_dias_uteis(date(2024, 11, 11), 1, [date(2024, 11, 12)]),
                         date(2024, 11, 13))


if __name__ == "__main__":
    unittest.main()
