import math
import random
import statistics
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_dinheiro as g


class TestGenDinheiro(unittest.TestCase):
    def test_determinismo(self):
        self.assertEqual(g.gerar_lote(random.Random(1), 100), g.gerar_lote(random.Random(1), 100))

    def test_mediana_e_assimetria(self):
        v = g.gerar_lote(random.Random(2), 20000, mediana=200.0, sigma=0.7)
        med = statistics.median(v) / 100
        self.assertAlmostEqual(med, 200.0, delta=8.0)
        self.assertGreater(statistics.mean(v), statistics.median(v))  # cauda à direita
        logs = [math.log(x / 100) for x in v]
        self.assertAlmostEqual(statistics.stdev(logs), 0.7, delta=0.03)

    def test_truncamento(self):
        v = g.gerar_lote(random.Random(3), 2000, mediana=50.0, sigma=1.0, minimo=1000, maximo=20000)
        self.assertTrue(all(1000 <= x <= 20000 for x in v))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            g.gerar_centavos(random.Random(0), mediana=-1)
        with self.assertRaises(ValueError):
            g.gerar_centavos(random.Random(0), minimo=10, maximo=5)
        with self.assertRaises(RuntimeError):
            g.gerar_centavos(random.Random(0), mediana=1.0, sigma=0.01, minimo=10**9)

    def test_formatar_brl(self):
        self.assertEqual(g.formatar_brl(123456), "R$ 1.234,56")
        self.assertEqual(g.formatar_brl(5), "R$ 0,05")
        self.assertEqual(g.formatar_brl(-100000000), "-R$ 1.000.000,00")

    def test_decimal(self):
        self.assertEqual(g.para_decimal(1999), Decimal("19.99"))


if __name__ == "__main__":
    unittest.main()
