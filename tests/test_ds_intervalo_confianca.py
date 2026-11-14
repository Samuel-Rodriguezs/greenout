import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_intervalo_confianca import ic_media_t, ic_media_z, ic_proporcao_wald, ic_proporcao_wilson

DADOS = [1, 2, 3, 4, 5]  # média 3, s = sqrt(2.5), erro padrão = sqrt(0.5)


class TestIntervaloConfianca(unittest.TestCase):
    def test_media_z(self):
        lo, hi = ic_media_z(DADOS)
        h = 1.959964 * 0.5 ** 0.5
        self.assertAlmostEqual(lo, 3 - h, places=4)
        self.assertAlmostEqual(hi, 3 + h, places=4)

    def test_media_t_mais_larga(self):
        lo, hi = ic_media_t(DADOS)
        h = 2.776445 * 0.5 ** 0.5
        self.assertAlmostEqual(lo, 3 - h, places=3)
        self.assertAlmostEqual(hi, 3 + h, places=3)
        zlo, zhi = ic_media_z(DADOS)
        self.assertGreater(hi - lo, zhi - zlo)

    def test_confianca_maior_intervalo_maior(self):
        a = ic_media_z(DADOS, 0.90)
        b = ic_media_z(DADOS, 0.99)
        self.assertGreater(b[1] - b[0], a[1] - a[0])

    def test_wald(self):
        # p = 0.5, n = 100: h = 1.959964 * 0.05
        lo, hi = ic_proporcao_wald(50, 100)
        self.assertAlmostEqual(lo, 0.5 - 1.959964 * 0.05, places=4)
        self.assertAlmostEqual(hi, 0.5 + 1.959964 * 0.05, places=4)
        self.assertEqual(ic_proporcao_wald(0, 10), (0.0, 0.0))

    def test_wilson(self):
        lo, hi = ic_proporcao_wilson(8, 10)
        self.assertAlmostEqual(lo, 0.4902, delta=0.001)
        self.assertAlmostEqual(hi, 0.9433, delta=0.001)
        lo0, hi0 = ic_proporcao_wilson(0, 10)
        self.assertAlmostEqual(lo0, 0.0, places=10)
        self.assertGreater(hi0, 0.2)

    def test_erros(self):
        with self.assertRaises(ValueError):
            ic_media_z([1])
        with self.assertRaises(ValueError):
            ic_media_t(DADOS, 1.0)
        with self.assertRaises(ValueError):
            ic_proporcao_wilson(11, 10)


if __name__ == "__main__":
    unittest.main()
