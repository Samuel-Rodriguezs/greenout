import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_conecta4 import Conecta4


class TestConecta4(unittest.TestCase):
    def test_gravidade_e_alternancia(self):
        j = Conecta4()
        self.assertEqual(j.soltar(3), 5)
        self.assertEqual(j.soltar(3), 4)
        self.assertEqual(j.grade[5][3], 1)
        self.assertEqual(j.grade[4][3], 2)

    def test_vitoria_horizontal(self):
        j = Conecta4()
        for c in (0, 0, 1, 1, 2, 2, 3):
            j.soltar(c)
        self.assertEqual(j.vencedor, 1)
        with self.assertRaises(RuntimeError):
            j.soltar(4)

    def test_vitoria_vertical_e_diagonal(self):
        j = Conecta4()
        for c in (0, 1, 0, 1, 0, 1, 0):
            j.soltar(c)
        self.assertEqual(j.vencedor, 1)
        d = Conecta4()
        for c in (0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3):
            d.soltar(c)
        self.assertEqual(d.vencedor, 1)

    def test_coluna_cheia(self):
        j = Conecta4()
        for _ in range(6):
            j.soltar(0)
        with self.assertRaises(ValueError):
            j.soltar(0)
        with self.assertRaises(ValueError):
            j.soltar(9)

    def test_ia_vence_quando_pode(self):
        j = Conecta4()
        for c in (0, 6, 1, 6, 2, 5):
            j.soltar(c)
        self.assertEqual(j.melhor_jogada(3, random.Random(1)), 3)

    def test_ia_bloqueia(self):
        j = Conecta4()
        for c in (0, 1, 0, 2, 5, 3):
            j.soltar(c)
        # jogador 2 tem 1,2,3 na base; jogador 1 precisa bloquear em 0 ou 4
        self.assertIn(j.melhor_jogada(4, random.Random(1)), (0, 4))
        self.assertEqual(j.vez, 1)

    def test_ia_nao_altera_estado(self):
        j = Conecta4()
        j.soltar(3)
        antes = [r[:] for r in j.grade]
        j.melhor_jogada(3, random.Random(2))
        self.assertEqual(j.grade, antes)
        self.assertEqual(j.vez, 2)

    def test_empate(self):
        j = Conecta4()
        j.grade = [[1 + (l // 2 + c) % 2 for c in range(7)] for l in range(6)]
        self.assertEqual(j.colunas_validas(), [])
        self.assertTrue(j.empate)
        self.assertTrue(j.terminou)


if __name__ == "__main__":
    unittest.main()
