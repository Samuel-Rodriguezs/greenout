import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_calendario_texto import calendario_mensal, semanas_do_mes


class TestCalendarioTexto(unittest.TestCase):
    def test_novembro_2026(self) -> None:
        esperado = "\n".join(
            [
                "   Novembro 2026",
                "Do Se Te Qu Qu Se Sa",
                " 1  2  3  4  5  6  7",
                " 8  9 10 11 12 13 14",
                "15 16 17 18 19 20 21",
                "22 23 24 25 26 27 28",
                "29 30",
            ]
        )
        self.assertEqual(calendario_mensal(2026, 11), esperado)

    def test_fevereiro_bissexto_comeca_no_meio(self) -> None:
        linhas = calendario_mensal(2024, 2).splitlines()
        self.assertEqual(linhas[2], "             1  2  3")  # 1/2/2024 foi quinta
        self.assertEqual(linhas[-1], "25 26 27 28 29")

    def test_fevereiro_exato_quatro_semanas(self) -> None:
        # fevereiro de 2026 começa no domingo e tem 28 dias
        self.assertEqual(len(semanas_do_mes(2026, 2)), 4)

    def test_destaque(self) -> None:
        txt = calendario_mensal(2026, 11, destacar=[5, 14])
        self.assertIn("[5]", txt)
        self.assertIn("[14]", txt)

    def test_semanas(self) -> None:
        semanas = semanas_do_mes(2026, 11)
        self.assertEqual(semanas[0], [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(semanas[-1], [29, 30, 0, 0, 0, 0, 0])

    def test_mes_invalido(self) -> None:
        with self.assertRaises(ValueError):
            calendario_mensal(2026, 13)


if __name__ == "__main__":
    unittest.main()
