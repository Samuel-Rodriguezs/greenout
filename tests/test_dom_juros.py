import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_juros import (juros_compostos, juros_simples, montante_composto,
                       montante_simples, taxa_equivalente)

D = Decimal


class TestDomJuros(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(juros_simples("1000", "0.05", 3), D("150.00"))
        self.assertEqual(montante_simples("1000", "0.05", 3), D("1150.00"))

    def test_composto(self):
        self.assertEqual(montante_composto("1000", "0.10", 2), D("1210.00"))
        self.assertEqual(montante_composto("1000", "0.01", 3), D("1030.30"))
        self.assertEqual(juros_compostos("1000", "0.10", 2), D("210.00"))

    def test_zero_periodos(self):
        self.assertEqual(montante_composto("500", "0.1", 0), D("500.00"))
        self.assertEqual(juros_simples("500", "0.1", 0), D("0.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            juros_simples("-1", "0.1", 1)
        with self.assertRaises(ValueError):
            montante_composto("1", "0.1", -1)

    def test_taxa_equivalente(self):
        anual = taxa_equivalente("0.01", 1, 12)
        self.assertAlmostEqual(float(anual), 0.126825, places=6)
        self.assertAlmostEqual(float(taxa_equivalente(anual, 12, 1)), 0.01, places=9)
        with self.assertRaises(ValueError):
            taxa_equivalente("0.1", 0, 1)


if __name__ == "__main__":
    unittest.main()
