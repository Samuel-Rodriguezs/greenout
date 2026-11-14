import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_correcao import (corrigir_por_indices, corrigir_por_variacoes,
                          fator_acumulado, variacao_acumulada_percentual)

D = Decimal


class TestDomCorrecao(unittest.TestCase):
    def test_variacoes(self):
        # 1,01 * 1,005 = 1,01505
        self.assertEqual(corrigir_por_variacoes("1000", ["1.0", "0.5"]), D("1015.05"))
        self.assertEqual(fator_acumulado(["1.0", "0.5"]), D("1.01505"))

    def test_sem_variacoes(self):
        self.assertEqual(corrigir_por_variacoes("123.45", []), D("123.45"))

    def test_deflacao(self):
        self.assertEqual(corrigir_por_variacoes("1000", ["-10"]), D("900.00"))

    def test_indices(self):
        self.assertEqual(corrigir_por_indices("200", "100", "150"), D("300.00"))
        self.assertEqual(corrigir_por_indices("100", "3", "4"), D("133.33"))

    def test_acumulada(self):
        self.assertEqual(variacao_acumulada_percentual(["10", "10"]), D("21"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            fator_acumulado(["-100"])
        with self.assertRaises(ValueError):
            corrigir_por_indices("10", "0", "5")


if __name__ == "__main__":
    unittest.main()
