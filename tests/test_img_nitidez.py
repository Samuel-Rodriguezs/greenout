import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_nitidez import afiar, mascara_nitidez


class TestImgNitidez(unittest.TestCase):
    def test_regiao_plana_inalterada(self):
        img = [[90] * 4 for _ in range(4)]
        self.assertEqual(afiar(img), img)
        self.assertEqual(mascara_nitidez(img, 2.0), img)

    def test_ponto_isolado(self):
        img = [[0, 0, 0], [0, 10, 0], [0, 0, 0]]
        # centro: 5*10 = 50; vizinhos diretos: -10 -> 0 (saturado); cantos: 0
        self.assertEqual(afiar(img), [[0, 0, 0], [0, 50, 0], [0, 0, 0]])

    def test_borda_vertical_ganha_contraste(self):
        img = [[100, 100, 150, 150]] * 3
        out = afiar(img)
        # em x=1: 5*100 - 100 - 150 - 100 - 100 = 50 ; em x=2: 5*150 - 100 - 150 - 150 - 150 = 200
        self.assertEqual(out[1], [100, 50, 200, 150])

    def test_quantidade_zero_e_identidade(self):
        img = [[10, 200, 30], [40, 50, 60], [70, 80, 250]]
        self.assertEqual(mascara_nitidez(img, 0.0), img)

    def test_mascara_aumenta_contraste_local(self):
        img = [[0, 0, 0], [0, 100, 0], [0, 0, 0]]
        out = mascara_nitidez(img, 1.0, 1, 1.0)
        # desfocado no centro = 100*0.2042 = 20 (arredondado) -> 100 + 80 = 180
        self.assertEqual(out[1][1], 180)
        self.assertEqual(out[0][0], 0)


if __name__ == "__main__":
    unittest.main()
