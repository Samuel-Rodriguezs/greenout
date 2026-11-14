import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_rotulos import areas, caixas_delimitadoras, rotular

IMG = [
    [1, 1, 0, 0, 1],
    [1, 0, 0, 1, 1],
    [0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 1, 0, 1],
]


class TestImgRotulos(unittest.TestCase):
    def test_conectividade_4(self):
        rot, n = rotular(IMG)
        self.assertEqual(n, 4)
        self.assertEqual(rot, [
            [1, 1, 0, 0, 2],
            [1, 0, 0, 2, 2],
            [0, 0, 0, 0, 0],
            [3, 0, 3, 0, 0],
            [3, 3, 3, 0, 4],
        ])

    def test_diagonal_une_com_conectividade_8(self):
        img = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.assertEqual(rotular(img, 4)[1], 3)
        rot, n = rotular(img, 8)
        self.assertEqual(n, 1)
        self.assertEqual(rot, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def test_sem_objetos(self):
        self.assertEqual(rotular([[0, 0], [0, 0]]), ([[0, 0], [0, 0]], 0))

    def test_fundo_personalizado(self):
        rot, n = rotular([[255, 7], [255, 7]], fundo=255)
        self.assertEqual((rot, n), ([[0, 1], [0, 1]], 1))

    def test_areas_e_caixas(self):
        rot, _ = rotular(IMG)
        self.assertEqual(areas(rot), {1: 3, 2: 3, 3: 5, 4: 1})
        caixas = caixas_delimitadoras(rot)
        self.assertEqual(caixas[1], (0, 0, 1, 1))
        self.assertEqual(caixas[2], (3, 0, 4, 1))
        self.assertEqual(caixas[3], (0, 3, 2, 4))
        self.assertEqual(caixas[4], (4, 4, 4, 4))

    def test_conectividade_invalida(self):
        with self.assertRaises(ValueError):
            rotular(IMG, 6)


if __name__ == "__main__":
    unittest.main()
