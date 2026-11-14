import random
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_embaralhar as g


class TestGenEmbaralhar(unittest.TestCase):
    def test_e_permutacao_e_nao_altera_entrada(self):
        orig = list(range(30))
        copia = list(orig)
        r = g.fisher_yates(random.Random(1), orig)
        self.assertEqual(orig, copia)
        self.assertEqual(sorted(r), orig)
        self.assertNotEqual(r, orig)

    def test_uniformidade_n3(self):
        rng = random.Random(2)
        c = Counter(tuple(g.fisher_yates(rng, [0, 1, 2])) for _ in range(12000))
        self.assertEqual(len(c), 6)
        for v in c.values():
            self.assertAlmostEqual(v, 2000, delta=200)

    def test_determinismo(self):
        self.assertEqual(g.permutacao_aleatoria(random.Random(3), 50), g.permutacao_aleatoria(random.Random(3), 50))

    def test_vazio_e_unitario(self):
        self.assertEqual(g.fisher_yates(random.Random(0), []), [])
        self.assertEqual(g.fisher_yates(random.Random(0), "a"), ["a"])

    def test_desarranjo(self):
        for n in (0, 2, 3, 10):
            p = g.desarranjo(random.Random(n), n)
            self.assertEqual(sorted(p), list(range(n)))
            self.assertTrue(all(p[i] != i for i in range(n)))
        with self.assertRaises(ValueError):
            g.desarranjo(random.Random(0), 1)

    def test_particao_balanceada(self):
        itens = list(range(23))
        gs = g.particionar_em_k(random.Random(4), itens, 5)
        self.assertEqual([len(x) for x in gs], [5, 5, 5, 4, 4])
        self.assertEqual(sorted(x for grupo in gs for x in grupo), itens)
        with self.assertRaises(ValueError):
            g.particionar_em_k(random.Random(4), itens, 0)

    def test_particao_mais_grupos_que_itens(self):
        gs = g.particionar_em_k(random.Random(0), [1, 2], 4)
        self.assertEqual([len(x) for x in gs], [1, 1, 0, 0])

    def test_treino_teste(self):
        tr, te = g.dividir_treino_teste(random.Random(5), range(100), 0.2)
        self.assertEqual((len(tr), len(te)), (80, 20))
        self.assertEqual(set(tr) & set(te), set())
        self.assertEqual(sorted(tr + te), list(range(100)))
        with self.assertRaises(ValueError):
            g.dividir_treino_teste(random.Random(5), [1], 1.5)

    def test_dobras_cruzadas(self):
        dobras = g.dobras_cruzadas(random.Random(6), range(50), 5)
        validacoes = [x for _, v in dobras for x in v]
        self.assertEqual(sorted(validacoes), list(range(50)))
        for tr, v in dobras:
            self.assertEqual(set(tr) & set(v), set())
            self.assertEqual(len(tr) + len(v), 50)


if __name__ == "__main__":
    unittest.main()
