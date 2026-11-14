import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_inss import FAIXAS_EXEMPLO, aliquota_efetiva, calcular_inss

D = Decimal


class TestDomInss(unittest.TestCase):
    def test_primeira_faixa(self):
        self.assertEqual(calcular_inss("1000"), D("75.00"))

    def test_limite_primeira_faixa(self):
        self.assertEqual(calcular_inss("1412.00"), D("105.90"))

    def test_duas_faixas_e_meia(self):
        # 1412*7,5% + 1254,68*9% + 333,32*12% = 258,8196
        self.assertEqual(calcular_inss("3000"), D("258.82"))

    def test_teto(self):
        self.assertEqual(calcular_inss("7786.02"), D("908.86"))
        self.assertEqual(calcular_inss("10000"), D("908.86"))

    def test_zero(self):
        self.assertEqual(calcular_inss("0"), D("0.00"))

    def test_faixas_customizadas(self):
        faixas = ((D("1000"), D("0.10")), (D("2000"), D("0.20")))
        self.assertEqual(calcular_inss("1500", faixas), D("200.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            calcular_inss("-1")
        with self.assertRaises(ValueError):
            calcular_inss("100", ((D("100"), D("0.1")), (D("50"), D("0.2"))))

    def test_efetiva(self):
        self.assertEqual(aliquota_efetiva("0"), D(0))
        self.assertAlmostEqual(float(aliquota_efetiva("1000")), 0.075, places=6)
        self.assertEqual(len(FAIXAS_EXEMPLO), 4)


if __name__ == "__main__":
    unittest.main()
