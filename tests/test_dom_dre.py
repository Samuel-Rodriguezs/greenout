import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_dre import montar_dre

D = Decimal


class TestDomDre(unittest.TestCase):
    def test_completa(self):
        r = montar_dre("100000", "0.10", "40000", "20000", "-2000", "0.20")
        self.assertEqual(r.deducoes, D("10000.00"))
        self.assertEqual(r.receita_liquida, D("90000.00"))
        self.assertEqual(r.lucro_bruto, D("50000.00"))
        self.assertEqual(r.resultado_operacional, D("30000.00"))
        self.assertEqual(r.lair, D("28000.00"))
        self.assertEqual(r.imposto_renda, D("5600.00"))
        self.assertEqual(r.lucro_liquido, D("22400.00"))

    def test_margens(self):
        r = montar_dre("100000", "0.10", "40000", "20000", "-2000", "0.20")
        self.assertAlmostEqual(float(r.margem_bruta), 50000 / 90000, places=9)
        self.assertAlmostEqual(float(r.margem_liquida), 22400 / 90000, places=9)

    def test_prejuizo_sem_imposto(self):
        r = montar_dre("1000", "0", "900", "300", "0", "0.30")
        self.assertEqual(r.lair, D("-200.00"))
        self.assertEqual(r.imposto_renda, D("0.00"))
        self.assertEqual(r.lucro_liquido, D("-200.00"))

    def test_receita_zero(self):
        r = montar_dre("0", "0.1", "0", "0")
        self.assertEqual(r.margem_liquida, D(0))
        self.assertEqual(r.lucro_liquido, D("0.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            montar_dre("-1", "0", "0", "0")
        with self.assertRaises(ValueError):
            montar_dre("1", "1.5", "0", "0")
        with self.assertRaises(ValueError):
            montar_dre("1", "0", "0", "0", "0", "-0.1")


if __name__ == "__main__":
    unittest.main()
