import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_histograma import histograma, histograma_ascii

DADOS = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]


class TestHistograma(unittest.TestCase):
    def test_contagens(self):
        lim, cont = histograma(DADOS, 4)
        self.assertEqual(cont, [1, 2, 3, 4])
        for a, b in zip(lim, [1, 1.75, 2.5, 3.25, 4]):
            self.assertAlmostEqual(a, b)

    def test_soma_igual_n(self):
        _, cont = histograma([0.1, 5.5, 9.9, 3.3, 7.7], 3)
        self.assertEqual(sum(cont), 5)

    def test_constante(self):
        _, cont = histograma([7, 7, 7], 3)
        self.assertEqual(cont, [3, 0, 0])

    def test_ascii(self):
        txt = histograma_ascii(DADOS, 4, largura=8)
        linhas = txt.splitlines()
        self.assertEqual(len(linhas), 4)
        self.assertTrue(linhas[3].endswith("######## 4"))
        self.assertTrue(linhas[0].endswith("## 1"))
        self.assertIn("[3.25, 4.00]", linhas[3])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            histograma([], 3)
        with self.assertRaises(ValueError):
            histograma([1], 0)


if __name__ == "__main__":
    unittest.main()
