import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_regressao_multipla import ajustar


class TestRegressaoMultipla(unittest.TestCase):
    def test_ajuste_exato(self):
        # y = 1 + 2*x1 + 3*x2
        X = [(1, 1), (2, 1), (1, 2), (2, 3), (3, 2)]
        y = [6, 8, 9, 14, 13]
        m = ajustar(X, y)
        self.assertAlmostEqual(m.intercepto, 1.0)
        self.assertAlmostEqual(m.coeficientes[0], 2.0)
        self.assertAlmostEqual(m.coeficientes[1], 3.0)
        self.assertAlmostEqual(m.r2, 1.0)
        self.assertAlmostEqual(m.prever((4, 5)), 24.0)

    def test_simples_com_ruido(self):
        # pontos (1,2),(2,3),(3,5): b1 = 1.5, b0 = 1/3 ; SSE = 1/6, SST = 14/3
        m = ajustar([(1,), (2,), (3,)], [2, 3, 5])
        self.assertAlmostEqual(m.coeficientes[0], 1.5)
        self.assertAlmostEqual(m.intercepto, 1 / 3)
        self.assertAlmostEqual(m.r2, 1 - (1 / 6) / (14 / 3))

    def test_colinear(self):
        X = [(1, 2), (2, 4), (3, 6), (4, 8)]
        with self.assertRaises(ValueError):
            ajustar(X, [1, 2, 3, 4])

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            ajustar([(1,), (2,)], [1])
        with self.assertRaises(ValueError):
            ajustar([(1, 2), (3, 4)], [1, 2])
        with self.assertRaises(ValueError):
            ajustar([(1, 2), (3,), (4, 5)], [1, 2, 3])

    def test_prever_dimensao(self):
        m = ajustar([(1,), (2,), (3,)], [2, 3, 5])
        with self.assertRaises(ValueError):
            m.prever((1, 2))


if __name__ == "__main__":
    unittest.main()
