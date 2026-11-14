import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_desenho import desenhar_circulo, desenhar_linha, nova_imagem, pontos_circulo, pontos_linha


class TestImgDesenho(unittest.TestCase):
    def test_linha_horizontal_e_vertical(self):
        self.assertEqual(pontos_linha(1, 2, 4, 2), [(1, 2), (2, 2), (3, 2), (4, 2)])
        self.assertEqual(pontos_linha(3, 0, 3, 2), [(3, 0), (3, 1), (3, 2)])

    def test_linha_diagonal(self):
        self.assertEqual(pontos_linha(0, 0, 3, 3), [(0, 0), (1, 1), (2, 2), (3, 3)])
        self.assertEqual(pontos_linha(0, 3, 3, 0), [(0, 3), (1, 2), (2, 1), (3, 0)])

    def test_linha_suave(self):
        self.assertEqual(pontos_linha(0, 0, 5, 2),
                         [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)])

    def test_linha_ingreme(self):
        self.assertEqual(pontos_linha(0, 0, 2, 5),
                         [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5)])

    def test_linha_invertida_tem_mesmo_conjunto(self):
        direta = pontos_linha(0, 0, 5, 2)
        inversa = pontos_linha(5, 2, 0, 0)
        self.assertEqual(inversa[0], (5, 2))
        self.assertEqual(sorted(direta), sorted(inversa))

    def test_ponto_unico(self):
        self.assertEqual(pontos_linha(2, 2, 2, 2), [(2, 2)])

    def test_desenhar_linha_na_matriz(self):
        img = desenhar_linha(nova_imagem(4, 3), 0, 0, 3, 2, 1)
        # y = 2x/3: (0,0) (1,1) (2,1) (3,2)
        self.assertEqual(img, [[1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]])

    def test_linha_cortada_nas_bordas(self):
        img = desenhar_linha(nova_imagem(3, 1), -2, 0, 5, 0, 9)
        self.assertEqual(img, [[9, 9, 9]])

    def test_circulo_raio_2(self):
        pts = pontos_circulo(0, 0, 2)
        esperado = {(2, 0), (-2, 0), (0, 2), (0, -2), (2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (-1, 2), (1, -2), (-1, -2)}
        self.assertEqual(pts, esperado)

    def test_circulo_na_matriz(self):
        img = desenhar_circulo(nova_imagem(7, 7), 3, 3, 2, 1)
        self.assertEqual(img, [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ])

    def test_circulo_raio_zero_e_negativo(self):
        self.assertEqual(pontos_circulo(4, 5, 0), {(4, 5)})
        with self.assertRaises(ValueError):
            pontos_circulo(0, 0, -1)

    def test_nova_imagem_invalida(self):
        with self.assertRaises(ValueError):
            nova_imagem(0, 3)


if __name__ == "__main__":
    unittest.main()
