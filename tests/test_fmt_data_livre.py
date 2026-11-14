import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_data_livre import ErroData, parse

BASE = date(2024, 1, 31)  # quarta-feira


class TestFmtDataLivre(unittest.TestCase):
    def esperar(self, texto, esperado, base=BASE):
        with self.subTest(texto=texto):
            self.assertEqual(parse(texto, base), esperado)

    def test_relativos_simples(self):
        self.esperar("hoje", date(2024, 1, 31))
        self.esperar("Amanhã", date(2024, 2, 1))
        self.esperar("depois de amanhã", date(2024, 2, 2))
        self.esperar("ontem", date(2024, 1, 30))
        self.esperar("anteontem", date(2024, 1, 29))

    def test_daqui_a(self):
        self.esperar("daqui a 3 dias", date(2024, 2, 3))
        self.esperar("daqui a duas semanas", date(2024, 2, 14))
        self.esperar("em 1 mês", date(2024, 2, 29))  # 31/01 + 1 mês limitado ao fim de fevereiro
        self.esperar("daqui a 2 meses", date(2024, 3, 31))
        self.esperar("daqui a um ano", date(2025, 1, 31))
        self.esperar("dentro de 10 dias", date(2024, 2, 10))

    def test_ha_e_atras(self):
        self.esperar("há 2 dias", date(2024, 1, 29))
        self.esperar("3 semanas atrás", date(2024, 1, 10))
        self.esperar("há um ano", date(2023, 1, 31))
        self.esperar("1 mes atras", date(2023, 12, 31))

    def test_dias_da_semana(self):
        self.esperar("próxima segunda", date(2024, 2, 5))
        self.esperar("sexta que vem", date(2024, 2, 2))
        self.esperar("quarta", date(2024, 1, 31))
        self.esperar("próxima quarta", date(2024, 2, 7))
        self.esperar("última sexta", date(2024, 1, 26))
        self.esperar("terça-feira passada", date(2024, 1, 30))
        self.esperar("sábado", date(2024, 2, 3))

    def test_semana_mes_ano(self):
        self.esperar("próxima semana", date(2024, 2, 7))
        self.esperar("mês passado", date(2023, 12, 31))
        self.esperar("ano que vem", date(2025, 1, 31))

    def test_absolutas(self):
        self.esperar("25/12/2024", date(2024, 12, 25))
        self.esperar("5/3", date(2024, 3, 5))
        self.esperar("2023-07-09", date(2023, 7, 9))
        self.esperar("15 de março de 2025", date(2025, 3, 15))
        self.esperar("dia 7 de setembro", date(2024, 9, 7))
        self.esperar("1 de março", date(2024, 3, 1))

    def test_data_base_padrao(self):
        self.assertEqual(parse("hoje"), date.today())

    def test_malformadas(self):
        for ruim in ["", "   ", "blablabla", "32/01/2024", "29/02/2023", "2024-13-01", "31 de abril",
                     "daqui a x dias", "daqui a 3 horas", "próxima foo", "15 de foo de 2020"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroData):
                    parse(ruim, BASE)


if __name__ == "__main__":
    unittest.main()
