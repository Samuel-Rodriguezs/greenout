import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_sudoku import sudoku_valido

RESOLVIDO = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def copia(t):
    return [linha[:] for linha in t]


class TesteSudoku(unittest.TestCase):
    def test_resolvido(self):
        self.assertTrue(sudoku_valido(RESOLVIDO))

    def test_vazio(self):
        self.assertTrue(sudoku_valido([[0] * 9 for _ in range(9)]))

    def test_parcial_valido(self):
        t = copia(RESOLVIDO)
        for r in range(9):
            for c in range(0, 9, 2):
                t[r][c] = 0
        self.assertTrue(sudoku_valido(t))

    def test_repeticao_na_linha(self):
        t = [[0] * 9 for _ in range(9)]
        t[0][0] = t[0][8] = 5
        self.assertFalse(sudoku_valido(t))

    def test_repeticao_na_coluna(self):
        t = [[0] * 9 for _ in range(9)]
        t[0][4] = t[8][4] = 7
        self.assertFalse(sudoku_valido(t))

    def test_repeticao_no_bloco(self):
        t = [[0] * 9 for _ in range(9)]
        t[0][0] = t[2][2] = 3
        self.assertFalse(sudoku_valido(t))

    def test_mesmo_valor_em_blocos_diferentes(self):
        t = [[0] * 9 for _ in range(9)]
        t[0][0] = 3
        t[3][3] = 3
        self.assertTrue(sudoku_valido(t))

    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            sudoku_valido([[0] * 9 for _ in range(8)])
        with self.assertRaises(ValueError):
            sudoku_valido([[0] * 8 for _ in range(9)])

    def test_valor_fora_do_intervalo(self):
        t = [[0] * 9 for _ in range(9)]
        t[4][4] = 10
        with self.assertRaises(ValueError):
            sudoku_valido(t)


if __name__ == "__main__":
    unittest.main()
