import random
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_amostragem as g


class TestGenAmostragem(unittest.TestCase):
    def test_com_reposicao_proporcional(self):
        itens, pesos = ["a", "b", "c"], [1, 2, 7]
        c = Counter(g.com_reposicao(random.Random(1), itens, pesos, 20000))
        self.assertAlmostEqual(c["a"] / 20000, 0.1, delta=0.015)
        self.assertAlmostEqual(c["b"] / 20000, 0.2, delta=0.015)
        self.assertAlmostEqual(c["c"] / 20000, 0.7, delta=0.015)

    def test_peso_zero_nunca_sorteado(self):
        r = g.com_reposicao(random.Random(2), ["x", "y", "z"], [0, 1, 0], 500)
        self.assertEqual(set(r), {"y"})

    def test_sem_reposicao_distintos_e_tamanho(self):
        for seed in range(30):
            r = g.sem_reposicao(random.Random(seed), list(range(20)), [i + 1 for i in range(20)], 7)
            self.assertEqual(len(r), 7)
            self.assertEqual(len(set(r)), 7)

    def test_sem_reposicao_favorece_pesos_altos(self):
        itens = ["leve", "pesado"]
        pesos = [1, 9]
        primeiro = Counter(g.sem_reposicao(random.Random(s), itens, pesos, 1)[0] for s in range(4000))
        self.assertAlmostEqual(primeiro["pesado"] / 4000, 0.9, delta=0.02)

    def test_sem_reposicao_k_total_e_erros(self):
        r = g.sem_reposicao(random.Random(3), [1, 2, 3], [1, 1, 1], 3)
        self.assertEqual(sorted(r), [1, 2, 3])
        with self.assertRaises(ValueError):
            g.sem_reposicao(random.Random(3), [1, 2, 3], [1, 0, 1], 3)
        with self.assertRaises(ValueError):
            g.com_reposicao(random.Random(3), [1, 2], [1], 1)
        with self.assertRaises(ValueError):
            g.com_reposicao(random.Random(3), [1, 2], [0, 0], 1)
        with self.assertRaises(ValueError):
            g.com_reposicao(random.Random(3), [1, 2], [-1, 2], 1)

    def test_reservatorio_tamanho_e_uniformidade(self):
        self.assertEqual(g.reservatorio(random.Random(0), range(3), 10), [0, 1, 2])
        self.assertEqual(g.reservatorio(random.Random(0), range(10), 0), [])
        c = Counter()
        for s in range(3000):
            c.update(g.reservatorio(random.Random(s), range(10), 3))
        for i in range(10):
            self.assertAlmostEqual(c[i] / 3000, 0.3, delta=0.04)
        with self.assertRaises(ValueError):
            g.reservatorio(random.Random(0), [], -1)

    def test_determinismo(self):
        a = g.sem_reposicao(random.Random(9), list("abcdef"), [1, 2, 3, 4, 5, 6], 4)
        self.assertEqual(a, g.sem_reposicao(random.Random(9), list("abcdef"), [1, 2, 3, 4, 5, 6], 4))


if __name__ == "__main__":
    unittest.main()
