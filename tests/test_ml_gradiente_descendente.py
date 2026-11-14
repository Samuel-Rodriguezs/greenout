import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_gradiente_descendente import descer, gradiente_numerico


class TestGradienteDescendente(unittest.TestCase):
    def test_parabola_1d(self):
        x, _ = descer(lambda p: (p[0] - 3) ** 2, [0.0], grad=lambda p: [2 * (p[0] - 3)])
        self.assertAlmostEqual(x[0], 3.0, places=4)

    def test_quadratica_2d_numerico(self):
        f = lambda p: (p[0] - 1) ** 2 + 2 * (p[1] + 2) ** 2
        x, _ = descer(f, [5.0, 5.0], taxa=0.1, tol=1e-6)
        self.assertAlmostEqual(x[0], 1.0, places=3)
        self.assertAlmostEqual(x[1], -2.0, places=3)

    def test_gradiente_numerico(self):
        g = gradiente_numerico(lambda p: p[0] ** 2 + 3 * p[1], [2.0, 1.0])
        self.assertAlmostEqual(g[0], 4.0, places=4)
        self.assertAlmostEqual(g[1], 3.0, places=4)

    def test_momento_converge(self):
        f = lambda p: p[0] ** 2
        x, _ = descer(f, [10.0], grad=lambda p: [2 * p[0]], taxa=0.05, momento=0.8, tol=1e-6)
        self.assertAlmostEqual(x[0], 0.0, places=3)

    def test_taxa_invalida(self):
        with self.assertRaises(ValueError):
            descer(lambda p: p[0] ** 2, [1.0], taxa=0)

    def test_ja_no_minimo(self):
        _, it = descer(lambda p: p[0] ** 2, [0.0], grad=lambda p: [2 * p[0]])
        self.assertEqual(it, 1)

    def test_divergencia_limitada_por_max_iter(self):
        _, it = descer(lambda p: p[0] ** 2, [1.0], grad=lambda p: [2 * p[0]], taxa=0.001, max_iter=5)
        self.assertEqual(it, 5)


if __name__ == "__main__":
    unittest.main()
