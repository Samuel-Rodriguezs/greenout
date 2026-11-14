import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_salario_liquido import calcular_liquido

D = Decimal


class TestDomSalarioLiquido(unittest.TestCase):
    def test_tres_mil(self):
        h = calcular_liquido("3000")
        self.assertEqual(h.inss, D("258.82"))
        self.assertEqual(h.irrf, D("36.15"))
        self.assertEqual(h.liquido, D("2705.03"))

    def test_faixa_isenta_de_ir(self):
        h = calcular_liquido("2000")
        self.assertEqual(h.inss, D("158.82"))  # 105,90 + 588*9% = 52,92
        self.assertEqual(h.irrf, D("0.00"))

    def test_outros_descontos(self):
        h = calcular_liquido("3000", outros_descontos="100")
        self.assertEqual(h.liquido, D("2605.03"))

    def test_dependente_reduz_ir(self):
        self.assertLess(calcular_liquido("3000", 1).irrf, calcular_liquido("3000").irrf)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            calcular_liquido("-5")


if __name__ == "__main__":
    unittest.main()
