import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_prazos import calcular_vencimento, dias_restantes, esta_vencido


class TestPrazos(unittest.TestCase):
    def test_corridos_simples(self) -> None:
        # 10/11/2026 (terça) + 15 = 25/11/2026 (quarta)
        self.assertEqual(calcular_vencimento(date(2026, 11, 10), 15), date(2026, 11, 25))

    def test_corridos_prorroga_fim_de_semana(self) -> None:
        # 10/11 + 4 = 14/11 (sábado) -> segunda 16/11
        self.assertEqual(calcular_vencimento(date(2026, 11, 10), 4), date(2026, 11, 16))
        self.assertEqual(
            calcular_vencimento(date(2026, 11, 10), 4, prorrogar=False), date(2026, 11, 14)
        )

    def test_corridos_prorroga_feriado(self) -> None:
        # 13/11 + 2 = 15/11 (domingo e feriado) -> 16/11; com 16/11 feriado -> 17/11
        self.assertEqual(calcular_vencimento(date(2026, 11, 13), 2), date(2026, 11, 16))
        self.assertEqual(
            calcular_vencimento(date(2026, 11, 13), 2, feriados=[date(2026, 11, 16)]),
            date(2026, 11, 17),
        )

    def test_uteis(self) -> None:
        # 5 dias úteis a partir de sexta 13/11 -> sexta 20/11
        self.assertEqual(calcular_vencimento(date(2026, 11, 13), 5, "uteis"), date(2026, 11, 20))
        fer = [date(2026, 11, 20)]
        self.assertEqual(
            calcular_vencimento(date(2026, 11, 13), 5, "uteis", fer), date(2026, 11, 23)
        )

    def test_prazo_zero(self) -> None:
        self.assertEqual(calcular_vencimento(date(2026, 11, 10), 0), date(2026, 11, 10))

    def test_entradas_invalidas(self) -> None:
        with self.assertRaises(ValueError):
            calcular_vencimento(date(2026, 11, 10), -1)
        with self.assertRaises(ValueError):
            calcular_vencimento(date(2026, 11, 10), 5, "semanas")
        with self.assertRaises(ValueError):
            dias_restantes(date(2026, 11, 10), date(2026, 11, 1), "x")

    def test_dias_restantes(self) -> None:
        self.assertEqual(dias_restantes(date(2026, 11, 20), date(2026, 11, 13)), 7)
        self.assertEqual(dias_restantes(date(2026, 11, 20), date(2026, 11, 13), "uteis"), 5)
        self.assertEqual(dias_restantes(date(2026, 11, 16), date(2026, 11, 14), "uteis"), 1)
        self.assertEqual(dias_restantes(date(2026, 11, 13), date(2026, 11, 20), "uteis"), -5)
        self.assertEqual(dias_restantes(date(2026, 11, 20), date(2026, 11, 20)), 0)

    def test_esta_vencido(self) -> None:
        self.assertFalse(esta_vencido(date(2026, 11, 20), date(2026, 11, 20)))
        self.assertTrue(esta_vencido(date(2026, 11, 20), date(2026, 11, 21)))


if __name__ == "__main__":
    unittest.main()
