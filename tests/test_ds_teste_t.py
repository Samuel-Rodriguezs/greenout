import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_teste_t import t_cdf, t_ppf, t_student, t_welch


class TestTesteT(unittest.TestCase):
    def test_cdf_exata(self):
        self.assertAlmostEqual(t_cdf(0, 5), 0.5)
        # gl=1 (Cauchy): cdf(1) = 0.75
        self.assertAlmostEqual(t_cdf(1, 1), 0.75, places=10)
        # gl=2: cdf(t) = 0.5 + t / (2 sqrt(2 + t^2))
        self.assertAlmostEqual(t_cdf(1, 2), 0.5 + 1 / (2 * 3 ** 0.5), places=10)
        self.assertAlmostEqual(t_cdf(-1, 2), 0.5 - 1 / (2 * 3 ** 0.5), places=10)

    def test_ppf(self):
        self.assertAlmostEqual(t_ppf(0.975, 10), 2.2281, places=3)
        self.assertAlmostEqual(t_ppf(0.975, 4), 2.7764, places=3)
        self.assertAlmostEqual(t_ppf(0.5, 7), 0.0, places=6)

    def test_student(self):
        a, b = [1, 2, 3, 4, 5], [3, 4, 5, 6, 7]
        r = t_student(a, b)
        self.assertAlmostEqual(r.t, -2.0)
        self.assertEqual(r.gl, 8)
        self.assertAlmostEqual(r.p_valor, 0.0805, delta=0.001)

    def test_welch_variancias_iguais_coincide(self):
        a, b = [1, 2, 3, 4, 5], [3, 4, 5, 6, 7]
        w, s = t_welch(a, b), t_student(a, b)
        self.assertAlmostEqual(w.t, s.t)
        self.assertAlmostEqual(w.gl, 8.0)
        self.assertAlmostEqual(w.p_valor, s.p_valor, places=8)

    def test_welch_gl(self):
        # va = 2.5 (n=5), vb = 10 (n=5): ea=0.5, eb=2
        a, b = [1, 2, 3, 4, 5], [2, 4, 6, 8, 10]
        r = t_welch(a, b)
        self.assertAlmostEqual(r.gl, 2.5 ** 2 / (0.25 / 4 + 4 / 4))
        self.assertAlmostEqual(r.t, (3 - 6) / 2.5 ** 0.5)

    def test_amostras_iguais(self):
        r = t_student([1, 2, 3], [1, 2, 3])
        self.assertAlmostEqual(r.t, 0.0)
        self.assertAlmostEqual(r.p_valor, 1.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            t_welch([1], [1, 2])
        with self.assertRaises(ValueError):
            t_student([2, 2], [2, 2])
        with self.assertRaises(ValueError):
            t_cdf(1, 0)


if __name__ == "__main__":
    unittest.main()
