import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_dungeon_walk import gerar


class TestWalk(unittest.TestCase):
    def test_deterministico(self):
        self.assertEqual(gerar(30, 20, 5), gerar(30, 20, 5))
        self.assertNotEqual(gerar(30, 20, 5)[0], gerar(30, 20, 6)[0])

    def test_atinge_fracao_alvo(self):
        g, ordem = gerar(30, 20, 2, fracao_chao=0.4)
        self.assertEqual(sum(1 for r in g for c in r if c == 0), len(ordem))
        self.assertEqual(len(ordem), round(28 * 18 * 0.4))

    def test_borda_intacta(self):
        g, _ = gerar(30, 20, 3, fracao_chao=0.9)
        self.assertTrue(all(g[0][x] == g[19][x] == 1 for x in range(30)))
        self.assertTrue(all(g[y][0] == g[y][29] == 1 for y in range(20)))

    def test_conexo_cada_celula_adjacente_a_anterior(self):
        _, ordem = gerar(30, 20, 4)
        vistos = {ordem[0]}
        for x, y in ordem[1:]:
            vizinhas = {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}
            self.assertTrue(vizinhas & vistos)
            vistos.add((x, y))

    def test_inicio_no_centro(self):
        _, ordem = gerar(31, 21, 0)
        self.assertEqual(ordem[0], (15, 10))

    def test_persistencia_gera_tuneis_mais_longos(self):
        def retas(persist):
            _, o = gerar(60, 40, 1, fracao_chao=0.15, persistencia=persist)
            return sum(1 for a, b, c in zip(o, o[1:], o[2:])
                       if (b[0] - a[0], b[1] - a[1]) == (c[0] - b[0], c[1] - b[1]))
        self.assertGreater(retas(0.9), retas(0.0))

    def test_max_passos_limita(self):
        _, ordem = gerar(30, 20, 1, fracao_chao=1.0, max_passos=10)
        self.assertLessEqual(len(ordem), 11)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            gerar(4, 20, 0)
        with self.assertRaises(ValueError):
            gerar(20, 20, 0, fracao_chao=0)
        with self.assertRaises(ValueError):
            gerar(20, 20, 0, persistencia=2)


if __name__ == "__main__":
    unittest.main()
