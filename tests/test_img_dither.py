import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_dither import floyd_steinberg


class TestImgDither(unittest.TestCase):
    def test_extremos_nao_mudam(self):
        self.assertEqual(floyd_steinberg([[0] * 4] * 4), [[0] * 4] * 4)
        self.assertEqual(floyd_steinberg([[255] * 4] * 4), [[255] * 4] * 4)

    def test_calculo_manual_2x2(self):
        # (0,0): 100 -> 0, erro 100 => (0,1)=143.75, (1,0)=131.25, (1,1)=106.25
        # (0,1): 143.75 -> 255, erro -111.25 => (1,0)=110.39, (1,1)=71.48
        # (1,0): 110.39 -> 0, erro 110.39 => (1,1)=119.77 -> 0
        self.assertEqual(floyd_steinberg([[100, 100], [100, 100]]), [[0, 255], [0, 0]])

    def test_saida_so_tem_niveis_validos(self):
        img = [[(x * 37 + y * 11) % 256 for x in range(8)] for y in range(8)]
        self.assertTrue(all(v in (0, 255) for l in floyd_steinberg(img) for v in l))
        quatro = floyd_steinberg(img, 4)
        self.assertTrue(all(v in (0, 85, 170, 255) for l in quatro for v in l))

    def test_preserva_brilho_medio(self):
        img = [[128] * 8 for _ in range(8)]
        out = floyd_steinberg(img)
        media = sum(sum(l) for l in out) / 64
        self.assertAlmostEqual(media, 128, delta=8)

    def test_niveis_exatos_sao_preservados(self):
        img = [[0, 85], [170, 255]]
        self.assertEqual(floyd_steinberg(img, 4), img)

    def test_nao_altera_entrada(self):
        img = [[100, 100], [100, 100]]
        floyd_steinberg(img)
        self.assertEqual(img, [[100, 100], [100, 100]])

    def test_niveis_invalidos(self):
        with self.assertRaises(ValueError):
            floyd_steinberg([[1]], 1)


if __name__ == "__main__":
    unittest.main()
