import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_rotacao import (espelhar_horizontal, espelhar_vertical, rotacionar_90, rotacionar_180,
                         transpor)

IMG = [[1, 2, 3], [4, 5, 6]]


class TestImgRotacao(unittest.TestCase):
    def test_transpor(self):
        self.assertEqual(transpor(IMG), [[1, 4], [2, 5], [3, 6]])

    def test_espelhos(self):
        self.assertEqual(espelhar_horizontal(IMG), [[3, 2, 1], [6, 5, 4]])
        self.assertEqual(espelhar_vertical(IMG), [[4, 5, 6], [1, 2, 3]])

    def test_rotacao_horaria(self):
        self.assertEqual(rotacionar_90(IMG), [[4, 1], [5, 2], [6, 3]])

    def test_rotacao_anti_horaria(self):
        self.assertEqual(rotacionar_90(IMG, -1), [[3, 6], [2, 5], [1, 4]])
        self.assertEqual(rotacionar_90(IMG, 3), [[3, 6], [2, 5], [1, 4]])

    def test_rotacao_180(self):
        self.assertEqual(rotacionar_180(IMG), [[6, 5, 4], [3, 2, 1]])
        self.assertEqual(rotacionar_90(IMG, 2), rotacionar_180(IMG))

    def test_quatro_giros_voltam(self):
        self.assertEqual(rotacionar_90(IMG, 4), IMG)
        r = IMG
        for _ in range(4):
            r = rotacionar_90(r)
        self.assertEqual(r, IMG)

    def test_nao_altera_original_e_aceita_rgb(self):
        rgb = [[(1, 0, 0), (0, 1, 0)]]
        self.assertEqual(rotacionar_90(rgb), [[(1, 0, 0)], [(0, 1, 0)]])
        self.assertEqual(rotacionar_90(IMG, 0), IMG)
        self.assertIsNot(rotacionar_90(IMG, 0)[0], IMG[0])
        self.assertEqual(IMG, [[1, 2, 3], [4, 5, 6]])


if __name__ == "__main__":
    unittest.main()
