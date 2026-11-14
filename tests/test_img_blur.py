import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_blur import blur_caixa, blur_gaussiano, kernel_gaussiano


class TestImgBlur(unittest.TestCase):
    def test_caixa_espalha_ponto(self):
        img = [[0, 0, 0], [0, 9, 0], [0, 0, 0]]
        self.assertEqual(blur_caixa(img, 1, "zero"), [[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    def test_caixa_media_central(self):
        img = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.assertEqual(blur_caixa(img)[1][1], 5)
        # canto com replicação: soma 21 / 9 = 2.33 -> 2
        self.assertEqual(blur_caixa(img)[0][0], 2)

    def test_caixa_imagem_constante(self):
        img = [[40] * 4 for _ in range(4)]
        self.assertEqual(blur_caixa(img, 2), img)

    def test_kernel_gaussiano(self):
        k = kernel_gaussiano(1, 1.0)
        self.assertAlmostEqual(sum(sum(l) for l in k), 1.0)
        self.assertAlmostEqual(k[1][1], 0.2042, places=3)
        self.assertAlmostEqual(k[0][1], 0.1238, places=3)
        self.assertAlmostEqual(k[0][0], 0.0751, places=3)
        self.assertEqual(k[0][1], k[1][0])

    def test_gaussiano_preserva_constante(self):
        img = [[77] * 5 for _ in range(5)]
        self.assertEqual(blur_gaussiano(img, 2, 1.5), img)

    def test_gaussiano_ponto(self):
        img = [[0, 0, 0], [0, 255, 0], [0, 0, 0]]
        out = blur_gaussiano(img, 1, 1.0, "zero")
        self.assertEqual(out[1][1], 52)  # 255 * 0.2042
        self.assertEqual(out[0][1], 32)  # 255 * 0.1238
        self.assertEqual(out[0][0], 19)  # 255 * 0.0751

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            blur_caixa([[1]], 0)
        with self.assertRaises(ValueError):
            kernel_gaussiano(1, 0)


if __name__ == "__main__":
    unittest.main()
