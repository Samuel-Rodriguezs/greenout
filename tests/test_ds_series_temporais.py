import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_series_temporais as s


class TestSeriesTemporais(unittest.TestCase):
    def test_diferenciar(self):
        self.assertEqual(s.diferenciar([1, 2, 4, 7]), [1, 2, 3])
        self.assertEqual(s.diferenciar([1, 2, 4, 7], ordem=2), [1, 1])
        self.assertEqual(s.diferenciar([1, 5, 2, 9, 4], lag=2), [1, 4, 2])

    def test_integrar_inverte(self):
        serie = [3, 5, 4, 10]
        self.assertEqual(s.integrar(s.diferenciar(serie), 3), [3, 5, 4, 10])

    def test_diferenciar_erros(self):
        with self.assertRaises(ValueError):
            s.diferenciar([1], 1)
        with self.assertRaises(ValueError):
            s.diferenciar([1, 2, 3], lag=0)

    def test_indices_sazonais(self):
        ind = s.indices_sazonais([10, 20, 10, 20, 10, 20], 2)
        self.assertAlmostEqual(ind[0], 2 / 3)
        self.assertAlmostEqual(ind[1], 4 / 3)
        self.assertAlmostEqual(sum(ind), 2.0)

    def test_dessazonalizar(self):
        r = s.dessazonalizar([10, 20, 10, 20], 2)
        for v in r:
            self.assertAlmostEqual(v, 15.0)

    def test_tendencia(self):
        a, b = s.tendencia_linear([1, 3, 5, 7])
        self.assertAlmostEqual(a, 1.0)
        self.assertAlmostEqual(b, 2.0)

    def test_autocorrelacao(self):
        self.assertAlmostEqual(s.autocorrelacao([1, 2, 3, 4, 5], 0), 1.0)
        self.assertAlmostEqual(s.autocorrelacao([1, 2, 3, 4, 5], 1), 0.4)
        self.assertAlmostEqual(s.autocorrelacao([1, 2, 3, 4, 5], 2), -0.1)

    def test_erros(self):
        with self.assertRaises(ValueError):
            s.indices_sazonais([1], 2)
        with self.assertRaises(ValueError):
            s.autocorrelacao([2, 2, 2], 1)
        with self.assertRaises(ValueError):
            s.tendencia_linear([1])


if __name__ == "__main__":
    unittest.main()
