import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_horas_extras import (ADICIONAL_100, adicional_noturno,
                              horas_noturnas_computadas, valor_hora,
                              valor_horas_extras)

D = Decimal


class TestDomHorasExtras(unittest.TestCase):
    def test_valor_hora(self):
        self.assertEqual(valor_hora("2200"), D(10))

    def test_extras_50(self):
        self.assertEqual(valor_horas_extras("2200", 10), D("150.00"))

    def test_extras_100(self):
        self.assertEqual(valor_horas_extras("2200", 10, ADICIONAL_100), D("200.00"))

    def test_extras_fracionadas(self):
        self.assertEqual(valor_horas_extras("2200", "1.5"), D("22.50"))

    def test_zero(self):
        self.assertEqual(valor_horas_extras("2200", 0), D("0.00"))

    def test_noturno(self):
        self.assertEqual(adicional_noturno("2200", 10), D("20.00"))

    def test_hora_reduzida(self):
        self.assertEqual(horas_noturnas_computadas(7), D(8))
        self.assertEqual(horas_noturnas_computadas(0), D(0))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            valor_horas_extras("2200", -1)
        with self.assertRaises(ValueError):
            valor_hora("2200", D(0))
        with self.assertRaises(ValueError):
            adicional_noturno("2200", -2)


if __name__ == "__main__":
    unittest.main()
