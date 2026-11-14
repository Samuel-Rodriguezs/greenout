import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_descritiva as d


class TestDescritiva(unittest.TestCase):
    def test_basicos(self):
        x = [1, 2, 3, 4, 5]
        self.assertEqual(d.media(x), 3)
        self.assertEqual(d.mediana(x), 3)
        self.assertEqual(d.mediana([4, 1, 3, 2]), 2.5)
        self.assertAlmostEqual(d.variancia(x), 2.0)
        self.assertAlmostEqual(d.variancia(x, amostral=True), 2.5)
        self.assertAlmostEqual(d.desvio_padrao(x), 2 ** 0.5)

    def test_quartis_iqr(self):
        self.assertEqual(d.quartis([1, 2, 3, 4, 5]), (2, 3, 4))
        self.assertAlmostEqual(d.iqr([1, 2, 3, 4, 5]), 2)
        q1, q2, q3 = d.quartis([1, 2, 3, 4, 5, 100])
        self.assertAlmostEqual(q1, 2.25)
        self.assertAlmostEqual(q2, 3.5)
        self.assertAlmostEqual(q3, 4.75)

    def test_assimetria_curtose(self):
        x = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(d.assimetria(x), 0.0)
        self.assertAlmostEqual(d.curtose(x), -1.3)
        # m2 = 1.2, m3 = (-27 -1... ) calculado: [1,1,1,1,6]
        y = [1, 1, 1, 1, 6]
        # média 2, m2 = 4, m3 = (4*(-1) + 64)/5 = 12, g1 = 12/8 = 1.5
        self.assertAlmostEqual(d.assimetria(y), 1.5)
        # m4 = (4*1 + 256)/5 = 52, 52/16 - 3 = 0.25
        self.assertAlmostEqual(d.curtose(y), 0.25)

    def test_erros(self):
        with self.assertRaises(ValueError):
            d.media([])
        with self.assertRaises(ValueError):
            d.assimetria([2, 2, 2])
        with self.assertRaises(ValueError):
            d.variancia([1], amostral=True)

    def test_resumo(self):
        r = d.resumo([1, 2, 3, 4, 5])
        self.assertEqual(r["q1"], 2)
        self.assertAlmostEqual(r["desvio"], 2.5 ** 0.5)
        self.assertEqual(r["n"], 5)


if __name__ == "__main__":
    unittest.main()
