import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_g2048 import Jogo2048, deslizar_linha


class Test2048(unittest.TestCase):
    def test_deslizar(self):
        self.assertEqual(deslizar_linha([2, 2, 2, 2]), ([4, 4, 0, 0], 8))
        self.assertEqual(deslizar_linha([0, 2, 0, 2]), ([4, 0, 0, 0], 4))
        self.assertEqual(deslizar_linha([4, 2, 2, 0]), ([4, 4, 0, 0], 4))
        self.assertEqual(deslizar_linha([2, 4, 8, 16]), ([2, 4, 8, 16], 0))

    def test_inicio_deterministico(self):
        a = Jogo2048(rng=random.Random(5)).grade
        b = Jogo2048(rng=random.Random(5)).grade
        self.assertEqual(a, b)
        self.assertEqual(sum(1 for r in a for v in r if v), 2)

    def test_mover_direcoes(self):
        j = Jogo2048(rng=random.Random(1))
        j.grade = [[2, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]]
        self.assertEqual(j._aplicar("esquerda")[0][0], [4, 0, 0, 0])
        self.assertEqual(j._aplicar("direita")[0][0], [0, 0, 0, 4])
        self.assertEqual(j._aplicar("cima")[0][0][0], 4)
        self.assertEqual(j._aplicar("baixo")[0][3][0], 4)

    def test_mover_adiciona_peca_e_pontos(self):
        j = Jogo2048(rng=random.Random(1))
        j.grade = [[2, 2, 0, 0]] + [[0] * 4 for _ in range(3)]
        self.assertTrue(j.mover("esquerda"))
        self.assertEqual(j.pontos, 4)
        self.assertEqual(sum(1 for r in j.grade for v in r if v), 2)

    def test_movimento_invalido_e_fim(self):
        j = Jogo2048(rng=random.Random(1))
        j.grade = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
        self.assertTrue(j.fim)
        self.assertFalse(j.mover("esquerda"))
        with self.assertRaises(ValueError):
            j.mover("diagonal")

    def test_vitoria(self):
        j = Jogo2048(rng=random.Random(1))
        j.grade[0][0] = 2048
        self.assertTrue(j.venceu)


if __name__ == "__main__":
    unittest.main()
