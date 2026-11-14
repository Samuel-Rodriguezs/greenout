import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_laplaciano import bordas_laplaciano, cruzamentos_zero, laplaciano

PONTO = [[0, 0, 0], [0, 10, 0], [0, 0, 0]]


class TestImgLaplaciano(unittest.TestCase):
    def test_conectividade_4(self):
        self.assertEqual(laplaciano(PONTO, 4), [[0, 10, 0], [10, -40, 10], [0, 10, 0]])

    def test_conectividade_8(self):
        self.assertEqual(laplaciano(PONTO, 8), [[10, 10, 10], [10, -80, 10], [10, 10, 10]])

    def test_regiao_plana(self):
        self.assertEqual(laplaciano([[5] * 3] * 3), [[0.0] * 3] * 3)

    def test_rampa_linear_tem_resposta_zero_no_interior(self):
        img = [[0, 10, 20, 30]] * 3
        self.assertEqual(laplaciano(img)[1][1:3], [0, 0])

    def test_bordas_absoluto_e_saturado(self):
        self.assertEqual(bordas_laplaciano(PONTO), [[0, 10, 0], [10, 40, 10], [0, 10, 0]])
        grande = [[0, 0, 0], [0, 200, 0], [0, 0, 0]]
        self.assertEqual(bordas_laplaciano(grande)[1][1], 255)

    def test_cruzamentos_zero(self):
        # degrau 0|100: resposta é +100 de um lado e -100 do outro da transição
        img = [[0, 0, 100, 100]] * 3
        r = laplaciano(img)
        self.assertEqual(r[1], [0, 100, -100, 0])
        self.assertEqual(cruzamentos_zero(img)[1], [0, 255, 0, 0])
        self.assertEqual(cruzamentos_zero(img, limiar=300)[1], [0, 0, 0, 0])

    def test_conectividade_invalida(self):
        with self.assertRaises(ValueError):
            laplaciano(PONTO, 6)


if __name__ == "__main__":
    unittest.main()
