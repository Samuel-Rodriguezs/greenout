import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_matriz_rotacao import espiral, rotacionar_90, rotacionar_antihorario, rotacionar_in_place


class TestMatriz(unittest.TestCase):
    def test_rotacao_quadrada(self):
        self.assertEqual(rotacionar_90([[1, 2], [3, 4]]), [[3, 1], [4, 2]])

    def test_rotacao_retangular(self):
        self.assertEqual(rotacionar_90([[1, 2, 3], [4, 5, 6]]), [[4, 1], [5, 2], [6, 3]])

    def test_antihorario_inverte_horario(self):
        m = [[1, 2, 3], [4, 5, 6]]
        self.assertEqual(rotacionar_antihorario(rotacionar_90(m)), m)

    def test_quatro_giros_identidade(self):
        m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        r = m
        for _ in range(4):
            r = rotacionar_90(r)
        self.assertEqual(r, m)

    def test_in_place(self):
        for n in (0, 1, 2, 3, 4, 5):
            m = [[i * n + j for j in range(n)] for i in range(n)]
            esperado = rotacionar_90(m)
            rotacionar_in_place(m)
            self.assertEqual(m, esperado)

    def test_in_place_nao_quadrada(self):
        with self.assertRaises(ValueError):
            rotacionar_in_place([[1, 2, 3], [4, 5, 6]])

    def test_irregular(self):
        with self.assertRaises(ValueError):
            rotacionar_90([[1, 2], [3]])
        with self.assertRaises(ValueError):
            espiral([[1], [2, 3]])

    def test_espiral(self):
        self.assertEqual(espiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), [1, 2, 3, 6, 9, 8, 7, 4, 5])
        self.assertEqual(espiral([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]), [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7])

    def test_espiral_bordas(self):
        self.assertEqual(espiral([]), [])
        self.assertEqual(espiral([[]]), [])
        self.assertEqual(espiral([[1, 2, 3]]), [1, 2, 3])
        self.assertEqual(espiral([[1], [2], [3]]), [1, 2, 3])
        self.assertEqual(espiral([[7]]), [7])


if __name__ == "__main__":
    unittest.main()
