import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_sobel import bordas, direcao, gradientes, magnitude

VERTICAL = [[0, 0, 255, 255]] * 4


class TestImgSobel(unittest.TestCase):
    def test_gradiente_borda_vertical_sobel(self):
        gx, gy = gradientes(VERTICAL, "sobel")
        for y in range(4):
            self.assertEqual(gx[y], [0, 1020, 1020, 0])
            self.assertEqual(gy[y], [0, 0, 0, 0])

    def test_gradiente_prewitt(self):
        gx, _ = gradientes(VERTICAL, "prewitt")
        self.assertEqual(gx[1], [0, 765, 765, 0])

    def test_borda_horizontal_gy(self):
        img = [[0] * 3, [0] * 3, [90] * 3]
        gx, gy = gradientes(img, "sobel")
        # linha 1: (90 * (1+2+1)) = 360 ; linha 2 tem vizinhos 0 acima e replicação abaixo
        self.assertEqual(gy[1], [360, 360, 360])
        self.assertEqual(gy[2], [360, 360, 360])
        self.assertEqual(gy[0], [0, 0, 0])
        self.assertEqual(gx[1], [0, 0, 0])

    def test_magnitude_diagonal(self):
        img = [[0, 0, 0], [0, 0, 10], [0, 10, 10]]
        mag = magnitude(img, "prewitt")
        # centro: gx = (0+0+0) -> direita 0+10+10 = 20 ; gy = 0+10+10 = 20
        self.assertAlmostEqual(mag[1][1], math.hypot(20, 20))

    def test_direcao(self):
        d = direcao(VERTICAL)
        self.assertEqual(d[1][1], 0.0)
        d2 = direcao([[0, 0, 0], [0, 0, 0], [9, 9, 9]])
        self.assertAlmostEqual(d2[1][1], math.pi / 2)

    def test_bordas_saturadas_e_limiar(self):
        self.assertEqual(bordas(VERTICAL)[0], [0, 255, 255, 0])
        self.assertEqual(bordas(VERTICAL, limiar=500)[2], [0, 255, 255, 0])
        self.assertEqual(bordas(VERTICAL, limiar=2000)[2], [0, 0, 0, 0])

    def test_imagem_plana_sem_bordas(self):
        self.assertEqual(bordas([[7] * 3] * 3), [[0] * 3] * 3)

    def test_operador_invalido(self):
        with self.assertRaises(ValueError):
            gradientes(VERTICAL, "roberts")


if __name__ == "__main__":
    unittest.main()
