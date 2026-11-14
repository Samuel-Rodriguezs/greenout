import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_delta_mulaw as d
from sig_ondas import senoidal
from sig_quantizacao import quantizar, snr_db


class TestDelta(unittest.TestCase):
    def test_dpcm(self):
        self.assertEqual(d.delta_codificar([10, 12, 11, 15]), [10, 2, -1, 4])
        self.assertEqual(d.delta_decodificar([10, 2, -1, 4]), [10, 12, 11, 15])

    def test_dpcm_vazio_e_ida_volta(self):
        self.assertEqual(d.delta_codificar([]), [])
        x = [0, 5, -3, -3, 100]
        self.assertEqual(d.delta_decodificar(d.delta_codificar(x)), x)

    def test_delta_1bit(self):
        self.assertEqual(d.delta_1bit_codificar([1, 2, 3, 3, 0], 1), [1, 1, 1, 0, 0])
        self.assertEqual(d.delta_1bit_decodificar([1, 1, 1, 0, 0], 1), [1, 2, 3, 2, 1])

    def test_delta_1bit_segue_rampa(self):
        x = [0.5 * i for i in range(1, 20)]
        rec = d.delta_1bit_decodificar(d.delta_1bit_codificar(x, 0.5), 0.5)
        self.assertEqual(rec, x)

    def test_delta_1bit_passo_invalido(self):
        with self.assertRaises(ValueError):
            d.delta_1bit_codificar([1], 0)
        with self.assertRaises(ValueError):
            d.delta_1bit_decodificar([1], -1)


class TestMuLaw(unittest.TestCase):
    def test_extremos_e_zero(self):
        self.assertAlmostEqual(d.mulaw_comprimir(1.0), 1.0)
        self.assertAlmostEqual(d.mulaw_comprimir(-1.0), -1.0)
        self.assertEqual(d.mulaw_comprimir(0.0), 0.0)

    def test_valor_conhecido(self):
        # ln(1+255*0.5)/ln(256)
        self.assertAlmostEqual(d.mulaw_comprimir(0.5), 0.8761, places=3)

    def test_inversa(self):
        for x in (-1, -0.37, -0.001, 0, 0.02, 0.5, 1):
            self.assertAlmostEqual(d.mulaw_expandir(d.mulaw_comprimir(x)), x, places=9)

    def test_fora_da_faixa(self):
        with self.assertRaises(ValueError):
            d.mulaw_comprimir(1.5)
        with self.assertRaises(ValueError):
            d.mulaw_expandir(-2)
        with self.assertRaises(ValueError):
            d.mulaw_decodificar([256])

    def test_codigos_8_bits(self):
        c = d.mulaw_codificar([-1, 0, 1])
        self.assertEqual((c[0], c[2]), (0, 255))
        self.assertIn(c[1], (127, 128))

    def test_melhor_que_linear_em_sinal_fraco(self):
        x = senoidal(7, 1000, 1000, amp=0.02)
        mu = d.mulaw_decodificar(d.mulaw_codificar(x))
        lin = quantizar(x, 8)
        self.assertGreater(snr_db(x, mu), snr_db(x, lin) + 10)

    def test_codificar_bits_invalido(self):
        with self.assertRaises(ValueError):
            d.mulaw_codificar([0.0], 0)


if __name__ == "__main__":
    unittest.main()
