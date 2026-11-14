import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_killer_sudoku import (eh_solucao, gaiolas_de_solucao, resolver,
                               validar_gaiolas)

SOLUCAO_9 = [
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
SOLUCAO_4 = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]]


def pares_horizontais(n):
    return [[(r, c), (r, c + 1)] for r in range(n) for c in range(0, n - 1, 2)]


def blocos_horizontais_9():
    saida = []
    for r in range(9):
        for c in range(0, 9, 3):
            saida.append([(r, c), (r, c + 1), (r, c + 2)])
    return saida


class TestKillerSudoku(unittest.TestCase):
    def test_4x4(self):
        gaiolas = gaiolas_de_solucao(SOLUCAO_4, pares_horizontais(4))
        sol = resolver(4, gaiolas)
        self.assertIsNotNone(sol)
        self.assertTrue(eh_solucao(4, sol, gaiolas))

    def test_4x4_com_gaiolas_verticais_unica(self):
        particao = [[(r, c), (r + 1, c)] for r in (0, 2) for c in range(4)]
        gaiolas = gaiolas_de_solucao(SOLUCAO_4, particao)
        sol = resolver(4, gaiolas)
        self.assertTrue(eh_solucao(4, sol, gaiolas))

    def test_9x9_com_dados(self):
        gaiolas = gaiolas_de_solucao(SOLUCAO_9, blocos_horizontais_9())
        dados = {(r, c): SOLUCAO_9[r][c] for r in range(9) for c in range(9) if (r + c) % 3 == 0}
        sol = resolver(9, gaiolas, dados)
        self.assertTrue(eh_solucao(9, sol, gaiolas))
        for (r, c), v in dados.items():
            self.assertEqual(sol[r][c], v)

    def test_sem_solucao_soma_impossivel(self):
        gaiolas = gaiolas_de_solucao(SOLUCAO_4, pares_horizontais(4))
        gaiolas[0] = (gaiolas[0][0], 1)  # duas células distintas nunca somam 1
        self.assertIsNone(resolver(4, gaiolas))

    def test_dado_contraditorio(self):
        gaiolas = gaiolas_de_solucao(SOLUCAO_4, pares_horizontais(4))
        self.assertIsNone(resolver(4, gaiolas, {(0, 0): 4}))

    def test_validacao(self):
        gaiolas = gaiolas_de_solucao(SOLUCAO_4, pares_horizontais(4))
        with self.assertRaises(ValueError):
            validar_gaiolas(4, gaiolas[:-1])
        with self.assertRaises(ValueError):
            validar_gaiolas(4, gaiolas + [(((0, 0),), 1)])
        with self.assertRaises(ValueError):
            resolver(5, [])

    def test_eh_solucao_rejeita_repeticao(self):
        ruim = [l[:] for l in SOLUCAO_4]
        ruim[0][0], ruim[0][1] = ruim[0][1], ruim[0][0]
        self.assertFalse(eh_solucao(4, ruim, gaiolas_de_solucao(SOLUCAO_4, pares_horizontais(4))))


if __name__ == "__main__":
    unittest.main()
