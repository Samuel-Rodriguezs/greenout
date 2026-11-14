import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_quantizacao as q
from sig_ondas import senoidal


class TestQuantizacao(unittest.TestCase):
    def test_1_bit(self):
        self.assertEqual(q.quantizar([-0.9, -0.1, 0.1, 0.9], 1), [-0.5, -0.5, 0.5, 0.5])

    def test_2_bits_niveis(self):
        self.assertEqual(q.quantizar([-1, -0.3, 0.3, 1], 2), [-0.75, -0.25, 0.25, 0.75])

    def test_saturacao(self):
        self.assertEqual(q.quantizar([5, -5], 2), [0.75, -0.75])

    def test_vmax(self):
        self.assertEqual(q.quantizar([1.9], 1, vmax=2), [1.0])

    def test_indices(self):
        self.assertEqual(q.indices([-1, -0.3, 0.3, 1], 2), [0, 1, 2, 3])

    def test_erro_limitado_a_meio_passo(self):
        x = senoidal(7, 1000, 1000)
        e = q.erro_de_quantizacao(x, q.quantizar(x, 8))
        self.assertLessEqual(max(abs(v) for v in e), 1 / 256 + 1e-12)

    def test_snr_cresce_6db_por_bit(self):
        x = senoidal(7, 1000, 1000)
        s8 = q.snr_db(x, q.quantizar(x, 8))
        s10 = q.snr_db(x, q.quantizar(x, 10))
        self.assertAlmostEqual(s10 - s8, 12.04, delta=1.5)
        self.assertAlmostEqual(s8, q.snr_teorico(8), delta=2.0)

    def test_snr_bordas(self):
        self.assertEqual(q.snr_db([1, 2], [1, 2]), math.inf)
        self.assertEqual(q.snr_db([0, 0], [1, 1]), -math.inf)
        self.assertAlmostEqual(q.snr_db([1, 1], [0, 0]), 0.0)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            q.quantizar([0], 0)
        with self.assertRaises(ValueError):
            q.quantizar([0], 4, vmax=0)
        with self.assertRaises(ValueError):
            q.snr_db([1], [1, 2])


if __name__ == "__main__":
    unittest.main()
