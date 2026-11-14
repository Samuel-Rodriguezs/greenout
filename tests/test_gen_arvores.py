import random
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_arvores as g
from gen_grafos import componentes_conexas


class TestGenArvores(unittest.TestCase):
    def test_prufer_decodifica_exemplo_conhecido(self):
        # código clássico [3, 3, 3, 4] para n=6
        e = g.prufer_para_arestas([3, 3, 3, 4], 6)
        self.assertEqual(sorted(e), [(0, 3), (1, 3), (2, 3), (3, 4), (4, 5)])

    def test_arvore_uniforme_e_arvore(self):
        for n in (2, 3, 10, 50):
            for seed in range(20):
                e = g.arvore_uniforme(random.Random(seed), n)
                self.assertEqual(len(e), n - 1)
                self.assertEqual(componentes_conexas(n, e), 1)  # n-1 arestas + conexo = árvore

    def test_uniformidade_n4(self):
        # 4^2 = 16 árvores rotuladas, cada uma com probabilidade 1/16
        rng = random.Random(1)
        c = Counter(tuple(sorted(g.arvore_uniforme(rng, 4))) for _ in range(16000))
        self.assertEqual(len(c), 16)
        for v in c.values():
            self.assertAlmostEqual(v, 1000, delta=150)

    def test_determinismo(self):
        self.assertEqual(g.arvore_uniforme(random.Random(2), 30), g.arvore_uniforme(random.Random(2), 30))

    def test_prufer_invalido(self):
        with self.assertRaises(ValueError):
            g.prufer_para_arestas([9], 3)
        with self.assertRaises(ValueError):
            g.codigo_prufer(random.Random(0), 1)

    def test_bst_em_ordem_e_altura(self):
        n = 1024
        raiz = g.bst_aleatoria(random.Random(3), n)
        self.assertEqual(g.em_ordem(raiz), list(range(n)))
        self.assertLess(g.altura(raiz), 4 * 10)  # ~ 2.99 log2(n) no pior caso típico
        self.assertGreaterEqual(g.altura(raiz), 11)  # >= ceil(log2(n+1))

    def test_bst_vazia_e_unitaria(self):
        self.assertIsNone(g.bst_aleatoria(random.Random(0), 0))
        self.assertEqual(g.altura(None), 0)
        self.assertEqual(g.altura(g.bst_aleatoria(random.Random(0), 1)), 1)

    def test_inserir_duplicata_ignorada(self):
        r = g.inserir(None, 5)
        g.inserir(r, 5)
        self.assertEqual(g.em_ordem(r), [5])


if __name__ == "__main__":
    unittest.main()
