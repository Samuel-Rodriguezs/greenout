import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_cron import parse_cron, proxima_execucao


class TestCron(unittest.TestCase):
    def test_a_cada_minuto(self) -> None:
        self.assertEqual(
            proxima_execucao("* * * * *", datetime(2026, 11, 14, 10, 30, 45)),
            datetime(2026, 11, 14, 10, 31),
        )

    def test_estritamente_depois(self) -> None:
        self.assertEqual(
            proxima_execucao("30 10 * * *", datetime(2026, 11, 14, 10, 30)),
            datetime(2026, 11, 15, 10, 30),
        )

    def test_passo(self) -> None:
        c = parse_cron("*/15 * * * *")
        self.assertEqual(c.minutos, frozenset({0, 15, 30, 45}))
        self.assertEqual(c.proxima(datetime(2026, 1, 1, 0, 46)), datetime(2026, 1, 1, 1, 0))

    def test_diario_as_3h(self) -> None:
        self.assertEqual(
            proxima_execucao("0 3 * * *", datetime(2026, 12, 31, 23, 59)),
            datetime(2027, 1, 1, 3, 0),
        )

    def test_dia_da_semana(self) -> None:
        # segunda a sexta às 9h; 14/11/2026 é sábado -> segunda 16/11
        self.assertEqual(
            proxima_execucao("0 9 * * 1-5", datetime(2026, 11, 14, 12, 0)),
            datetime(2026, 11, 16, 9, 0),
        )
        # domingo como 0 e como 7
        self.assertEqual(parse_cron("0 0 * * 7").dias_semana, frozenset({0}))
        self.assertEqual(
            proxima_execucao("0 0 * * dom", datetime(2026, 11, 14)), datetime(2026, 11, 15)
        )

    def test_lista_e_faixa(self) -> None:
        c = parse_cron("0,30 8-10 * * *")
        self.assertEqual(
            c.proximas(datetime(2026, 1, 1, 9, 0), 3),
            [datetime(2026, 1, 1, 9, 30), datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 10, 30)],
        )

    def test_mes_por_nome(self) -> None:
        self.assertEqual(
            proxima_execucao("0 0 1 jan *", datetime(2026, 11, 14)), datetime(2027, 1, 1)
        )

    def test_29_de_fevereiro(self) -> None:
        self.assertEqual(
            proxima_execucao("0 0 29 2 *", datetime(2026, 3, 1)), datetime(2028, 2, 29)
        )

    def test_dia_mes_ou_dia_semana(self) -> None:
        # dia 13 OU sexta-feira
        c = parse_cron("0 0 13 * 5")
        self.assertEqual(c.proxima(datetime(2026, 11, 10)), datetime(2026, 11, 13))  # sexta e 13
        self.assertEqual(c.proxima(datetime(2026, 11, 13)), datetime(2026, 11, 20))
        self.assertEqual(c.proxima(datetime(2026, 12, 1)), datetime(2026, 12, 4))  # sexta
        self.assertEqual(c.proxima(datetime(2026, 12, 4)), datetime(2026, 12, 11))

    def test_nunca_satisfeita(self) -> None:
        with self.assertRaises(ValueError):
            proxima_execucao("0 0 31 2 *", datetime(2026, 1, 1))

    def test_invalidas(self) -> None:
        for expr in ("* * * *", "60 * * * *", "* 24 * * *", "* * 0 * *", "* * * 13 *",
                     "*/0 * * * *", "5-1 * * * *", "a * * * *", ", * * * *", "* * * * 8"):
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError):
                    parse_cron(expr)

    def test_casa(self) -> None:
        c = parse_cron("5 4 * * *")
        self.assertTrue(c.casa(datetime(2026, 1, 1, 4, 5)))
        self.assertFalse(c.casa(datetime(2026, 1, 1, 4, 6)))


if __name__ == "__main__":
    unittest.main()
