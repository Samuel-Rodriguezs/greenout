import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_binning as b


class TestBinning(unittest.TestCase):
    def test_rotulos(self):
        self.assertEqual(b.rotulos_faixas([0, 10, 20]), ["(0, 10]", "(10, 20]"])
        self.assertEqual(b.rotulos_faixas([0, 2.5, 5], direita=False), ["[0, 2.5)", "[2.5, 5)"])

    def test_cortar_direita(self):
        r = b.cortar([0, 5, 10, 15, 20, 25], [0, 10, 20])
        self.assertEqual(r, [None, "(0, 10]", "(0, 10]", "(10, 20]", "(10, 20]", None])

    def test_cortar_esquerda(self):
        r = b.cortar([0, 5, 10, 15, 20], [0, 10, 20], direita=False)
        self.assertEqual(r, ["[0, 10)", "[0, 10)", "[10, 20)", "[10, 20)", None])

    def test_incluir_extremo(self):
        self.assertEqual(b.cortar([0], [0, 10], incluir_extremo=True), ["(0, 10]"])
        self.assertEqual(b.cortar([10], [0, 10], direita=False, incluir_extremo=True), ["[0, 10)"])

    def test_rotulos_personalizados(self):
        r = b.cortar([5, 15, 70], [0, 18, 65, 120], rotulos=["jovem", "adulto", "idoso"])
        self.assertEqual(r, ["jovem", "jovem", "idoso"])
        with self.assertRaises(ValueError):
            b.cortar([1], [0, 5, 10], rotulos=["a"])

    def test_largura_igual(self):
        self.assertEqual(b.limites_largura_igual([0, 10, 4], 2), [0, 5, 10])

    def test_quantis(self):
        lim = b.limites_quantis([1, 2, 3, 4, 5, 6, 7, 8], 4)
        for a, e in zip(lim, [1, 2.75, 4.5, 6.25, 8]):
            self.assertAlmostEqual(a, e)

    def test_contagem(self):
        c = b.contar_por_faixa([0, 1, 5, 10, 11, 20, 99], [0, 10, 20])
        self.assertEqual(c, {"(0, 10]": 4, "(10, 20]": 2})

    def test_erros(self):
        with self.assertRaises(ValueError):
            b.cortar([1], [5, 5, 6])
        with self.assertRaises(ValueError):
            b.cortar([1], [5])
        with self.assertRaises(ValueError):
            b.limites_largura_igual([3, 3], 2)


if __name__ == "__main__":
    unittest.main()
