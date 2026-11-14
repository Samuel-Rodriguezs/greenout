import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_quantiza import aplicar_paleta, cor_mais_proxima, paleta_corte_mediano, quantizar_uniforme

PRETO, BRANCO = (0, 0, 0), (255, 255, 255)


class TestImgQuantiza(unittest.TestCase):
    def test_uniforme_1_bit(self):
        img = [[(0, 127, 128), (255, 100, 200)]]
        self.assertEqual(quantizar_uniforme(img, 1), [[(0, 0, 255), (255, 0, 255)]])

    def test_uniforme_2_bits(self):
        # níveis 0, 85, 170, 255
        img = [[(0, 63, 64), (127, 128, 255), (191, 192, 100)]]
        self.assertEqual(quantizar_uniforme(img, 2),
                         [[(0, 0, 85), (85, 170, 255), (170, 255, 85)]])

    def test_uniforme_8_bits_identidade(self):
        img = [[(1, 2, 3), (250, 251, 252)]]
        self.assertEqual(quantizar_uniforme(img, 8), img)

    def test_bits_invalidos(self):
        with self.assertRaises(ValueError):
            quantizar_uniforme([[PRETO]], 0)

    def test_paleta_duas_cores(self):
        img = [[(10, 10, 10), (10, 10, 10)], [(250, 250, 250), (250, 250, 250)]]
        self.assertEqual(paleta_corte_mediano(img, 2), [(10, 10, 10), (250, 250, 250)])

    def test_paleta_media_das_caixas(self):
        img = [[(0, 0, 0), (20, 0, 0), (200, 0, 0), (240, 0, 0)]]
        self.assertEqual(paleta_corte_mediano(img, 2), [(10, 0, 0), (220, 0, 0)])

    def test_paleta_k_maior_que_cores(self):
        img = [[PRETO, BRANCO]]
        self.assertEqual(paleta_corte_mediano(img, 8), [PRETO, BRANCO])

    def test_paleta_k_1_e_media_geral(self):
        img = [[(0, 0, 0), (100, 50, 200)]]
        self.assertEqual(paleta_corte_mediano(img, 1), [(50, 25, 100)])

    def test_cor_mais_proxima_e_aplicar(self):
        paleta = [PRETO, (255, 0, 0), BRANCO]
        self.assertEqual(cor_mais_proxima((200, 30, 20), paleta), (255, 0, 0))
        self.assertEqual(cor_mais_proxima((127, 127, 127), [PRETO, BRANCO]), PRETO)
        img = [[(10, 10, 10), (240, 240, 250)]]
        self.assertEqual(aplicar_paleta(img, paleta), [[PRETO, BRANCO]])
        with self.assertRaises(ValueError):
            aplicar_paleta(img, [])


if __name__ == "__main__":
    unittest.main()
