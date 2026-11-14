import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_duplicata import descontar_duplicata

D = Decimal


class TestDomDuplicata(unittest.TestCase):
    def test_basico(self):
        r = descontar_duplicata("10000", "0.03", 60)
        self.assertEqual(r.desconto, D("600.00"))
        self.assertEqual(r.liquido, D("9400.00"))
        self.assertAlmostEqual(float(r.taxa_efetiva_periodo), 10000 / 9400 - 1, places=9)

    def test_com_iof_e_tarifa(self):
        # IOF: 10000 * (0,000082*60 + 0,0038) = 87,20
        r = descontar_duplicata("10000", "0.03", 60, "0.000082", "0.0038", "15")
        self.assertEqual(r.iof, D("87.20"))
        self.assertEqual(r.tarifa, D("15.00"))
        self.assertEqual(r.liquido, D("9297.80"))

    def test_zero_dias(self):
        r = descontar_duplicata("500", "0.05", 0)
        self.assertEqual(r.liquido, D("500.00"))
        self.assertEqual(r.taxa_efetiva_periodo, D(0))

    def test_um_dia(self):
        self.assertEqual(descontar_duplicata("3000", "0.03", 1).desconto, D("3.00"))

    def test_encargos_excessivos(self):
        with self.assertRaises(ValueError):
            descontar_duplicata("100", "0.5", 60)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            descontar_duplicata("0", "0.03", 10)
        with self.assertRaises(ValueError):
            descontar_duplicata("100", "0.03", -1)


if __name__ == "__main__":
    unittest.main()
