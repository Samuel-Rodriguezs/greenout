import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_par_proximo import par_mais_proximo, par_mais_proximo_forca_bruta


class TestParProximo(unittest.TestCase):
    def test_dois_pontos(self):
        d, a, b = par_mais_proximo([(0, 0), (3, 4)])
        self.assertEqual(d, 5)
        self.assertEqual({a, b}, {(0, 0), (3, 4)})

    def test_exemplo_classico(self):
        pts = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
        d, a, b = par_mais_proximo(pts)
        self.assertAlmostEqual(d, 2 ** 0.5)
        self.assertEqual({a, b}, {(2, 3), (3, 4)})

    def test_pares_na_fronteira_da_divisao(self):
        pts = [(0, 0), (10, 0), (4.9, 5), (5.1, 5), (20, 20), (30, 1), (-9, 8)]
        d, a, b = par_mais_proximo(pts)
        self.assertAlmostEqual(d, 0.2)
        self.assertEqual({a, b}, {(4.9, 5), (5.1, 5)})

    def test_duplicatas_dao_zero(self):
        d, a, b = par_mais_proximo([(1, 1), (5, 5), (9, 2), (1, 1), (7, 7)])
        self.assertEqual(d, 0)
        self.assertEqual(a, b)

    def test_mesma_abscissa(self):
        d, _, _ = par_mais_proximo([(2, 0), (2, 10), (2, 11), (2, 30), (2, 50)])
        self.assertEqual(d, 1)

    def test_menos_de_dois(self):
        with self.assertRaises(ValueError):
            par_mais_proximo([(0, 0)])
        with self.assertRaises(ValueError):
            par_mais_proximo_forca_bruta([])

    def test_aleatorio_igual_forca_bruta(self):
        rng = random.Random(11)
        for _ in range(150):
            pts = [(rng.randint(0, 30), rng.randint(0, 30)) for _ in range(rng.randint(2, 40))]
            self.assertAlmostEqual(
                par_mais_proximo(pts)[0], par_mais_proximo_forca_bruta(pts)[0], msg=str(pts)
            )


if __name__ == "__main__":
    unittest.main()
