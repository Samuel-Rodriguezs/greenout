import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_distribuicoes as d


class TestDistribuicoes(unittest.TestCase):
    def test_normal(self):
        self.assertAlmostEqual(d.normal_pdf(0), 0.3989423, places=6)
        self.assertAlmostEqual(d.normal_pdf(1, 1, 2), 0.3989423 / 2, places=6)
        self.assertAlmostEqual(d.normal_cdf(0), 0.5)
        self.assertAlmostEqual(d.normal_cdf(1.96), 0.9750021, places=6)
        self.assertAlmostEqual(d.normal_cdf(-1.96), 0.0249979, places=6)
        self.assertAlmostEqual(d.normal_cdf(110, 100, 10), d.normal_cdf(1), places=12)

    def test_ppf_inversa(self):
        self.assertAlmostEqual(d.normal_ppf(0.975), 1.959964, places=5)
        self.assertAlmostEqual(d.normal_cdf(d.normal_ppf(0.3, 5, 2), 5, 2), 0.3)

    def test_binomial(self):
        self.assertAlmostEqual(d.binomial_pmf(5, 10, 0.5), 252 / 1024)
        self.assertAlmostEqual(d.binomial_pmf(0, 3, 0.2), 0.512)
        self.assertEqual(d.binomial_pmf(4, 3, 0.2), 0.0)
        # P(X<=1) com n=3, p=0.5 = (1 + 3)/8
        self.assertAlmostEqual(d.binomial_cdf(1, 3, 0.5), 0.5)
        self.assertAlmostEqual(d.binomial_cdf(10, 3, 0.5), 1.0)
        self.assertEqual(d.binomial_media_variancia(10, 0.3), (3.0, 10 * 0.3 * 0.7))

    def test_poisson(self):
        self.assertAlmostEqual(d.poisson_pmf(0, 2), math.exp(-2))
        self.assertAlmostEqual(d.poisson_pmf(2, 2), 2 * math.exp(-2))
        self.assertAlmostEqual(d.poisson_cdf(2, 2), 5 * math.exp(-2))
        self.assertEqual(d.poisson_pmf(0, 0), 1.0)
        self.assertEqual(d.poisson_pmf(-1, 2), 0.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            d.normal_pdf(0, 0, 0)
        with self.assertRaises(ValueError):
            d.normal_ppf(1)
        with self.assertRaises(ValueError):
            d.binomial_pmf(1, 3, 1.5)
        with self.assertRaises(ValueError):
            d.poisson_pmf(1, -1)


if __name__ == "__main__":
    unittest.main()
