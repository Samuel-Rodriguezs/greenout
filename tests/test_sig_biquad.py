import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_biquad as b

TAXA = 48000.0


class TestBiquad(unittest.TestCase):
    def test_1a_ordem_ganho_dc_e_corte(self):
        f = b.passa_baixa_1a_ordem(1000, TAXA)
        self.assertAlmostEqual(f.ganho(1e-3, TAXA), 1.0, places=6)
        self.assertAlmostEqual(f.ganho(1000, TAXA), 1 / math.sqrt(2), places=2)
        self.assertLess(f.ganho(20000, TAXA), 0.1)

    def test_1a_ordem_passa_alta(self):
        f = b.passa_alta_1a_ordem(1000, TAXA)
        self.assertLess(f.ganho(10, TAXA), 0.02)
        self.assertAlmostEqual(f.ganho(1000, TAXA), 1 / math.sqrt(2), places=2)
        self.assertAlmostEqual(f.ganho(23000, TAXA), 1.0, delta=0.01)

    def test_biquad_passa_baixa_butterworth(self):
        f = b.passa_baixa(1000, TAXA)
        self.assertAlmostEqual(f.ganho(1000, TAXA), 1 / math.sqrt(2), places=3)
        self.assertAlmostEqual(f.ganho(10, TAXA), 1.0, places=3)
        self.assertLess(f.ganho(10000, TAXA), 0.02)

    def test_biquad_passa_alta(self):
        f = b.passa_alta(1000, TAXA)
        self.assertAlmostEqual(f.ganho(1000, TAXA), 1 / math.sqrt(2), places=3)
        self.assertLess(f.ganho(50, TAXA), 0.01)

    def test_passa_banda_pico(self):
        f = b.passa_banda(2000, TAXA, q=5)
        self.assertAlmostEqual(f.ganho(2000, TAXA), 1.0, places=6)
        self.assertLess(f.ganho(500, TAXA), 0.2)

    def test_notch(self):
        f = b.rejeita_faixa(1000, TAXA, q=10)
        self.assertAlmostEqual(f.ganho(1000, TAXA), 0.0, places=6)
        self.assertAlmostEqual(f.ganho(100, TAXA), 1.0, delta=0.01)

    def test_resposta_ao_degrau_converge_ao_ganho_dc(self):
        f = b.passa_baixa(500, TAXA)
        y = f.filtrar([1.0] * 3000)
        self.assertAlmostEqual(y[-1], 1.0, places=6)

    def test_domino_temporal_coerente_com_ganho(self):
        f = b.passa_baixa(1000, TAXA)
        x = [math.sin(2 * math.pi * 5000 * i / TAXA) for i in range(2000)]
        y = f.filtrar(x)
        self.assertAlmostEqual(max(abs(v) for v in y[1000:]), f.ganho(5000, TAXA), places=3)

    def test_resetar(self):
        f = b.passa_baixa(1000, TAXA)
        a = f.filtrar([1, 0, 0])
        f.resetar()
        self.assertEqual(f.filtrar([1, 0, 0]), a)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            b.passa_baixa(30000, TAXA)
        with self.assertRaises(ValueError):
            b.passa_baixa(1000, TAXA, q=0)


if __name__ == "__main__":
    unittest.main()
