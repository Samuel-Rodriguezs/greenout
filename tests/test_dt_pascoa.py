import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_pascoa import pascoa


class TestPascoa(unittest.TestCase):
    def test_valores_conhecidos(self) -> None:
        conhecidos = {
            2000: date(2000, 4, 23),
            2019: date(2019, 4, 21),
            2022: date(2022, 4, 17),
            2024: date(2024, 3, 31),
            2025: date(2025, 4, 20),
            2026: date(2026, 4, 5),
            1818: date(1818, 3, 22),  # data mais cedo possível
            1943: date(1943, 4, 25),  # data mais tardia possível
        }
        for ano, esperado in conhecidos.items():
            with self.subTest(ano=ano):
                self.assertEqual(pascoa(ano), esperado)

    def test_sempre_domingo_e_dentro_da_janela(self) -> None:
        for ano in range(1583, 3000):
            p = pascoa(ano)
            self.assertEqual(p.weekday(), 6)
            self.assertGreaterEqual(p, date(ano, 3, 22))
            self.assertLessEqual(p, date(ano, 4, 25))

    def test_ano_anterior_ao_gregoriano(self) -> None:
        with self.assertRaises(ValueError):
            pascoa(1500)


if __name__ == "__main__":
    unittest.main()
