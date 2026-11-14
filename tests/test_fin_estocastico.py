import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_estocastico import estocastico


class TestEstocastico(unittest.TestCase):
    def test_k_a_mao(self):
        k, d = estocastico([10, 12, 14], [8, 9, 10], [9, 11, 13], n=3, suavizacao=1)
        self.assertEqual(k[:2], [None, None])
        self.assertAlmostEqual(k[2], 500 / 6)
        self.assertAlmostEqual(d[2], 500 / 6)

    def test_d_media_de_k(self):
        h = [10, 11, 12, 13]
        low = [8, 9, 10, 11]
        c = [9, 10, 12, 11]
        k, d = estocastico(h, low, c, n=2, suavizacao=2)
        # k1=(10-8)/(11-8)=2/3 ; k2=(12-9)/(12-9)=1 ; k3=(11-10)/(13-10)=1/3
        self.assertAlmostEqual(k[1], 200 / 3)
        self.assertAlmostEqual(k[2], 100.0)
        self.assertAlmostEqual(k[3], 100 / 3)
        self.assertAlmostEqual(d[2], (200 / 3 + 100) / 2)
        self.assertAlmostEqual(d[3], (100 + 100 / 3) / 2)
        self.assertIsNone(d[1])

    def test_faixa_nula(self):
        k, _ = estocastico([5, 5], [5, 5], [5, 5], n=2, suavizacao=1)
        self.assertEqual(k[1], 50.0)

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            estocastico([1], [1, 2], [1])
        with self.assertRaises(ValueError):
            estocastico([1], [1], [1], n=0)


if __name__ == "__main__":
    unittest.main()
