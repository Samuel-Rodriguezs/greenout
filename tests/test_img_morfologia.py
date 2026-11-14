import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_morfologia import (abrir, dilatar, elemento_cruz, elemento_quadrado, erodir, fechar,
                            gradiente_morfologico)

BLOCO = [
    [0, 0, 0, 0, 0],
    [0, 255, 255, 255, 0],
    [0, 255, 255, 255, 0],
    [0, 255, 255, 255, 0],
    [0, 0, 0, 0, 0],
]


def ponto(y: int, x: int, n: int = 5) -> list[list[int]]:
    img = [[0] * n for _ in range(n)]
    img[y][x] = 255
    return img


class TestImgMorfologia(unittest.TestCase):
    def test_erosao_bloco_vira_ponto(self):
        self.assertEqual(erodir(BLOCO), ponto(2, 2))

    def test_dilatacao_ponto_quadrado(self):
        esperado = [[0] * 5, [0, 255, 255, 255, 0], [0, 255, 255, 255, 0],
                    [0, 255, 255, 255, 0], [0] * 5]
        self.assertEqual(dilatar(ponto(2, 2)), esperado)

    def test_dilatacao_cruz(self):
        esperado = [[0] * 5, [0, 0, 255, 0, 0], [0, 255, 255, 255, 0],
                    [0, 0, 255, 0, 0], [0] * 5]
        self.assertEqual(dilatar(ponto(2, 2), elemento_cruz()), esperado)

    def test_borda_nao_erode_por_fora(self):
        self.assertEqual(erodir([[255] * 3] * 3), [[255] * 3] * 3)

    def test_abertura_remove_ruido_isolado(self):
        img = [row[:] for row in BLOCO]
        img[0][4] = 255
        self.assertEqual(abrir(img), BLOCO)

    def test_fechamento_preenche_buraco(self):
        # margem de 2 pixels: a dilatação não alcança a borda da imagem
        grande = [[0] * 7 for _ in range(7)]
        for y in range(2, 5):
            for x in range(2, 5):
                grande[y][x] = 255
        furado = [row[:] for row in grande]
        furado[3][3] = 0
        self.assertEqual(fechar(furado), grande)

    def test_cinza_minimo_maximo(self):
        img = [[10, 50, 30], [20, 90, 40], [60, 70, 80]]
        self.assertEqual(erodir(img)[1][1], 10)
        self.assertEqual(dilatar(img)[1][1], 90)
        self.assertEqual(erodir(img, elemento_cruz())[1][1], 20)
        self.assertEqual(dilatar(img)[0][0], 90)

    def test_gradiente(self):
        g = gradiente_morfologico(BLOCO)
        self.assertEqual(g[2][2], 0)  # interior
        self.assertEqual(g[1][1], 255)  # borda do objeto
        self.assertEqual(g[0][0], 255)  # fundo adjacente

    def test_elemento_invalido(self):
        with self.assertRaises(ValueError):
            elemento_quadrado(2)
        with self.assertRaises(ValueError):
            erodir(BLOCO, [[1, 1], [1, 1]])


if __name__ == "__main__":
    unittest.main()
