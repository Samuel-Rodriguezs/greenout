import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_percentis as p

DADOS = [15, 20, 35, 40, 50]


class TestPercentis(unittest.TestCase):
    def test_linear(self):
        self.assertAlmostEqual(p.percentil(DADOS, 0), 15)
        self.assertAlmostEqual(p.percentil(DADOS, 40), 29.0)  # pos 1.6: 20 + 0.6*15
        self.assertAlmostEqual(p.percentil(DADOS, 50), 35)
        self.assertAlmostEqual(p.percentil(DADOS, 100), 50)
        self.assertAlmostEqual(p.percentil([3, 1, 2, 4], 25), 1.75)

    def test_posto_proximo(self):
        self.assertEqual(p.percentil_posto_proximo(DADOS, 30), 20)
        self.assertEqual(p.percentil_posto_proximo(DADOS, 40), 20)
        self.assertEqual(p.percentil_posto_proximo(DADOS, 50), 35)
        self.assertEqual(p.percentil_posto_proximo(DADOS, 100), 50)
        self.assertEqual(p.percentil_posto_proximo(DADOS, 0), 15)

    def test_varios(self):
        r = p.percentis(DADOS, [25, 75])
        self.assertAlmostEqual(r[25], 20)
        self.assertAlmostEqual(r[75], 40)

    def test_posto_percentil(self):
        self.assertAlmostEqual(p.posto_percentil(DADOS, 35), 50.0)
        self.assertAlmostEqual(p.posto_percentil(DADOS, 100), 100.0)
        self.assertAlmostEqual(p.posto_percentil(DADOS, 0), 0.0)
        self.assertAlmostEqual(p.posto_percentil([1, 2, 2, 3], 2), 50.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            p.percentil([], 50)
        with self.assertRaises(ValueError):
            p.percentil(DADOS, 101)
        with self.assertRaises(ValueError):
            p.percentil_posto_proximo(DADOS, -1)


if __name__ == "__main__":
    unittest.main()
