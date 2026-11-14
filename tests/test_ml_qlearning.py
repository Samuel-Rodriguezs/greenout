import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_qlearning import Grade, politica_gulosa, seguir_politica, treinar

MAPA = [
    "S..#",
    ".#.X",
    "...G",
]


class TestQLearning(unittest.TestCase):
    def setUp(self):
        self.g = Grade(MAPA)

    def test_dinamica_do_ambiente(self):
        self.assertEqual(self.g.passo((0, 0), "cima"), ((0, 0), -1.0, False))
        self.assertEqual(self.g.passo((0, 2), "direita"), ((0, 2), -1.0, False))  # parede
        self.assertEqual(self.g.passo((2, 2), "direita"), ((2, 3), 10.0, True))
        self.assertEqual(self.g.passo((1, 2), "direita"), ((1, 3), -10.0, True))

    def test_aprende_caminho_otimo(self):
        Q = treinar(self.g, episodios=400, seed=1)
        caminho, total = seguir_politica(self.g, Q)
        self.assertEqual(caminho[-1], self.g.objetivo)
        # menor caminho: 5 passos (4 de custo -1 e o último +10)
        self.assertEqual(len(caminho) - 1, 5)
        self.assertEqual(total, 6.0)
        self.assertNotIn((1, 3), caminho)

    def test_deterministico(self):
        self.assertEqual(treinar(self.g, seed=3), treinar(self.g, seed=3))

    def test_sem_treino_nao_chega(self):
        Q = treinar(self.g, episodios=0)
        self.assertEqual(Q, {})
        self.assertEqual(politica_gulosa(Q, (0, 0)), "cima")

    def test_valores_q_perto_do_objetivo_altos(self):
        Q = treinar(self.g, episodios=400, seed=2)
        self.assertGreater(Q[(2, 2)]["direita"], 8.0)
        self.assertLess(Q[(2, 2)]["direita"], 10.01)

    def test_mapa_sem_objetivo(self):
        with self.assertRaises(ValueError):
            Grade(["S.."])


if __name__ == "__main__":
    unittest.main()
