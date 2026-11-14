import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_vpl import vale_a_pena, vpl

D = Decimal


class TestDomVpl(unittest.TestCase):
    def test_vpl(self):
        self.assertEqual(vpl("0.10", [-1000, 600, 600]), D("41.32"))

    def test_taxa_zero_soma_simples(self):
        self.assertEqual(vpl("0", [-1000, 600, 600]), D("200.00"))

    def test_so_investimento(self):
        self.assertEqual(vpl("0.1", [-500]), D("-500.00"))

    def test_decisao(self):
        self.assertTrue(vale_a_pena("0.10", [-1000, 600, 600]))
        self.assertFalse(vale_a_pena("0.20", [-1000, 600, 600]))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            vpl("0.1", [])
        with self.assertRaises(ValueError):
            vpl("-1", [1, 2])


if __name__ == "__main__":
    unittest.main()
