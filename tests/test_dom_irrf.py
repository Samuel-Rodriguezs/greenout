import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_irrf import calcular_irrf, irrf_sobre_base

D = Decimal


class TestDomIrrf(unittest.TestCase):
    def test_isento(self):
        self.assertEqual(irrf_sobre_base("2000"), D("0.00"))
        self.assertEqual(irrf_sobre_base("2259.20"), D("0.00"))

    def test_faixas(self):
        self.assertEqual(irrf_sobre_base("2500"), D("18.06"))   # 187,5 - 169,44
        self.assertEqual(irrf_sobre_base("3000"), D("68.56"))   # 450 - 381,44
        self.assertEqual(irrf_sobre_base("4000"), D("237.23"))  # 900 - 662,77
        self.assertEqual(irrf_sobre_base("5000"), D("479.00"))  # 1375 - 896

    def test_limite_exato(self):
        self.assertEqual(irrf_sobre_base("3751.05"), D("181.22"))  # 562,6575-381,44 = 181,2175

    def test_dependente(self):
        # base 3000 - 189,59 = 2810,41 -> 7,5%: 210,78075 - 169,44
        self.assertEqual(calcular_irrf("3000", 0, 1), D("41.34"))

    def test_inss_abate_base(self):
        self.assertEqual(calcular_irrf("3000", "258.82"), D("36.15"))

    def test_base_zero_ou_negativa(self):
        self.assertEqual(irrf_sobre_base("0"), D("0.00"))
        self.assertEqual(calcular_irrf("500", 0, 3), D("0.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            calcular_irrf("1000", 0, -1)
        with self.assertRaises(ValueError):
            calcular_irrf("-1")


if __name__ == "__main__":
    unittest.main()
