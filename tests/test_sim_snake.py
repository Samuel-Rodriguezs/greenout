import random
import sys
import unittest
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_snake import Snake


class TestSnake(unittest.TestCase):
    def test_movimento(self):
        s = Snake(rng=random.Random(1))
        s.comida = (0, 0)
        cabeca = s.corpo[0]
        self.assertTrue(s.passo())
        self.assertEqual(s.corpo[0], (cabeca[0], cabeca[1] + 1))
        self.assertEqual(len(s.corpo), 3)

    def test_comer_cresce(self):
        s = Snake(rng=random.Random(1))
        l, c = s.corpo[0]
        s.comida = (l, c + 1)
        s.passo()
        self.assertEqual(len(s.corpo), 4)
        self.assertEqual(s.pontos, 1)
        self.assertNotIn(s.comida, s.corpo)

    def test_parede(self):
        s = Snake(5, 5, random.Random(1))
        s.comida = (0, 0)
        for _ in range(10):
            s.passo()
        self.assertFalse(s.vivo)
        self.assertFalse(s.passo())

    def test_nao_inverte(self):
        s = Snake(rng=random.Random(1))
        s.virar("esquerda")
        self.assertEqual(s.direcao, "direita")
        s.virar("cima")
        self.assertEqual(s.direcao, "cima")

    def test_colisao_propria(self):
        s = Snake(10, 10, random.Random(1))
        s.corpo = deque([(5, 5), (5, 6), (6, 6), (6, 5), (6, 4)])
        s.direcao = "baixo"
        s.comida = (0, 0)
        self.assertFalse(s.passo())
        self.assertFalse(s.vivo)

    def test_comida_deterministica(self):
        self.assertEqual(Snake(rng=random.Random(9)).comida, Snake(rng=random.Random(9)).comida)


if __name__ == "__main__":
    unittest.main()
