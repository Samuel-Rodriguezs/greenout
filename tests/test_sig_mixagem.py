import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_mixagem as m


class TestMixagem(unittest.TestCase):
    def test_ganho_db(self):
        y = m.ganho_db([1.0, -2.0], 6.0206)
        self.assertAlmostEqual(y[0], 2.0, places=3)
        self.assertEqual(m.ganho_db([3.0], 0), [3.0])
        self.assertAlmostEqual(m.ganho_db([1.0], -20)[0], 0.1)

    def test_misturar_completa_com_zeros(self):
        self.assertEqual(m.misturar([[1, 1, 1], [2]]), [3, 1, 1])
        self.assertEqual(m.misturar([[1, 1], [1, 1]], [0.5, 2]), [2.5, 2.5])

    def test_misturar_erros(self):
        self.assertEqual(m.misturar([]), [])
        with self.assertRaises(ValueError):
            m.misturar([[1]], [1, 2])

    def test_normalizar(self):
        self.assertEqual(m.normalizar([0.25, -0.5]), [0.5, -1.0])
        self.assertEqual(m.normalizar([1, -2], 0.5), [0.25, -0.5])
        self.assertEqual(m.normalizar([0, 0]), [0, 0])
        self.assertEqual(m.normalizar([]), [])

    def test_remover_dc(self):
        self.assertEqual(m.remover_dc([3, 5, 7]), [-2, 0, 2])
        self.assertEqual(m.remover_dc([]), [])

    def test_fade_in_linear(self):
        self.assertEqual(m.fade_in([1] * 5, 5), [0, 0.25, 0.5, 0.75, 1])

    def test_fade_out_linear(self):
        self.assertEqual(m.fade_out([1] * 5, 3), [1, 1, 1, 0.5, 0])

    def test_fade_cosseno(self):
        y = m.fade_in([1] * 3, 3, "cosseno")
        self.assertAlmostEqual(y[1], 0.5)
        self.assertEqual(y[0], 0)

    def test_fade_bordas(self):
        self.assertEqual(m.fade_in([1, 1], 10), [0, 1])
        self.assertEqual(m.fade_in([1, 1], 0), [1, 1])
        with self.assertRaises(ValueError):
            m.fade_in([1], 1, "x")
        with self.assertRaises(ValueError):
            m.fade_out([1], -1)

    def test_crossfade(self):
        y = m.crossfade([1, 1, 1], [0, 0, 0], 2)
        self.assertEqual(len(y), 4)
        self.assertEqual(y[0], 1)
        self.assertAlmostEqual(y[1], 2 / 3)
        self.assertAlmostEqual(y[2], 1 / 3)
        self.assertEqual(y[3], 0)


if __name__ == "__main__":
    unittest.main()
