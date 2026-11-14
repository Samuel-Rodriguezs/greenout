import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_histograma import equalizar, histograma, histograma_acumulado


class TestImgHistograma(unittest.TestCase):
    def test_histograma(self):
        img = [[0, 0, 1], [1, 2, 2], [3, 3, 3]]
        self.assertEqual(histograma(img, 4), [2, 2, 2, 3])

    def test_histograma_256(self):
        h = histograma([[0, 255], [255, 7]])
        self.assertEqual(len(h), 256)
        self.assertEqual((h[0], h[7], h[255]), (1, 1, 2))

    def test_valor_fora_da_faixa(self):
        with self.assertRaises(ValueError):
            histograma([[4]], 4)

    def test_acumulado(self):
        self.assertEqual(histograma_acumulado([5, 2, 1, 0]), [5, 7, 8, 8])

    def test_equalizar_mapeamento_manual(self):
        # hist [5,2,1,0] -> cdf [5,7,8,8]; (cdf-5)/3*3 => 0->0, 1->2, 2->3
        img = [[0, 0, 0, 0], [0, 1, 1, 2]]
        self.assertEqual(equalizar(img, 4), [[0, 0, 0, 0], [0, 2, 2, 3]])

    def test_equalizar_uniforme_nao_muda(self):
        img = [[0, 0, 1, 1], [2, 2, 3, 3]]
        self.assertEqual(equalizar(img, 4), [[0, 0, 1, 1], [2, 2, 3, 3]])

    def test_equalizar_expande_contraste(self):
        img = [[100, 101], [102, 103]]
        self.assertEqual(equalizar(img), [[0, 85], [170, 255]])

    def test_equalizar_constante(self):
        self.assertEqual(equalizar([[9, 9], [9, 9]]), [[9, 9], [9, 9]])


if __name__ == "__main__":
    unittest.main()
