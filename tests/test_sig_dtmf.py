import cmath
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_dtmf as d
from sig_ondas import ruido_branco, senoidal

TAXA = 8000.0


class TestDTMF(unittest.TestCase):
    def test_frequencias(self):
        self.assertEqual(d.frequencias_da_tecla("1"), (697, 1209))
        self.assertEqual(d.frequencias_da_tecla("5"), (770, 1336))
        self.assertEqual(d.frequencias_da_tecla("#"), (941, 1477))
        self.assertEqual(d.frequencias_da_tecla("D"), (941, 1633))
        for ruim in ("E", "", "12"):
            with self.assertRaises(ValueError):
                d.frequencias_da_tecla(ruim)

    def test_goertzel_igual_dft(self):
        x = [math.sin(0.3 * i) + 0.5 * math.cos(1.1 * i) for i in range(64)]
        k = 5
        dft = sum(x[t] * cmath.exp(-2j * math.pi * k * t / 64) for t in range(64))
        self.assertAlmostEqual(d.goertzel(x, k * TAXA / 64, TAXA), abs(dft) ** 2, places=6)

    def test_goertzel_seleciona_frequencia(self):
        x = senoidal(770, TAXA, 800)
        self.assertGreater(d.goertzel(x, 770, TAXA), 1000 * d.goertzel(x, 852, TAXA))

    def test_todas_as_teclas(self):
        for linha in d.TECLAS:
            for t in linha:
                x = d.gerar_tecla(t, TAXA, 0.1)
                self.assertEqual(d.detectar_tecla(x, TAXA), t)

    def test_com_ruido(self):
        x = d.gerar_tecla("9", TAXA, 0.1)
        r = ruido_branco(len(x), amp=0.1, seed=5)
        y = [a + b for a, b in zip(x, r)]
        self.assertEqual(d.detectar_tecla(y, TAXA), "9")

    def test_silencio_ruido_e_tom_unico(self):
        self.assertIsNone(d.detectar_tecla([], TAXA))
        self.assertIsNone(d.detectar_tecla([0.0] * 800, TAXA))
        self.assertIsNone(d.detectar_tecla(ruido_branco(800, seed=2), TAXA))
        self.assertIsNone(d.detectar_tecla(senoidal(697, TAXA, 800), TAXA))

    def test_sequencia(self):
        x = d.gerar_sequencia("5551234*#", TAXA)
        self.assertEqual(d.decodificar_sequencia(x, TAXA), "5551234*#")

    def test_duracao(self):
        self.assertEqual(len(d.gerar_tecla("1", TAXA, 0.05)), 400)


if __name__ == "__main__":
    unittest.main()
