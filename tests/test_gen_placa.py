import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_placa as g
from dt_placa import antiga_para_mercosul as ref_conv
from dt_placa import tipo_placa, validar_placa


class TestGenPlaca(unittest.TestCase):
    def test_mercosul_valida(self):
        rng = random.Random(1)
        for _ in range(500):
            self.assertEqual(tipo_placa(g.gerar_placa_mercosul(rng)), "mercosul")

    def test_antiga_valida(self):
        rng = random.Random(2)
        for _ in range(500):
            self.assertEqual(tipo_placa(g.gerar_placa_antiga(rng)), "antiga")
            self.assertEqual(len(g.gerar_placa_antiga(rng, formatada=False)), 7)

    def test_conversao_concorda_com_modulo_existente(self):
        rng = random.Random(3)
        for _ in range(200):
            antiga = g.gerar_placa_antiga(rng)
            conv = g.antiga_para_mercosul(antiga)
            self.assertEqual(conv, ref_conv(antiga))
            self.assertEqual(tipo_placa(conv), "mercosul")

    def test_conversao_invalida(self):
        with self.assertRaises(ValueError):
            g.antiga_para_mercosul("ABC1D23")

    def test_lote(self):
        lote = g.gerar_lote(random.Random(4), 300)
        self.assertEqual(len(set(p.replace("-", "") for p in lote)), 300)
        self.assertTrue(all(validar_placa(p) for p in lote))
        self.assertEqual(lote, g.gerar_lote(random.Random(4), 300))

    def test_proporcao_extrema(self):
        tipos = {tipo_placa(p) for p in g.gerar_lote(random.Random(5), 50, 1.0)}
        self.assertEqual(tipos, {"mercosul"})
        tipos = {tipo_placa(p) for p in g.gerar_lote(random.Random(5), 50, 0.0)}
        self.assertEqual(tipos, {"antiga"})
        with self.assertRaises(ValueError):
            g.gerar_lote(random.Random(5), 1, 1.5)


if __name__ == "__main__":
    unittest.main()
