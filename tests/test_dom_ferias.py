import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_ferias import calcular_ferias, dias_de_direito, ferias_proporcionais

D = Decimal


class TestDomFerias(unittest.TestCase):
    def test_trinta_dias(self):
        f = calcular_ferias("3000")
        self.assertEqual(f.valor_ferias, D("3000.00"))
        self.assertEqual(f.terco, D("1000.00"))
        self.assertEqual(f.total, D("4000.00"))

    def test_com_abono(self):
        f = calcular_ferias("3000", 30, 10)
        self.assertEqual(f.dias_gozados, 20)
        self.assertEqual(f.valor_ferias, D("2000.00"))
        self.assertEqual(f.terco, D("666.67"))
        self.assertEqual(f.abono, D("1000.00"))
        self.assertEqual(f.terco_abono, D("333.33"))
        self.assertEqual(f.total, D("4000.00"))

    def test_abono_excede_limite(self):
        with self.assertRaises(ValueError):
            calcular_ferias("3000", 30, 11)

    def test_tabela_faltas(self):
        self.assertEqual(dias_de_direito(0), 30)
        self.assertEqual(dias_de_direito(5), 30)
        self.assertEqual(dias_de_direito(6), 24)
        self.assertEqual(dias_de_direito(14), 24)
        self.assertEqual(dias_de_direito(15), 18)
        self.assertEqual(dias_de_direito(24), 12)
        self.assertEqual(dias_de_direito(33), 0)
        with self.assertRaises(ValueError):
            dias_de_direito(-1)

    def test_proporcionais(self):
        self.assertEqual(ferias_proporcionais("3000", 6), D("2000.00"))
        self.assertEqual(ferias_proporcionais("3000", 0), D("0.00"))
        with self.assertRaises(ValueError):
            ferias_proporcionais("3000", 13)


if __name__ == "__main__":
    unittest.main()
