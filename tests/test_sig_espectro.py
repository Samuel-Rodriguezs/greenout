import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_espectro as e


def seno(k, n, amp=1.0, fase=0.0):
    return [amp * math.sin(2 * math.pi * k * i / n + fase) for i in range(n)]


class TestEspectro(unittest.TestCase):
    def test_magnitude_bin_exato(self):
        m = e.magnitude(seno(4, 64, amp=2.5))
        self.assertAlmostEqual(m[4], 2.5, places=9)
        self.assertAlmostEqual(m[3], 0.0, places=9)
        self.assertEqual(len(m), 33)

    def test_dc(self):
        m = e.magnitude([3.0] * 8)
        self.assertAlmostEqual(m[0], 3.0)
        self.assertAlmostEqual(m[1], 0.0)

    def test_fase_cosseno_e_seno(self):
        n = 32
        cos = [math.cos(2 * math.pi * 3 * i / n) for i in range(n)]
        self.assertAlmostEqual(e.fase(cos)[3], 0.0, places=9)
        self.assertAlmostEqual(e.fase(seno(3, n))[3], -math.pi / 2, places=9)

    def test_frequencias(self):
        self.assertEqual(e.frequencias(8, 8000), [0, 1000, 2000, 3000, 4000])
        with self.assertRaises(ValueError):
            e.frequencias(0, 100)

    def test_dominante(self):
        taxa = 1024
        x = [math.sin(2 * math.pi * 100 * i / taxa) + 0.3 * math.sin(2 * math.pi * 300 * i / taxa)
             for i in range(taxa)]
        self.assertAlmostEqual(e.frequencia_dominante(x, taxa), 100.0)

    def test_dominante_curto(self):
        with self.assertRaises(ValueError):
            e.frequencia_dominante([1.0], 100)

    def test_db(self):
        db = e.magnitude_db(seno(2, 16, amp=1.0))
        self.assertAlmostEqual(db[2], 0.0, places=6)
        self.assertAlmostEqual(db[5], -240.0, places=3)


if __name__ == "__main__":
    unittest.main()
