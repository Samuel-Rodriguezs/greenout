import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_cave import componentes, gerar, passo


class TestCave(unittest.TestCase):
    def test_deterministico_por_seed(self):
        self.assertEqual(gerar(40, 25, 7), gerar(40, 25, 7))
        self.assertNotEqual(gerar(40, 25, 7), gerar(40, 25, 8))

    def test_dimensoes_e_borda(self):
        g = gerar(30, 20, 1)
        self.assertEqual((len(g), len(g[0])), (20, 30))
        self.assertTrue(all(g[0][x] == g[-1][x] == 1 for x in range(30)))
        self.assertTrue(all(g[y][0] == g[y][-1] == 1 for y in range(20)))

    def test_uma_unica_regiao(self):
        g = gerar(50, 30, 3)
        self.assertEqual(len(componentes(g)), 1)
        self.assertGreater(len(componentes(g)[0]), 100)

    def test_sem_manter_maior_pode_ter_varias(self):
        g = gerar(60, 40, 5, prob_parede=0.5, manter_maior=False)
        self.assertGreaterEqual(len(componentes(g)), 1)

    def test_passo_regra(self):
        # chão isolado cercado por paredes vira parede; parede solitária num vazio some
        g = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
        self.assertEqual(passo(g)[1][1], 1)
        g = [[0] * 5 for _ in range(5)]
        g[2][2] = 1
        # fora do mapa conta como parede, mas o miolo tem 1 vizinho parede
        self.assertEqual(passo(g)[2][2], 0)

    def test_prob_extremas(self):
        self.assertEqual(componentes(gerar(10, 10, 1, prob_parede=1.0)), [])
        g = gerar(10, 10, 1, prob_parede=0.0, iteracoes=0)
        self.assertEqual(sum(map(sum, g)), 36)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            gerar(2, 10, 0)
        with self.assertRaises(ValueError):
            gerar(10, 10, 0, prob_parede=1.5)


if __name__ == "__main__":
    unittest.main()
