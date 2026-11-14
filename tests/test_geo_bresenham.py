import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_bresenham import celulas_visiveis, linha, tem_linha_de_visao


class TestBresenham(unittest.TestCase):
    def test_ponto(self):
        self.assertEqual(linha((2, 3), (2, 3)), [(2, 3)])

    def test_horizontal_vertical_diagonal(self):
        self.assertEqual(linha((0, 0), (0, 3)), [(0, 0), (0, 1), (0, 2), (0, 3)])
        self.assertEqual(linha((3, 1), (0, 1)), [(3, 1), (2, 1), (1, 1), (0, 1)])
        self.assertEqual(linha((0, 0), (2, 2)), [(0, 0), (1, 1), (2, 2)])

    def test_inclinada_conhecida(self):
        self.assertEqual(linha((0, 0), (2, 5)), [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5)])

    def test_simetria_de_extremos_e_tamanho(self):
        for a, b in [((0, 0), (7, 3)), ((5, 5), (1, 9)), ((9, 2), (0, 0))]:
            l = linha(a, b)
            self.assertEqual(l[0], a)
            self.assertEqual(l[-1], b)
            self.assertEqual(len(l), max(abs(a[0] - b[0]), abs(a[1] - b[1])) + 1)
            # passos de no máximo 1 célula em cada eixo
            for (r1, c1), (r2, c2) in zip(l, l[1:]):
                self.assertLessEqual(max(abs(r1 - r2), abs(c1 - c2)), 1)

    GRADE = [
        "......",
        "..#...",
        "......",
        "....#.",
        "......",
    ]

    def test_visao_livre_e_bloqueada(self):
        self.assertTrue(tem_linha_de_visao(self.GRADE, (0, 0), (0, 5)))
        self.assertFalse(tem_linha_de_visao(self.GRADE, (1, 0), (1, 5)))
        self.assertFalse(tem_linha_de_visao(self.GRADE, (3, 0), (3, 5)))

    def test_extremidade_parede_nao_bloqueia(self):
        self.assertTrue(tem_linha_de_visao(self.GRADE, (1, 0), (1, 2)))
        self.assertTrue(tem_linha_de_visao(self.GRADE, (1, 2), (1, 2)))

    def test_adjacentes_sempre_se_veem(self):
        self.assertTrue(tem_linha_de_visao(self.GRADE, (0, 1), (1, 2)))

    def test_fora_da_grade(self):
        with self.assertRaises(IndexError):
            tem_linha_de_visao(self.GRADE, (0, 0), (9, 9))
        with self.assertRaises(IndexError):
            tem_linha_de_visao(self.GRADE, (-1, 0), (1, 1))

    def test_celulas_visiveis(self):
        v = celulas_visiveis(self.GRADE, (1, 0), 3)
        self.assertIn((1, 0), v)
        self.assertIn((1, 2), v)  # a própria parede é visível
        self.assertNotIn((1, 3), v)  # atrás da parede
        self.assertIn((0, 3), v)
        self.assertNotIn((1, 4), v)  # fora do alcance


if __name__ == "__main__":
    unittest.main()
