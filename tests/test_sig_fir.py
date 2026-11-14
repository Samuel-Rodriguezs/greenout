import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_fir as f

TAXA = 8000.0


class TestFIR(unittest.TestCase):
    def test_passa_baixa_ganho_dc_e_simetria(self):
        h = f.passa_baixa(1000, TAXA, 51)
        self.assertAlmostEqual(sum(h), 1.0)
        for a, b in zip(h, reversed(h)):
            self.assertAlmostEqual(a, b)

    def test_passa_baixa_resposta(self):
        h = f.passa_baixa(1000, TAXA, 101)
        self.assertGreater(f.resposta_em_frequencia(h, 200, TAXA), 0.99)
        self.assertLess(f.resposta_em_frequencia(h, 3000, TAXA), 0.01)
        self.assertAlmostEqual(f.resposta_em_frequencia(h, 1000, TAXA), 0.5, delta=0.1)

    def test_passa_alta(self):
        h = f.passa_alta(1000, TAXA, 101)
        self.assertAlmostEqual(sum(h), 0.0, places=9)
        self.assertLess(f.resposta_em_frequencia(h, 100, TAXA), 0.01)
        self.assertGreater(f.resposta_em_frequencia(h, 3000, TAXA), 0.99)

    def test_passa_banda(self):
        h = f.passa_banda(1000, 2000, TAXA, 151)
        self.assertGreater(f.resposta_em_frequencia(h, 1500, TAXA), 0.95)
        self.assertLess(f.resposta_em_frequencia(h, 200, TAXA), 0.02)
        self.assertLess(f.resposta_em_frequencia(h, 3500, TAXA), 0.02)

    def test_filtrar_impulso(self):
        h = [0.25, 0.5, 0.25]
        self.assertEqual(f.filtrar([1, 0, 0, 0], h), [0.25, 0.5, 0.25, 0])

    def test_filtrar_atenua_tom_alto(self):
        h = f.passa_baixa(500, TAXA, 101)
        x = [math.sin(2 * math.pi * 3000 * i / TAXA) for i in range(400)]
        y = f.filtrar(x, h)[200:]
        self.assertLess(max(abs(v) for v in y), 0.01)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            f.passa_baixa(1000, TAXA, 10)
        with self.assertRaises(ValueError):
            f.passa_baixa(5000, TAXA, 11)
        with self.assertRaises(ValueError):
            f.passa_banda(2000, 1000, TAXA, 11)


if __name__ == "__main__":
    unittest.main()
