import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_idade import Idade, calcular_idade, eh_maior_de_idade, idade_em_anos, somar_meses


class TestIdade(unittest.TestCase):
    def test_exata(self) -> None:
        self.assertEqual(calcular_idade(date(1990, 5, 20), date(2026, 11, 14)), Idade(36, 5, 25))

    def test_no_aniversario_e_na_vespera(self) -> None:
        self.assertEqual(calcular_idade(date(2000, 11, 14), date(2026, 11, 14)), Idade(26, 0, 0))
        self.assertEqual(calcular_idade(date(2000, 11, 15), date(2026, 11, 14)), Idade(25, 11, 30))

    def test_mesmo_dia(self) -> None:
        self.assertEqual(calcular_idade(date(2026, 1, 1), date(2026, 1, 1)), Idade(0, 0, 0))

    def test_29_de_fevereiro(self) -> None:
        nasc = date(2000, 2, 29)
        self.assertEqual(calcular_idade(nasc, date(2001, 2, 27)), Idade(0, 11, 29))
        self.assertEqual(calcular_idade(nasc, date(2001, 2, 28)), Idade(1, 0, 0))
        self.assertEqual(calcular_idade(nasc, date(2004, 2, 29)), Idade(4, 0, 0))

    def test_virada_de_mes_curto(self) -> None:
        self.assertEqual(calcular_idade(date(2026, 1, 31), date(2026, 3, 1)), Idade(0, 1, 1))

    def test_futuro_invalido(self) -> None:
        with self.assertRaises(ValueError):
            calcular_idade(date(2030, 1, 1), date(2026, 1, 1))

    def test_somar_meses(self) -> None:
        self.assertEqual(somar_meses(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(somar_meses(date(2026, 11, 15), 3), date(2027, 2, 15))
        self.assertEqual(somar_meses(date(2026, 3, 31), -1), date(2026, 2, 28))

    def test_maioridade(self) -> None:
        self.assertFalse(eh_maior_de_idade(date(2008, 11, 15), date(2026, 11, 14)))
        self.assertTrue(eh_maior_de_idade(date(2008, 11, 14), date(2026, 11, 14)))
        self.assertEqual(idade_em_anos(date(1990, 1, 1), date(2026, 1, 1)), 36)

    def test_str(self) -> None:
        self.assertEqual(str(Idade(1, 1, 1)), "1 ano, 1 mês, 1 dia")
        self.assertEqual(str(Idade(36, 5, 25)), "36 anos, 5 meses, 25 dias")


if __name__ == "__main__":
    unittest.main()
