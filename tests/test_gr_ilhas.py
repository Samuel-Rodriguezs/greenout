import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_ilhas import contar_ilhas, flood_fill, maior_ilha

G = [
    [1, 1, 0, 0, 0],
    [1, 0, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1],
]


class TestIlhas(unittest.TestCase):
    def test_contagem(self):
        self.assertEqual(contar_ilhas(G), 4)

    def test_diagonal_une(self):
        self.assertEqual(contar_ilhas(G, diagonal=True), 3)

    def test_maior(self):
        self.assertEqual(maior_ilha(G), 3)
        self.assertEqual(maior_ilha(G, diagonal=True), 3)

    def test_vazias(self):
        self.assertEqual(contar_ilhas([]), 0)
        self.assertEqual(maior_ilha([[0, 0]]), 0)
        self.assertEqual(contar_ilhas([[]]), 0)

    def test_tudo_terra(self):
        self.assertEqual(contar_ilhas([[1] * 3] * 3), 1)
        self.assertEqual(maior_ilha([[1] * 3] * 3), 9)

    def test_flood_fill(self):
        img = [[1, 1, 0], [1, 0, 0], [1, 0, 1]]
        self.assertEqual(flood_fill(img, 0, 0, 2), [[2, 2, 0], [2, 0, 0], [2, 0, 1]])
        self.assertEqual(img[0][0], 1)

    def test_flood_fill_mesma_cor_e_fora(self):
        img = [[1, 1], [1, 1]]
        self.assertEqual(flood_fill(img, 0, 0, 1), img)
        with self.assertRaises(IndexError):
            flood_fill(img, 2, 0, 5)

    def test_grade_grande_sem_recursao(self):
        grande = [[1] * 300 for _ in range(300)]
        self.assertEqual(contar_ilhas(grande), 1)


if __name__ == "__main__":
    unittest.main()
