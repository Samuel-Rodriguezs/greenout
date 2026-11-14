import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_otsu import binarizar_otsu, limiar_otsu


class TestImgOtsu(unittest.TestCase):
    def test_bimodal_perfeito(self):
        img = [[10, 10, 200, 200], [10, 10, 200, 200]]
        self.assertEqual(limiar_otsu(img), 10)
        self.assertEqual(binarizar_otsu(img), [[0, 0, 255, 255], [0, 0, 255, 255]])

    def test_ruido_pequeno_nas_classes(self):
        img = [[8, 10, 12, 9], [198, 200, 202, 201], [11, 9, 199, 203]]
        t = limiar_otsu(img)
        self.assertTrue(12 <= t < 198)
        self.assertEqual(
            binarizar_otsu(img),
            [[0, 0, 0, 0], [255, 255, 255, 255], [0, 0, 255, 255]],
        )

    def test_tres_fundo_um_objeto(self):
        img = [[0, 0, 0], [0, 100, 100], [100, 100, 100]]
        self.assertEqual(limiar_otsu(img), 0)

    def test_imagem_uniforme(self):
        self.assertEqual(limiar_otsu([[50, 50], [50, 50]]), 0)
        self.assertEqual(binarizar_otsu([[50, 50], [50, 50]]), [[255, 255], [255, 255]])

    def test_vazia(self):
        with self.assertRaises(ValueError):
            limiar_otsu([])


if __name__ == "__main__":
    unittest.main()
