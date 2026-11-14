import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_pitch as p
from sig_ondas import dente_de_serra, ruido_branco, senoidal

TAXA = 8000.0


class TestPitch(unittest.TestCase):
    def test_seno_440(self):
        x = senoidal(440, TAXA, 1024)
        self.assertAlmostEqual(p.frequencia_fundamental(x, TAXA), 440, delta=1.5)

    def test_varias_frequencias(self):
        for f in (110, 220, 330, 660):
            x = senoidal(f, TAXA, 1024)
            self.assertAlmostEqual(p.frequencia_fundamental(x, TAXA), f, delta=f * 0.01)

    def test_dente_de_serra_ignora_harmonicos(self):
        x = dente_de_serra(200, TAXA, 1024)
        self.assertAlmostEqual(p.frequencia_fundamental(x, TAXA), 200, delta=2)

    def test_com_offset_dc(self):
        x = [v + 5 for v in senoidal(300, TAXA, 1024)]
        self.assertAlmostEqual(p.frequencia_fundamental(x, TAXA), 300, delta=3)

    def test_ruido_retorna_none(self):
        self.assertIsNone(p.frequencia_fundamental(ruido_branco(1024, seed=1), TAXA))

    def test_silencio_e_curto(self):
        self.assertIsNone(p.frequencia_fundamental([0.0] * 1000, TAXA))
        self.assertIsNone(p.frequencia_fundamental([1.0, 2.0], TAXA))

    def test_periodo(self):
        x = senoidal(400, TAXA, 1024)
        self.assertAlmostEqual(p.periodo_em_amostras(x, TAXA), 20, delta=0.2)

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            p.frequencia_fundamental([0.0] * 10, TAXA, fmin=500, fmax=100)


if __name__ == "__main__":
    unittest.main()
