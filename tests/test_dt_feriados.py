import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import dt_feriados as f


class TestFeriados(unittest.TestCase):
    def test_moveis_2024(self) -> None:
        self.assertEqual(f.carnaval(2024), (date(2024, 2, 12), date(2024, 2, 13)))
        self.assertEqual(f.sexta_feira_santa(2024), date(2024, 3, 29))
        self.assertEqual(f.corpus_christi(2024), date(2024, 5, 30))

    def test_moveis_2026(self) -> None:
        self.assertEqual(f.carnaval(2026)[1], date(2026, 2, 17))
        self.assertEqual(f.sexta_feira_santa(2026), date(2026, 4, 3))
        self.assertEqual(f.corpus_christi(2026), date(2026, 6, 4))

    def test_quantidade_e_ordem(self) -> None:
        f23 = f.feriados_nacionais(2023)
        self.assertEqual(len(f23), 9)  # 8 fixos + sexta santa
        f24 = f.feriados_nacionais(2024)
        self.assertEqual(len(f24), 10)  # inclui Consciência Negra
        self.assertEqual(list(f24), sorted(f24))

    def test_facultativos(self) -> None:
        sem = f.feriados_nacionais(2025)
        com = f.feriados_nacionais(2025, incluir_facultativos=True)
        self.assertEqual(len(com) - len(sem), 3)
        self.assertEqual(com[date(2025, 6, 19)], "Corpus Christi")
        self.assertNotIn(date(2025, 6, 19), sem)

    def test_consciencia_negra_so_a_partir_de_2024(self) -> None:
        self.assertFalse(f.eh_feriado(date(2023, 11, 20)))
        self.assertTrue(f.eh_feriado(date(2024, 11, 20)))

    def test_eh_feriado(self) -> None:
        self.assertTrue(f.eh_feriado(date(2026, 12, 25)))
        self.assertFalse(f.eh_feriado(date(2026, 12, 24)))
        self.assertFalse(f.eh_feriado(date(2026, 2, 17)))
        self.assertTrue(f.eh_feriado(date(2026, 2, 17), incluir_facultativos=True))


if __name__ == "__main__":
    unittest.main()
