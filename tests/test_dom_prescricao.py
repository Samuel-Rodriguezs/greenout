import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_prescricao import (bienal_prescrita, inicio_periodo_exigivel,
                            limite_ajuizamento, parcela_prescrita, somar_anos)


class TestDomPrescricao(unittest.TestCase):
    def test_somar_anos(self):
        self.assertEqual(somar_anos(date(2022, 3, 10), 2), date(2024, 3, 10))
        self.assertEqual(somar_anos(date(2024, 2, 29), 1), date(2025, 2, 28))
        self.assertEqual(somar_anos(date(2024, 2, 29), 4), date(2028, 2, 29))
        self.assertEqual(somar_anos(date(2024, 5, 10), -5), date(2019, 5, 10))

    def test_limite_bienal(self):
        self.assertEqual(limite_ajuizamento(date(2022, 3, 10)), date(2024, 3, 10))

    def test_bienal_borda(self):
        ext = date(2022, 3, 10)
        self.assertFalse(bienal_prescrita(ext, date(2024, 3, 10)))
        self.assertTrue(bienal_prescrita(ext, date(2024, 3, 11)))

    def test_quinquenal_borda(self):
        aj = date(2024, 5, 10)
        self.assertEqual(inicio_periodo_exigivel(aj), date(2019, 5, 10))
        self.assertFalse(parcela_prescrita(date(2019, 5, 10), aj))
        self.assertTrue(parcela_prescrita(date(2019, 5, 9), aj))

    def test_prazo_parametrizado(self):
        self.assertTrue(parcela_prescrita(date(2022, 1, 1), date(2024, 5, 10), anos=2))


if __name__ == "__main__":
    unittest.main()
