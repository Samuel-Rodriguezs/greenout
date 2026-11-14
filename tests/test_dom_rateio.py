import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_rateio import ratear, ratear_igualmente

D = Decimal


class TestDomRateio(unittest.TestCase):
    def test_igual_com_sobra(self):
        self.assertEqual(ratear_igualmente("100.00", 3),
                         [D("33.34"), D("33.33"), D("33.33")])

    def test_proporcional(self):
        self.assertEqual(ratear("100", [1, 2]), [D("33.33"), D("66.67")])

    def test_exato(self):
        self.assertEqual(ratear("300", [1, 1, 1]), [D("100"), D("100"), D("100")])

    def test_soma_preservada(self):
        partes = ratear("1000.01", [3, 5, 7, 11, 13])
        self.assertEqual(sum(partes), D("1000.01"))

    def test_peso_zero(self):
        self.assertEqual(ratear("10", [0, 1]), [D("0"), D("10")])

    def test_pesos_decimais(self):
        self.assertEqual(ratear("10", ["0.5", "0.5"]), [D("5"), D("5")])

    def test_total_zero(self):
        self.assertEqual(ratear("0", [1, 2]), [D("0"), D("0")])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            ratear("10", [])
        with self.assertRaises(ValueError):
            ratear("10", [0, 0])
        with self.assertRaises(ValueError):
            ratear("10", [-1, 2])
        with self.assertRaises(ValueError):
            ratear("10.005", [1])
        with self.assertRaises(ValueError):
            ratear_igualmente("10", 0)


if __name__ == "__main__":
    unittest.main()
