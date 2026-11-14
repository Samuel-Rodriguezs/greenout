import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_custas import (calcular_custas, calcular_custas_progressivas, custas_recurso,
                        percentual_da_faixa)


class TestCustas(unittest.TestCase):
    def test_faixas(self):
        self.assertEqual(percentual_da_faixa(D("10000")), D("1.0"))
        self.assertEqual(percentual_da_faixa(D("10000.01")), D("1.5"))
        self.assertEqual(percentual_da_faixa(D("999999")), D("2.5"))

    def test_calculo(self):
        self.assertEqual(calcular_custas(D("20000")), D("300.00"))
        self.assertEqual(calcular_custas(D("100000")), D("2000.00"))

    def test_minimo_e_maximo(self):
        self.assertEqual(calcular_custas(D("0")), D("50.00"))
        self.assertEqual(calcular_custas(D("1000")), D("50.00"))
        self.assertEqual(calcular_custas(D("1000000")), D("5000.00"))

    def test_progressivo(self):
        # 10000*1% + 10000*1.5% = 250
        self.assertEqual(calcular_custas_progressivas(D("20000")), D("250.00"))
        # exatamente no limite da primeira faixa
        self.assertEqual(calcular_custas_progressivas(D("10000")), D("100.00"))
        # 100 + 600 + 1.5*... : 10000*1% + 40000*1.5% + 50000*2% = 100+600+1000
        self.assertEqual(calcular_custas_progressivas(D("100000")), D("1700.00"))

    def test_progressivo_teto(self):
        self.assertEqual(calcular_custas_progressivas(D("5000000")), D("5000.00"))

    def test_recurso(self):
        self.assertEqual(custas_recurso(D("20000")), D("450.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            calcular_custas(D("-1"))
        with self.assertRaises(ValueError):
            calcular_custas(D("1"), minimo=D("10"), maximo=D("5"))
        with self.assertRaises(ValueError):
            calcular_custas_progressivas(D("-1"))

    def test_parametros_injetaveis(self):
        tab = [(None, D("10"))]
        self.assertEqual(calcular_custas(D("100"), D("0"), D("1000"), tab), D("10.00"))
        with self.assertRaises(ValueError):
            percentual_da_faixa(D("500"), [(D("100"), D("1"))])


if __name__ == "__main__":
    unittest.main()
